import os.path
import re
from contextlib import contextmanager
from decimal import Decimal

import bleach
import pyexcel
import pymssql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dv.models import (
    Allocation, BilateralInitiative, Indicator, OrganisationRole, Organisation, PrioritySector,
    Programme, ProgrammeAllocation, ProgrammeArea, Project, ProjectAllocation, State,
)
from dv.lib.utils import FM_EEA, FM_NORWAY, FM_REVERSED_DICT


GRANT_SHORT_NAME_TO_FM = {
    'EEA': 'EEA',
    'Norway': 'NOR',
}
GRANT_CODE_TO_FM = {
    'EEA FM': 'EEA',
    'N FM': 'NOR',
}
COMMENTS_PATTERN = re.compile(r'&lt;!--.*--&gt;')


def sanitize_html(text):
    cleaned_text = bleach.clean(text or '', strip=True, strip_comments=True)
    return COMMENTS_PATTERN.sub('', cleaned_text)


@contextmanager
def db_cursor():
    conn = pymssql.connect(
        settings.MSSQL_SERVER,
        settings.MSSQL_USERNAME,
        settings.MSSQL_PASSWORD,
        settings.MSSQL_DATABASE
    )
    cursor = conn.cursor(as_dict=True)
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()


class Command(BaseCommand):
    help = 'Import data for both periods'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period_id',
            type=int,
            choices=(2, 3),
            help='Run import for specific period; options: 2 (2009-2014); 3 (2014-2021).',
        )
        parser.add_argument(
            '--directory',
            help='A directory containing spreadsheet (xlsx) files. Required for period 2.',
        )

    def handle(self, *args, **options):
        funding_period = options.get('period_id')
        directory = options.get('directory')

        if not funding_period or funding_period == 2:
            if directory:
                self._import_2009_2014(directory)
            else:
                self.stdout.write(self.style.ERROR('A directory containing xlsx files must '
                                                   'be provided for 2009-2014 import.'))

        if not funding_period or funding_period == 3:
            self._import_2014_2021()

    def _import_2009_2014(self, directory_path):
        """Import data from Excel files for period 2009-2014"""
        self.stdout.write('Running import for 2009-2014.')

        EXCEL_FILES = (
            'BeneficiaryState',
            'BeneficiaryStatePrioritySector',
            'Programme',
            'ProgrammeOutcome',
            'ProgrammeIndicators',
            'Project',
            'ProjectThemes',
            'Organisation',
            'OrganisationRoles',
        )

        if not os.path.exists(directory_path):
            raise CommandError(f'Cannot open directory {directory_path}.')

        files = [
            f for f in os.listdir(directory_path)
            if (
                os.path.isfile(os.path.join(directory_path, f)) and
                f.endswith('.xlsx') and
                f[:-5].lower() in (name.lower() for name in EXCEL_FILES)
            )
        ]
        if not files:
            raise CommandError(f'Directory {directory_path} is empty.')

        existing_books = [file.split('.')[0].lower() for file in files]
        for file in EXCEL_FILES:
            if file.lower() not in existing_books:
                raise CommandError(f'Workbook {file} is missing.')

        sheets = {}
        for file in files:
            self.stdout.write(f'Loading {file}.')
            file_path = os.path.join(directory_path, file)
            book = pyexcel.get_book(file_name=file_path)
            name = file.split('.')[0]
            name = next(f for f in EXCEL_FILES if f.lower() == name.lower())
            try:
                sheets[name] = book[name]
            except KeyError:
                # if book name different than file name just load the first one
                if len(book.sheet_names()) == 0:
                    raise CommandError(f'No worksheets found in {name}.')
                sheet_names = ', '.join(book.sheet_names())
                self.stdout.write(f'Assuming first worksheet of {sheet_names}.')
                sheets[name] = book.sheet_by_index(0)

        for sheet in sheets.values():
            sheet.name_columns_by_row(0)

        def _convert_nulls(record):
            for k, v in record.items():
                if v in ('NULL', 'None', ''):
                    record[k] = None
                elif hasattr(record[k], 'strip'):
                    record[k] = record[k].strip()

        FUNDING_PERIOD = 2  # 2009-2014

        # GR country code used in 2009-2014; for 2014-2021 we use EL
        states = {state.name: state.pk for state in State.objects.exclude(code='EL')}

        sheet = sheets['BeneficiaryStatePrioritySector']
        priority_sectors = set()
        programme_areas = dict()
        pa_to_ps = dict()

        ps_count = 0
        for record in sheet.records:
            _convert_nulls(record)

            if record['PSCode'] not in priority_sectors:
                priority_sector, created = PrioritySector.objects.get_or_create(
                    code=record['PSCode'],
                    defaults={'name': record['PrioritySector']},
                )
                if created:
                    ps_count += 1
                priority_sectors.add(priority_sector.code)

            if record['PACode'] not in programme_areas:
                programme_area = ProgrammeArea.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=record['PACode'],
                    name=record['ProgrammeArea'],
                    short_name=record['ProgrammeAreaShortName'],
                    order=record['SortOrder'],
                    priority_sector_id=record['PSCode'],
                    objective=record['ProgrammeAreaObjective'] or '',
                )
                programme_areas[programme_area.code] = programme_area.id
                pa_to_ps[programme_area.code] = programme_area.priority_sector_id

            Allocation.objects.create(
                funding_period=FUNDING_PERIOD,
                financial_mechanism=FM_REVERSED_DICT[record['GrantName']],
                state_id=states[record['BeneficiaryState']],
                programme_area_id=programme_areas[record['PACode']],
                gross_allocation=record['GrossAllocation'],
                net_allocation=record['NetAllocation'],
            )

        self.stdout.write(self.style.SUCCESS(f'Imported {ps_count} PrioritySector objects.'))

        pa_count = ProgrammeArea.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {pa_count} ProgrammeArea objects.'))

        a_count = Allocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {a_count} Allocation objects.'))

        sheet = sheets['Programme']
        for record in sheet.records:
            _convert_nulls(record)

            programme = Programme.objects.create(
                funding_period=FUNDING_PERIOD,
                code=record['ProgrammeCode'],
                name=record['Programme'],
                summary=sanitize_html(record['ProgrammeSummary']),
                status=record['ProgrammeStatus'] or '',
                allocation_eea=record['AllocatedProgrammeGrantEEA'] or 0,
                allocation_norway=record['AllocatedProgrammeGrantNorway'] or 0,
                co_financing=record['ProgrammeCoFinancing'],
                url=record['UrlProgrammePage'] or '',
                is_tap=record['IsTAProgramme'],
            )
            programme_area_codes = [
                programme_areas[pa.split('-')[0].strip()]
                for pa in record['PAListWithShortName'].split(',')
            ]
            programme.programme_areas.add(*programme_area_codes)
            programme.states.add(states[record['BeneficiaryState']])

        p_count = Programme.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {p_count} Programme objects.'))

        sheet = sheets['ProgrammeOutcome']
        for record in sheet.records:
            _convert_nulls(record)

            # PS13 and PS14 are split in two; get full PS code from PA
            # PS13a & PS14a - Technical Assistance
            # PS13b & PS14b - Fund for bilateral assistance
            if record['PSCode'] in ('PS13', 'PS14'):
                record['PSCode'] = pa_to_ps[record['PACode']]
            ProgrammeAllocation.objects.create(
                funding_period=FUNDING_PERIOD,
                financial_mechanism=GRANT_CODE_TO_FM[record['FMCode']],
                state_id=states[record['BeneficiaryState']],
                programme_area_id=programme_areas[record['PACode']],
                priority_sector_id=record['PSCode'],
                programme_id=record['ProgrammeCode'],
                allocation=record['GrantAmount'],
            )

        pa_count = ProgrammeAllocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {pa_count} ProgrammeAllocation objects.'))

    def _import_2014_2021(self):
        """Import data from grACE db for period 2014-2021"""
        self.stdout.write('Running import for 2014-2021.')

        FUNDING_PERIOD = 3  # 2014-2021

        # GR country code used in 2009-2014; for 2014-2021 we use EL
        states = {state.name: state for state in State.objects.exclude(code='GR')}

        programme_area_query = 'SELECT * FROM fmo.TR_RDPProgrammeArea'
        ps_count = 0
        with db_cursor() as cursor:
            cursor.execute(programme_area_query)
            programme_areas = {}
            priority_sectors = {}
            for row in cursor.fetchall():
                priority_sector, created = PrioritySector.objects.get_or_create(
                    code=row['PSCode'],
                    defaults={'name': row['PrioritySector']},
                )
                if created:
                    ps_count += 1
                priority_sectors[priority_sector.code] = priority_sector
                programme_area = ProgrammeArea.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['PACode'],
                    name=row['ProgrammeArea'],
                    short_name=row['ProgrammeAreaShortName'],
                    order=row['idPA'],
                    priority_sector=priority_sector,
                    objective=row['Objective'] or '',
                )
                programme_areas[programme_area.code] = programme_area

        self.stdout.write(self.style.SUCCESS(f'Imported {ps_count} PrioritySector objects.'))

        pa_count = ProgrammeArea.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {pa_count} ProgrammeArea objects.'))

        allocation_query = 'SELECT * FROM fmo.TR_RDPCountryProgrammeArea'
        with db_cursor() as cursor:
            cursor.execute(allocation_query)
            for row in cursor.fetchall():
                # Exclude allocations for Hungary in PAs different from HHHH
                # Will eventually be fixed in the data, this is temporary
                if row['Country'] == 'Hungary' and row['PACode'] != 'HHHH':
                    continue
                Allocation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    financial_mechanism=GRANT_SHORT_NAME_TO_FM[row['GrantShortName']],
                    state=states.get(row['Country']),
                    programme_area=programme_areas.get(row['PACode']),
                    gross_allocation=row['GrossAllocation'],
                    net_allocation=row['NetAllocation'],
                    thematic=row['Thematic'] or '',
                )

        a_count = Allocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {a_count} Allocation objects.'))

        # Exclude programmes from Hungary
        programme_query = "SELECT * FROM fmo.TR_RDPProgramme WHERE Country != 'Hungary'"
        with db_cursor() as cursor:
            cursor.execute(programme_query)
            programmes = {}
            for row in cursor.fetchall():
                programme = Programme.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['ProgrammeShortName'],
                    name=row['Programme'],
                    summary=sanitize_html(row['ProgrammeSummary']),
                    status=row['ProgrammeStatus'] or '',
                    allocation_eea=row['ProgrammeGrantEEA'] or 0,
                    allocation_norway=row['ProgrammeGrantNorway'] or 0,
                    co_financing=row['ProgrammeCoFinancing'],
                    is_tap=row['IsTAProgramme'],
                    is_bfp=row['IsBFProgramme'],
                )
                programmes[programme.code] = programme

                self._add_m2m_entries(programme, row, 'ProgrammeAreaList', 'programme_areas',
                                      'ProgrammeArea', programme_areas)

                # For the moment, all programmes have one or zero (NULL/Non-country specific) states
                self._add_m2m_entries(programme, row, 'Country', 'states',
                                      'State', states)

        p_count = Allocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {p_count} Programme objects.'))

        programme_allocation_query = 'SELECT * FROM fmo.TR_RDPProgrammeBudgetHeading'
        with db_cursor() as cursor:
            cursor.execute(programme_allocation_query)
            for row in cursor.fetchall():
                ProgrammeAllocation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    financial_mechanism=GRANT_SHORT_NAME_TO_FM[row['GrantShortName']],
                    state=states[row['Country']],
                    programme_area=programme_areas.get(row['PACode']),
                    priority_sector=priority_sectors.get(row['PSCode']),
                    programme=programmes.get(row['ProgrammeShortName']),
                    allocation=row['BudgetHeadingGrant'],
                    thematic=row['Thematic'] or '',
                    sdg_no=row['SDGno'],
                )

        pa_count = ProgrammeAllocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {pa_count} ProgrammeAllocation objects.'))

        project_query = 'SELECT * FROM fmo.TR_RDPProject'
        with db_cursor() as cursor:
            cursor.execute(project_query)
            projects = {}
            for row in cursor.fetchall():
                project = Project.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['ProjectCode'],
                    name=row['Project'],
                    status=row['ProjectContractStatus'],
                    state=states.get(row['Country']),
                    programme=programmes.get(row['ProgrammeShortName']),
                    nuts_id=row['ProjectLocation'] or None,
                    url=row['ProjectURL'],
                    allocation=row['ProjectGrant'],
                    is_eea=bool(row['IdFinancialMechanismEEA']),
                    is_norway=bool(row['IdFinancialMechanismNorway']),
                    has_ended=row['Hasended'],
                    is_dpp=row['isdpp'],
                    is_positive_fx=bool(row['ResultPositiveEffects']),
                    is_improved_knowledge=bool(row['ResultsImprovedKnowledge']),
                    is_continued_coop=bool(row['CooperationContinue']),
                    initial_description=sanitize_html(row['ProjectInitialDescriptionHtml']),
                    results_description=sanitize_html(row['ProjectResultsDescriptionHtml']),
                )
                projects[project.code] = project

                self._add_m2m_entries(project, row, 'ProgrammeAreaCodesList', 'programme_areas',
                                      'ProgrammeArea', programme_areas)
                self._add_m2m_entries(project, row, 'PrioritySectorCodesList', 'priority_sectors',
                                      'PrioritySector', priority_sectors)

        p_count = Project.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {p_count} Project objects.'))

        for project in Project.objects.prefetch_related('programme_areas', 'priority_sectors'):
            if project.is_eea and project.is_norway:
                ProjectAllocation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    financial_mechanism=FM_EEA,
                    state_id=project.state_id,
                    programme_area=project.programme_areas.get(),
                    priority_sector=project.priority_sectors.get(),
                    project=project,
                    allocation=Decimal('0.5525') * project.allocation,
                )
                ProjectAllocation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    financial_mechanism=FM_NORWAY,
                    state=project.state,
                    programme_area=project.programme_areas.get(),
                    priority_sector=project.priority_sectors.get(),
                    project=project,
                    allocation=Decimal('0.4475') * project.allocation,
                )
            else:
                for idx, pa, ps in zip(range(3), project.programme_areas.all(), project.priority_sectors.all()):
                    ProjectAllocation.objects.create(
                        funding_period=FUNDING_PERIOD,
                        financial_mechanism=FM_EEA if project.is_eea else FM_NORWAY,
                        state_id=project.state_id,
                        programme_area=pa,
                        priority_sector=ps,
                        project=project,
                        allocation=project.allocation if idx == 0 else 0,
                    )

        pa_count = ProjectAllocation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {pa_count} ProjectAllocation objects.'))

        indicator_query = 'SELECT * FROM fmo.TR_RDPIndicators'
        with db_cursor() as cursor:
            cursor.execute(indicator_query)
            for row in cursor.fetchall():
                Indicator.objects.create(
                    funding_period=FUNDING_PERIOD,
                    programme=programmes.get(row['ProgrammeShortName']),
                    programme_area=programme_areas.get(row['PACode']),
                    state=states.get(row['Country']),
                    indicator=row['CoreCommonIndicator'],
                    outcome=row['Outcome'],
                    header=row['Header'],
                    unit_of_measurement=row['UnitOfMeasurement'],
                    achievement_eea=row['Achievement_EEA'] or 0,
                    achievement_norway=row['Achievement_Norway'] or 0,
                    order=row['CoreIndicatorCode'],
                    is_core=bool(row['IsCore']),
                    is_common=bool(row['IsCommon']),
                    thematic=row['Thematic'] or '',
                    sdg_no=row['SDGno'],
                )

        i_count = Indicator.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {i_count} Indicator objects.'))

        organisation_query = '''
            SELECT DISTINCT
                IdOrganisation,
                Organisation,
                CountryOrganisation,
                City,
                OrganisationClassificationSector,
                OrganisationClassification
            FROM fmo.TR_RDPOrganisationRole
        '''
        with db_cursor() as cursor:
            cursor.execute(organisation_query)
            organisations = {}
            for row in cursor.fetchall():
                organisation = Organisation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['IdOrganisation'],
                    name=row['Organisation'],
                    city=row['City'],
                    country=row['CountryOrganisation'],
                    category=row['OrganisationClassificationSector'],
                    subcategory=row['OrganisationClassification'],
                )
                organisations[organisation.code] = organisation.id
        o_count = Organisation.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {o_count} Organisation objects.'))

        organisation_role_query = 'SELECT * FROM fmo.TR_RDPOrganisationRole'
        with db_cursor() as cursor:
            cursor.execute(organisation_role_query)
            for row in cursor.fetchall():
                OrganisationRole.objects.create(
                    funding_period=FUNDING_PERIOD,
                    organisation_id=organisations[row['IdOrganisation']],
                    nuts_id=row['NUTSCode'] or None,
                    role_code=row['OrganisationRoleCode'],
                    role_name=row['OrganisationRole'],
                    programme=programmes.get(row['ProgrammeCode']),
                    project=projects.get(row['ProjectCode']),
                    state=states.get(row['CountryRole']),
                )
        or_count = OrganisationRole.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {or_count} OrganisationRole objects.'))

        bilateral_initiative_query = 'SELECT * FROM fmo.TR_RDPBilateralinitiative'
        with db_cursor() as cursor:
            cursor.execute(bilateral_initiative_query)
            for row in cursor.fetchall():
                bilateral_initiative = BilateralInitiative.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['BICode'],
                    title=row['BITitle'],
                    url=row['BIURL'] or '',
                    grant=row['BIGrant'],
                    programme=programmes.get(row['ProgrammeShortName']),
                    project=projects.get(row['ProjectCode']),
                    state=states.get(row['Country']),
                    level=row['Level'] or '',
                    status=row['BIStatus'],
                    initial_description=sanitize_html(row['BIInitialDescriptionHtml']),
                    results_description=sanitize_html(row['BIResultsDescriptionHtml']),
                    promoter_state=states.get(row['PromoterCountry']),
                    promoter_organization=row['PromoterOrganisation'],
                )
                self._add_m2m_entries(bilateral_initiative, row, 'ProgrammeAreaCodesList', 'programme_areas',
                                      'ProgrammeArea', programme_areas)

        bi_count = BilateralInitiative.objects.filter(funding_period=FUNDING_PERIOD).count()
        self.stdout.write(self.style.SUCCESS(f'Imported {bi_count} BilateralInitiative objects.'))

    def _add_m2m_entries(self, obj, row, key, m2m_attr, m2m_attr_type, m2m_list):
        for code in (row[key] or '').split(','):
            code = code.strip()
            m2m_obj = m2m_list.get(code)
            if code and not m2m_obj:
                self.stdout.write(self.style.WARNING(f'{m2m_attr_type} {code} not found.'))
                continue
            getattr(obj, m2m_attr).add(m2m_obj)

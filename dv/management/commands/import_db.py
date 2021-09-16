import re
from contextlib import contextmanager

import bleach
import pymssql
from django.conf import settings
from django.core.management.base import BaseCommand

from dv.models import (
    Allocation, BilateralInitiative, Indicator, OrganisationRole,
    PrioritySector, Programme, ProgrammeArea, Project, State
)


FUNDING_PERIOD = 3  # 2014-2021
GRANT_SHORT_NAME_TO_FM = {
    'EEA': 'EEA',
    'Norway': 'NOR',
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
    help = 'Import data from grACE db'

    def handle(self, *args, **options):
        # GR country code used in 2009-2014; for 2014-2021 we use EL
        states = {state.name: state for state in State.objects.exclude(code='GR')}

        programme_area_query = 'SELECT * FROM fmo.TR_RDPProgrammeArea'
        with db_cursor() as cursor:
            cursor.execute(programme_area_query)
            programme_areas = {}
            priority_sectors = {}
            for row in cursor.fetchall():
                priority_sector, _ = PrioritySector.objects.get_or_create(
                    code=row['PSCode'],
                    defaults={'name': row['PrioritySector']},
                )
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

        self.stdout.write(self.style.SUCCESS(
            f'Imported {PrioritySector.objects.count()} PrioritySector objects.'))
        self.stdout.write(self.style.SUCCESS(
            f'Imported {ProgrammeArea.objects.count()} ProgrammeArea objects.'))

        allocation_query = 'SELECT * FROM fmo.TR_RDPCountryProgrammeArea'
        with db_cursor() as cursor:
            cursor.execute(allocation_query)
            for row in cursor.fetchall():
                Allocation.objects.create(
                    funding_period=FUNDING_PERIOD,
                    financial_mechanism=GRANT_SHORT_NAME_TO_FM[row['GrantShortName']],
                    state=states.get(row['Country']),
                    programme_area=programme_areas.get(row['PACode']),
                    gross_allocation=row['GrossAllocation'],
                    net_allocation=row['NetAllocation'],
                    thematic=row['Thematic'] or '',
                )

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Allocation.objects.count()} Allocation objects.'))

        programme_query = 'SELECT * FROM fmo.TR_RDPProgramme'
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

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Programme.objects.count()} Programme objects.'))

        # Remove duplicate entries
        project_query = (
            'SELECT * FROM '
            '(SELECT ROW_NUMBER() OVER(PARTITION BY ProjectCode ORDER BY ProjectCode DESC) '
            'AS RowNum, * '
            'FROM fmo.TR_RDPProject) n WHERE RowNum = 1;'
        )
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

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Project.objects.count()} Project objects.'))

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
                )

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Indicator.objects.count()} Indicator objects.'))

        organisation_role_query = 'SELECT * FROM fmo.TR_RDPOrganisationRole'
        with db_cursor() as cursor:
            cursor.execute(organisation_role_query)
            for row in cursor.fetchall():
                OrganisationRole.objects.create(
                    funding_period=FUNDING_PERIOD,
                    organisation_country=row['CountryOrganisation'],
                    organisation_name=row['Organisation'],
                    nuts_id=row['NUTSCode'] or None,
                    role_code=row['OrganisationRoleCode'],
                    role_name=row['OrganisationRole'],
                    programme=programmes.get(row['ProgrammeCode']),
                    project=projects.get(row['ProjectCode']),
                    state=states.get(row['CountryRole']),
                )
        self.stdout.write(self.style.SUCCESS(
            f'Imported {OrganisationRole.objects.count()} OrganisationRole objects.'))

        bilateral_initiative_query = 'SELECT * FROM fmo.TR_RDPBilateralinitiative'
        with db_cursor() as cursor:
            cursor.execute(bilateral_initiative_query)
            for row in cursor.fetchall():
                bilateral_initiative = BilateralInitiative.objects.create(
                    funding_period=FUNDING_PERIOD,
                    code=row['BICode'],
                    title=row['BITitle'],
                    programme=programmes.get(row['ProgrammeShortName']),
                    project=projects.get(row['ProjectCode']),
                    state=states.get(row['Country']),
                    level=row['Level'] or '',
                    status=row['BIStatus'],
                )
                self._add_m2m_entries(bilateral_initiative, row, 'ProgrammeAreaCodesList', 'programme_areas',
                                      'ProgrammeArea', programme_areas)

        self.stdout.write(self.style.SUCCESS(
            f'Imported {BilateralInitiative.objects.count()} BilateralInitiative objects.'))

    def _add_m2m_entries(self, obj, row, key, m2m_attr, m2m_attr_type, m2m_list):
        for code in (row[key] or '').split(','):
            code = code.strip()
            m2m_obj = m2m_list.get(code)
            if code and not m2m_obj:
                self.stdout.write(self.style.WARNING(f'{m2m_attr_type} {code} not found.'))
                continue
            getattr(obj, m2m_attr).add(m2m_obj)

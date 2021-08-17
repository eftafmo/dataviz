import re

import bleach
import pymssql
from django.conf import settings
from django.core.management.base import BaseCommand

from dv.models import Allocation, PrioritySector, Programme, ProgrammeArea, State


FUNDING_PERIOD = 3  # 2014-2021
GRANT_SHORT_NAME_TO_FM = {
    'EEA': 'EEA',
    'Norway': 'NOR',
}
COMMENTS_PATTERN = re.compile(r'&lt;!--.*--&gt;')

def sanitize_html(text):
    cleaned_text = bleach.clean(text or '', strip=True, strip_comments=True)
    return COMMENTS_PATTERN.sub('', cleaned_text)


class Command(BaseCommand):
    help = 'Import data from grACE db'

    def handle(self, *args, **options):
        conn = pymssql.connect(
            settings.MSSQL_SERVER,
            settings.MSSQL_USERNAME,
            settings.MSSQL_PASSWORD,
            settings.MSSQL_DATABASE
        )
        cursor = conn.cursor(as_dict=True)

        states = {state.name: state for state in State.objects.all()}

        programme_area_query = 'SELECT * FROM fmo.TR_RDPProgrammeArea'
        cursor.execute(programme_area_query)
        programme_areas = {}
        for row in cursor.fetchall():
            priority_sector, _ = PrioritySector.objects.get_or_create(
                code=row['PSCode'],
                defaults={'name': row['PrioritySector']},
            )
            programme_area = ProgrammeArea.objects.create(
                funding_period=FUNDING_PERIOD,
                code=row['PACode'],
                name=row['ProgrammeArea'],
                short_name=row['ProgrammeAreaShortName'],
                priority_sector=priority_sector,
                objective=row['Objective'] or '',
            )
            programme_areas[programme_area.code] = programme_area

        self.stdout.write(self.style.SUCCESS(
            f'Imported {PrioritySector.objects.count()} PrioritySector objects.'))
        self.stdout.write(self.style.SUCCESS(
            f'Imported {ProgrammeArea.objects.count()} ProgrammeArea objects.'))

        allocation_query = 'SELECT * FROM fmo.TR_RDPCountryProgrammeArea'
        cursor.execute(allocation_query)
        for row in cursor.fetchall():
            Allocation.objects.create(
                funding_period=FUNDING_PERIOD,
                financial_mechanism=GRANT_SHORT_NAME_TO_FM[row['GrantShortName']],
                state=states.get(row['Country']),
                programme_area=programme_areas.get(row['PACode']),
                gross_allocation=row['GrossAllocation'],
                net_allocation=row['NetAllocation'],
            )

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Allocation.objects.count()} Allocation objects.'))

        programme_query = 'SELECT * FROM fmo.TR_RDPProgramme'
        cursor.execute(programme_query)
        for row in cursor.fetchall():
            programme = Programme.objects.create(
                funding_period=FUNDING_PERIOD,
                short_name=row['ProgrammeShortName'],
                name=row['Programme'],
                summary=sanitize_html(row['ProgrammeSummary']),
                allocation_eea=row['ProgrammeGrantEEA'] or 0,
                allocation_norway=row['ProgrammeGrantNorway'] or 0,
                co_financing=row['ProgrammeCoFinancing'],
                is_tap=row['IsTAProgramme'],
                is_bfp=row['IsBFProgramme'],
            )

            for pa_code in (row['ProgrammeAreaList'] or '').split(','):
                pa_code = pa_code.strip()
                programme_area = programme_areas.get(pa_code)
                if not programme_area:
                    self.stdout.write(self.style.WARNING(f'ProgrammeArea {pa_code} not found.'))
                    continue
                programme.programme_areas.add(programme_area)

            # For the moment, all programmes have one or zero (NULL/Non-country specific) states
            for state_name in (row['Country'] or '').split(','):
                state_name = state_name.strip()
                state = states.get(state_name)
                if not state:
                    self.stdout.write(self.style.WARNING(f'State {state_name} not found.'))
                    continue
                programme.states.add(state)

        self.stdout.write(self.style.SUCCESS(
            f'Imported {Programme.objects.count()} Programme objects.'))

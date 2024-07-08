import yaml
import os.path
from django.test import TestCase
from dv.lib import utils
from dv.models import (
    GRANT_TYPE,
    State,
    PrioritySector,
    ProgrammeArea,
    Programme,
    Programme_ProgrammeArea,
    Outcome,
    ProgrammeOutcome,
    Project,
    Indicator,
    ProgrammeIndicator,
    OrganisationType,
    Organisation,
)


FIXTURES_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "import_fixture.yaml"
)


class ImportTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(FIXTURES_FILE, "r") as f:
            self.DATA = yaml.load(f)

    def _test_states(self):
        data = self.DATA[State.IMPORT_SOURCE]

        state = State.from_data(data)
        state.save()
        state = State.objects.get()

        self.assertEqual(state.code, data["Abbreviation"])
        self.assertEqual(state.name, data["BeneficaryState"])
        self.assertEqual(state.gross_allocation_eea, data["GrossAllocationEEA"])
        self.assertEqual(state.gross_allocation_norway, data["GrossAllocationNorway"])
        self.assertEqual(state.gross_allocation, data["GrossAllocation"])
        self.assertEqual(state.net_allocation_eea, data["NetAllocationEEA"])
        self.assertEqual(state.net_allocation_norway, data["NetAllocationNorway"])
        self.assertEqual(state.net_allocation, data["NetAllocation"])

    def _test_priority_sectors(self):
        data = self.DATA[PrioritySector.IMPORT_SOURCE]

        sector = PrioritySector.from_data(data)
        sector.save()
        sector = PrioritySector.objects.get()

        self.assertEqual(sector.code, data["PSCode"])
        self.assertEqual(sector.name, data["PrioritySector"])
        grant_type = utils.str_to_constant_name(data["GrantName"].split()[0])
        self.assertEqual(sector.type, getattr(GRANT_TYPE, grant_type))

    def _test_programme_areas(self):
        # programme areas are defined in the same sheet with priority sectors
        data = self.DATA[ProgrammeArea.IMPORT_SOURCE]

        area = ProgrammeArea.from_data(data)
        area.save()
        area = ProgrammeArea.objects.get()

        self.assertEqual(
            area.priority_sector,
            PrioritySector.objects.get_by_natural_key(data["PSCode"]),
        )
        self.assertEqual(area.code, data["PACode"])
        self.assertEqual(area.name, data["ProgrammeArea"])
        self.assertEqual(area.short_name, data["ProgrammeAreaShortName"])
        self.assertEqual(area.order, data["SortOrder"])
        self.assertEqual(area.objective, data["ProgrammeAreaObjective"])
        self.assertEqual(area.gross_allocation, data["GrossAllocation"])
        self.assertEqual(area.net_allocation, data["NetAllocation"])

    def _test_programmes(self):
        data = self.DATA[Programme.IMPORT_SOURCE]

        programme = Programme.from_data(data)
        programme.save()
        programme = Programme.objects.get()

        self.assertEqual(
            programme.state, State.objects.get(name=data["BeneficiaryState"])
        )
        # pa_code = data['PAListWithShortName'].split()[0]
        # self.assertEqual(programme.programme_area,
        #                  ProgrammeArea.objects.get_by_natural_key(pa_code))
        self.assertEqual(programme.code, data["ProgrammeCode"])
        self.assertEqual(programme.name, data["Programme"])
        status_attr = utils.str_to_constant_name(data["ProgrammeStatus"])
        self.assertEqual(programme.status, getattr(Programme.STATUS, status_attr))
        self.assertEqual(programme.summary, data["ProgrammeSummary"])
        self.assertEqual(programme.allocation, data["AllocatedProgrammeGrant"])
        self.assertEqual(programme.co_financing, data["ProgrammeCoFinancing"])

    def _test_programme_programme_areas(self):
        data = self.DATA[Programme_ProgrammeArea.IMPORT_SOURCE]

        p_pas = Programme_ProgrammeArea.from_data(data)
        for p_pa in p_pas:
            p_pa.save()
        p_pas = Programme_ProgrammeArea.objects.all()

        programme = Programme.objects.get_by_natural_key(data["ProgrammeCode"])
        pa_codes = [p.split(" - ")[0] for p in data["PAListWithShortName"].split(",")]
        pas = ProgrammeArea.objects.filter_by_natural_keys(pa_codes)

        # self.assertEqual(len(p_pas), len(pas))
        # for p_pa in p_pas:
        #     self.assertEqual(p_pa.programme, programme)
        #     self.assertIn(p_pa.programme_area, pas)

        # or simply: (assertItemsEqual)
        self.assertCountEqual(programme.programme_areas.all(), pas)

    def _test_outcomes(self):
        data = self.DATA[Outcome.IMPORT_SOURCE]

        outcome = Outcome.from_data(data)
        outcome.save()
        outcome = Outcome.objects.get()

        pa_code = data["PACode"]
        self.assertEqual(
            outcome.programme_area, ProgrammeArea.objects.get_by_natural_key(pa_code)
        )
        self.assertEqual(outcome.code, data["OutcomeCode"])
        self.assertEqual(outcome.name, data["Outcome"])

    def _test_programme_outcomes(self):
        data = self.DATA[ProgrammeOutcome.IMPORT_SOURCE]

        p_o = ProgrammeOutcome.from_data(data)
        p_o.save()
        p_o = ProgrammeOutcome.objects.get()

        self.assertEqual(
            p_o.programme, Programme.objects.get_by_natural_key(data["ProgrammeCode"])
        )
        self.assertEqual(
            p_o.outcome, Outcome.objects.get_by_natural_key(data["OutcomeCode"])
        )
        self.assertEqual(p_o.allocation, data["GrantAmount"])
        self.assertEqual(p_o.co_financing, data["ProgrammeCoFinancing"])

    def _test_projects(self):
        data = self.DATA[Project.IMPORT_SOURCE]

        project = Project.from_data(data)
        project.save()
        project = Project.objects.get()

        self.assertEqual(
            project.state, State.objects.get(name=data["BeneficiaryState"])
        )
        self.assertEqual(
            project.outcome, Outcome.objects.get_by_natural_key(data["OutcomeCode"])
        )
        status_attr = utils.str_to_constant_name(data["ProjectStatus"])
        self.assertEqual(project.status, getattr(Project.STATUS, status_attr))
        self.assertEqual(project.code, data["ProjectCode"])
        self.assertEqual(project.name, data["Project"])
        self.assertEqual(project.allocation, data["GrantAmount"])
        self.assertEqual(project.programme_co_financing, data["ProgrammeCoFinancing"])
        self.assertEqual(project.project_co_financing, data["ProjectCoFinancing"])
        self.assertEqual(project.nuts, data["NUTSCode"])

    def _test_indicators(self):
        data = self.DATA[Indicator.IMPORT_SOURCE]

        indicator = Indicator.from_data(data)
        indicator.save()
        indicator = Indicator.objects.get()

        self.assertEqual(indicator.code, data["IndicatorCode"])
        self.assertEqual(indicator.name, data["Indicator"])

    def _test_programme_indicators(self):
        data = self.DATA[ProgrammeIndicator.IMPORT_SOURCE]

        p_i = ProgrammeIndicator.from_data(data)
        p_i.save()
        p_i = ProgrammeIndicator.objects.get()

        self.assertEqual(
            p_i.indicator, Indicator.objects.get_by_natural_key(data["IndicatorCode"])
        )
        self.assertEqual(p_i.achievement, data["Achievement"])

        # TODO: this isn't finished
        # self.assertFalse(True, "must.. implement..")

    def _test_organisation_types(self):
        data = self.DATA[OrganisationType.IMPORT_SOURCE]

        org_type = OrganisationType.from_data(data)
        org_type.save()
        org_type = OrganisationType.objects.get()

        category_attr = utils.str_to_constant_name(data["OrganisationTypeCategory"])
        self.assertEqual(
            org_type.category, getattr(OrganisationType.CATEGORIES, category_attr)
        )
        self.assertEqual(org_type.name, data["OrganisationType"])

    def _test_organisations(self):
        data = self.DATA[Organisation.IMPORT_SOURCE]

        org = Organisation.from_data(data)
        org.save()
        org = Organisation.objects.get()

        self.assertEqual(org.id, data["IdOrganisation"])
        self.assertEqual(org.name, data["Organisation"])
        ptype_attr = utils.str_to_constant_name(data["IsProgrammeOrProjectOrg"])
        self.assertEqual(org.ptype, getattr(Organisation.ORGANISATION_TYPE, ptype_attr))
        self.assertEqual(
            org.orgtype, OrganisationType.objects.get(name=data["OrganisationType"])
        )

    def _test_organisation_roles(self):
        pass

    def test_import(self):
        # most tests are dependent on previously-imported foreign keys,
        # so doing everything under a single test to avoid database teardown
        self._test_states()
        self._test_priority_sectors()
        self._test_programme_areas()
        self._test_programmes()
        self._test_programme_programme_areas()
        self._test_outcomes()
        self._test_programme_outcomes()
        self._test_projects()
        self._test_indicators()
        self._test_programme_indicators()
        self._test_organisation_types()
        self._test_organisations()
        self._test_organisation_roles()

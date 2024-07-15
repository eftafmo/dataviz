from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyText

from dv.models import BilateralInitiative, State
from dv.tests.factories.programme_factory import ProgrammeFactory
from dv.tests.factories.project_factory import ProjectFactory


class BilateralInitiativeFactory(DjangoModelFactory):
    class Meta:
        model = BilateralInitiative

    funding_period = 3
    code = FuzzyText("bi-code-")
    title = FuzzyText("bi-title-")
    grant = FuzzyDecimal(0)
    programme = SubFactory(ProgrammeFactory)
    project = SubFactory(ProjectFactory)
    state = FuzzyChoice(State.objects.all())

    initial_description = FuzzyText("project-initial-description-")
    results_description = FuzzyText("project-results-description-")

    status = FuzzyChoice(
        {
            "Completed",
            "Completion under review by FMO",
            "Completion under review by NFP",
            "Draft Completion",
            "On-going",
            "Under review by FMO",
            "Under review by NFP",
        }
    )

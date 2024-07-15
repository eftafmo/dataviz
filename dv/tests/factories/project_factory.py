from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyText

from dv.models import Project, State
from dv.tests.factories.programme_factory import ProgrammeFactory


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    funding_period = 3
    code = FuzzyText("project-code-")
    name = FuzzyText("project-name-")
    status = FuzzyChoice(
        {
            "Cancelled",
            "Completed",
            "Non Completed",
            "Partially Completed",
            "Partially completed",
            "Signed",
            "Terminated",
        }
    )
    state = FuzzyChoice(State.objects.all())
    programme = SubFactory(ProgrammeFactory)

    allocation = FuzzyDecimal(0)

    is_eea = True
    is_norway = False
    has_ended = False
    is_dpp = False
    is_positive_fx = False
    is_improved_knowledge = False
    is_continued_coop = False

    initial_description = FuzzyText("project-initial-description-")
    results_description = FuzzyText("project-results-description-")

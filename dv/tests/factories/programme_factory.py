from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyText

from dv.models import Programme


class ProgrammeFactory(DjangoModelFactory):
    class Meta:
        model = Programme

    funding_period = 3
    code = FuzzyText("programme-code-")
    name = FuzzyText("programme-name-")
    summary = FuzzyText("programme-summary-")

    status = FuzzyChoice(
        {
            "Approved",
            "Closed",
            "Completed",
            "Implementation",
            "Programme implementation",
        }
    )

    allocation_eea = FuzzyDecimal(0)
    allocation_norway = FuzzyDecimal(0)
    co_financing = FuzzyDecimal(0)

    is_tap = False
    is_bfp = False

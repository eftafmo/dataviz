from django.core.management.base import BaseCommand

from dv.models import (
    ProgrammeIndicator,
    ProgrammeOutcome,
)


class Command(BaseCommand):
    help = 'Fix state_id for IN22 indicators. Because relashionships are hard.'

    def handle(self, *args, **options):
        programme_indicators = ProgrammeIndicator.objects.all()
        for pi in programme_indicators:
            po = ProgrammeOutcome.objects.get(
                programme=pi.programme,
                outcome=pi.outcome
            )
            if pi.state_id != po.state_id:
                pi.state = po.state
                pi.save()

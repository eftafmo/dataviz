import logging
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.core.management import call_command

from dv.models import (
    State,
    NUTSVersion,
    NUTS,
    StaticContent,
)

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = "Load fixtures data"

    # Order is important
    FIXTURES = {
        "initial": (
            State,
            NUTSVersion,
            NUTS,
            StaticContent,
        ),
        "test": (User,),
    }

    def add_arguments(self, parser):
        parser.add_argument("fixture_type", choices=("initial", "test"))
        parser.add_argument(
            "-e",
            "--exclude",
            action="append",
            default=[],
            help="Exclude fixtures from the list",
        )
        parser.add_argument(
            "--dump",
            action="store_true",
            default=False,
            help="Dump the data back to the fixtures instead of loading it in the DB",
        )

    def handle(self, fixture_type, *args, exclude, dump=False, **options):
        logging.basicConfig()
        for model in self.FIXTURES[fixture_type]:
            opt = model._meta
            name = opt.model_name
            path = (
                Path(settings.BASE_DIR)
                / "dv"
                / "fixtures"
                / fixture_type
                / f"{name}.json"
            )

            if name in exclude:
                continue

            if dump:
                logger.info("Dumping fixtures: %s", path)
                call_command(
                    "dumpdata",
                    "--indent",
                    "2",
                    "-o",
                    str(path),
                    "--natural-foreign",
                    "--natural-primary",
                    f"{opt.app_label}.{name}",
                )
            else:
                logger.info("Loading fixtures: %s", path)
                call_command("loaddata", path)

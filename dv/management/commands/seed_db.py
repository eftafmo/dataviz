import shutil
import sys

from django.core.management import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seed DB for E2E tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Do not prompt for any user input",
            default=False,
        )

    def handle(self, *args, noinput=False, **options):
        if not noinput:
            print(
                "This will IRREVERSIBLY DESTROY all data currently in the  database! "
                "Are you sure you want to continue?",
                end=" ",
            )
            if input("[Y/n] ") != "Y":
                sys.exit(1)

        # Remove cache
        shutil.rmtree("/var/tmp/django_cache", ignore_errors=True)
        # Flush db
        call_command("flush", "--noinput")
        # Load initial fixtures
        call_command("load_fixtures", "initial")
        # Load test fixtures
        # Create users / password:
        #  - admin@example.com / admin
        call_command("load_fixtures", "test")
        # Rebuild ES
        call_command("rebuild_index", "--noinput")

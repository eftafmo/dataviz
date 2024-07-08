import json

from django.utils.encoding import force_str
from django.core.management.base import BaseCommand
from dv.models import NUTS


class Command(BaseCommand):
    help = "JSON dump the NUTS to stdout."

    def handle(self, *args, **options):
        nuts = {nut.code: force_str(nut.label) for nut in NUTS.objects.all()}
        json_nuts = json.dumps(nuts, sort_keys=True, indent=2, ensure_ascii=False)
        print(json_nuts)

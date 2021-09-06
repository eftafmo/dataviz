"""Import NUTS data into the DB"""

import csv
import logging

import requests
from django.core.management.base import BaseCommand

from dv.models import NUTS

logger = logging.getLogger(__name__)
API_BASE = "https://gisco-services.ec.europa.eu/distribution/v2/nuts"


def get_file_list(year):
    logger.debug("Getting dataset list for %s", year)
    resp = requests.get(f"{API_BASE}/datasets.json")
    resp.raise_for_status()
    dataset = resp.json()

    for key, values in dataset.items():
        if key.split("-")[-1] == year:
            files = values["files"]
            break
    else:
        raise RuntimeError(f"Unable to find files for {year}")

    logger.debug("Getting file list for %s", files)
    resp = requests.get(f"{API_BASE}/{files}")
    resp.raise_for_status()
    return resp.json()


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("year", help="NUTS version to import")

    def handle(self, year, verbosity, **options):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        if int(verbosity) > 0:
            logger.setLevel(logging.INFO)
        if int(verbosity) > 1:
            logger.setLevel(logging.DEBUG)

        file_path = get_file_list(year)["csv"][f"NUTS_AT_{year}.csv"]

        logger.info("Getting NUTS codes: %s", file_path)
        resp = requests.get(f"{API_BASE}/{file_path}")
        resp.raise_for_status()
        lines = resp.content.decode("utf8").splitlines()

        created_count = 0
        reader = csv.DictReader(lines)
        for line in reader:
            name, latin_name = line["NUTS_NAME"], line["NAME_LATN"]
            if name == latin_name:
                label = name
            else:
                label = f"{name} / {latin_name}"

            obj, created = NUTS.objects.update_or_create(
                {"label": label}, code=line["NUTS_ID"]
            )
            created_count += created
            logger.info("NUTS %s, created=%s", obj, created)

        logger.info("Created %s out of %s", created_count, len(lines) - 1)


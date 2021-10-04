"""Import NUTS data into the DB"""

import csv
import logging

import requests
from django.core.management.base import BaseCommand

from dv.models import NUTS
from dv.models import NUTSVersion

logger = logging.getLogger(__name__)
API_BASE = "https://gisco-services.ec.europa.eu/distribution/v2/nuts"

# Some Organisations have fake NUTS code, so include them here as well.
FAKE_NUTS = {
    "UA010": "Ukraine",
    "MD010": "Moldova, Republic of",
    "RS0GF": "Serbia",
    "RS-061": "Serbia",
    "RU010": "Russian Federation",
}


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

        nuts_version = NUTSVersion.objects.get_or_create(
            year=year, defaults={"year": year}
        )[0]

        nuts_0 = []
        created_count = 0
        reader = csv.DictReader(lines)
        for line in reader:
            if len(line["NUTS_ID"]) == 2:
                nuts_0.append(line["NUTS_ID"])

            name, latin_name = line["NUTS_NAME"], line["NAME_LATN"]
            if name == latin_name:
                label = name
            else:
                label = f"{name} / {latin_name}"

            obj, created = NUTS.objects.update_or_create(
                {"label": label}, code=line["NUTS_ID"]
            )
            obj.nuts_versions.add(nuts_version)
            created_count += created
            logger.info("NUTS %s, created=%s", obj, created)

        logger.info("Created %s out of %s", created_count, len(lines) - 1)

        # Extra-Regio codes are used to indicate there is no region.
        # Add them as well to the DB for integrity checks.
        created_count = 0
        for country_code in nuts_0:
            for level in (1, 2, 3):
                code = country_code + "Z" * level
                label = f"Extra-Regio NUTS {level}"

                obj, created = NUTS.objects.update_or_create(
                    {"label": label}, code=code
                )
                obj.nuts_versions.add(nuts_version)
                created_count += created
                logger.info("NUTS extra %s, created=%s", obj, created)
        logger.info("Created Extra-Regio %s out of %s", created_count, len(nuts_0 * 3))

        created_count = 0
        for code, label in FAKE_NUTS.items():
            obj, created = NUTS.objects.update_or_create(
                {"label": label}, code=code
            )
            obj.nuts_versions.add(nuts_version)
            created_count += created
            logger.info("NUTS extra %s, created=%s", obj, created)
        logger.info("Created Fake NUTS codes %s out of %s", created_count, len(FAKE_NUTS))


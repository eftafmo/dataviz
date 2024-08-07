from datetime import datetime
import requests

from django.core.cache import cache
from django.core.management.base import BaseCommand
from pytz import timezone

from dv.models import News, Programme, Project

ENDPOINT = "https://eeagrants.org/rest/articles?page={}"
TZ = timezone("Europe/Brussels")


def parse_time(value: str) -> datetime:
    try:
        # Check if value is already a timestamp
        timestamp = int(value)
    except (ValueError, TypeError):
        # Value may look like:
        # <time datetime="2024-07-05T13:15:40+02:00">1720178140</time>
        timestamp = int(value.split(">")[1].split("<")[0].strip())

    return TZ.localize(datetime.fromtimestamp(timestamp))


class Command(BaseCommand):
    help = f"Import news from {ENDPOINT}"

    def handle(self, *args, **options):
        page = 0
        data = []
        while page == 0 or data:
            resp = requests.get(ENDPOINT.format(page))
            resp.raise_for_status()
            data = resp.json()["posts"]
            if page == 0:
                News.objects.all().delete()
            self.stdout.write(f"Importing {len(data)} news from page {page}")
            for item in data:
                self._save(item)
            page += 1
        cache.clear()
        self.stdout.write("Cache cleared")

    def _save(self, item):
        try:
            link = item["link"].replace("http://", "https://")
            # self.stdout.write('Importing post %s' % link)
            news, created = News.objects.get_or_create(link=link)
            news.title = item["title"]
            news.created = parse_time(item["created"])
            news.updated = parse_time(item["updated"])
            news.summary = item["summary"]
            news.image = item["image"].replace("http://", "https://")
            news.is_partnership = item["is_partnership"] == "yes"
            project_id = item.get("project_id").strip()
            if project_id:
                if Project.objects.filter(code=project_id).exists():
                    news.project_id = project_id
                else:
                    self.stderr.write(f"Project code: {project_id} doesn't exist!")
            news.save()

            programme_ids = item.get("programme_id")
            if programme_ids:
                programme_ids = programme_ids.split(", ")
                for programme in Programme.objects.filter(code__in=programme_ids):
                    news.programmes.add(programme)
                    programme_ids.remove(programme.code)
                if len(programme_ids) >= 1:
                    self.stderr.write(
                        f"Programmes with codes {programme_ids} not found."
                    )

        except Exception as err:
            self.stderr.write("ERROR: %s" % repr(err))

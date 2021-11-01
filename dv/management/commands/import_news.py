import json

from urllib.request import urlopen
from datetime import datetime

from django.core.cache import cache
from pytz import timezone

from django.core.management.base import BaseCommand
from dv.models import News, Project

ENDPOINT = 'https://eeagrants.org/rest/articles?page={}'


class Command(BaseCommand):
    help = f'Import news from {ENDPOINT}'

    def handle(self, *args, **options):
        page = 0
        data = []
        while page == 0 or data:
            with urlopen(ENDPOINT.format(page)) as url:
                data = json.loads(url.read().decode())['posts']
                if page == 0:
                    News.objects.all().delete()
                self.stdout.write(f'Importing {len(data)} news from page {page}')
                for item in data:
                    self._save(item)
                page += 1
        cache.clear()
        self.stdout.write('Cache cleared')

    def _save(self, item):
        try:
            link = item['link'].replace('http://', 'https://')
            # self.stdout.write('Importing post %s' % link)
            news, created = News.objects.get_or_create(link=link)
            news.title = item['title']
            tz = timezone('Europe/Brussels')
            news.created = tz.localize(datetime.fromtimestamp(int(item['created'])))
            news.updated = tz.localize(datetime.fromtimestamp(int(item['updated'])))
            news.summary = item['summary']
            news.image = item['image'].replace('http://', 'https://')
            news.is_partnership = item['is_partnership'] == 'yes'
            if item['project_id']:
                project = Project.objects.filter(code=item['project_id']).exists()
                if project:
                    news.project_id = item['project_id'].strip()
            news.save()

            if item["programme_id"]:
                for prg in item['programme_id'].split(', '):
                    news.programmes.add(prg.upper().strip())

        except Exception as err:
            self.stderr.write(('ERROR: %s' % repr(err)))

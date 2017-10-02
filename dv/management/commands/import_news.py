import json

from urllib.request import urlopen
from datetime import datetime

from django.core.cache import cache
from pytz import timezone

from django.core.management.base import BaseCommand
from dv.models import News

ENDPOINT = 'http://eeagrants.org/rest/articles?page={}'


class Command(BaseCommand):
    help = 'Import news from %s' % ENDPOINT

    def handle(self, *args, **options):
        page = 1
        data = []
        while page == 1 or data:
            with urlopen(ENDPOINT.format(page)) as url:
                data = json.loads(url.read().decode())['posts']
                if page == 1:
                    News.objects.all().delete()
                print('Importing {} news from page {}'.format(len(data), page))
                for item in data:
                    self._save(item)
                page += 1
        cache.clear()
        print("Cache cleared")

    def _save(self, item):
        try:
            link = item['link'].replace('http://', 'https://')
            self.stdout.write('Importing post %s' % link)
            news, created = News.objects.get_or_create(link=link)
            news.title = item['title']
            tz = timezone('Europe/Brussels')
            news.created = tz.localize(datetime.fromtimestamp(int(item['created'])))
            news.updated = tz.localize(datetime.fromtimestamp(int(item['updated'])))
            news.summary = item['summary']
            news.image = item['image'].replace('http://', 'https://')
            news.is_partnership = item['is_partnership'] == 'yes'
            if item['project_id']:
                news.project_id = item['project_id'][0:9].upper().strip()
            news.save()

            for prg in item['programme_id'].split(', '):
                news.programmes.add(prg.upper().strip())

        except Exception as err:
            self.stderr.write(('ERROR: %s' % repr(err)))

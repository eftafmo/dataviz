import json

from urllib.request import urlopen
from datetime import datetime
from pytz import timezone

from django.core.management.base import BaseCommand
from dv.models import News

ENDPOINT = 'http://eeagrants.org/rest/articles?page={}'


class Command(BaseCommand):
    help = 'Import the file given as argument'

    def handle(self, *args, **options):
        page = 0
        data = []
        News.objects.all().delete()
        while page == 0 or data:
            with urlopen(ENDPOINT.format(page)) as url:
                data = json.loads(url.read().decode())['posts']
                print('Importing {} news from page {}'.format(len(data), page))
                for item in data:
                    self._save(item)
                page += 1

    def _save(self, item):
        try:
            self.stdout.write('Importing post %s' % item['link'])
            news, created = News.objects.get_or_create(link=item['link'])
            news.title = item['title']
            tz = timezone('Europe/Brussels')
            news.created = tz.localize(datetime.fromtimestamp(int(item['created'])))
            news.updated = tz.localize(datetime.fromtimestamp(int(item['updated'])))
            news.summary = item['summary']
            news.image = item['image']
            news.is_partnership = item['is_partnership'] == 'yes'
            news.project_id = item['project_id']
            news.save()

            for prg in item['programme_id'].split(', '):
                news.programmes.add(prg)

        except Exception as err:
            self.stderr.write(('ERROR: %s' % repr(err)))

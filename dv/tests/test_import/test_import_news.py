from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from dv.models import News

from dv.tests.factories.project_factory import ProjectFactory


class TestImportNews(TestCase):
    fixtures = ["initial/state"]

    def setUp(self):
        self.project = ProjectFactory()
        self.mock_posts = [
            {
                "title": "The fight against disinformation",
                "link": "https://example.com/news/fight-against-disinformation",
                "created": '<time datetime="2024-07-05T13:15:40+02:00">1720178140</time>',
                "updated": "1720180299",
                "programme_id": self.project.programme.code,
                "project_id": self.project.code,
                "summary": "Disinformation and fake news",
                "image": "",
                "is_partnership": "no",
            },
        ]
        self.mock_open = patch("dv.management.commands.import_news.requests").start()
        self.mock_open.get.return_value.json.side_effect = [
            {"posts": self.mock_posts},
            {"posts": []},
        ]

    def tearDown(self):
        patch.stopall()

    def test_import_news(self):
        call_command("import_news")
        obj = News.objects.first()
        self.assertEqual(obj.title, "The fight against disinformation")
        self.assertEqual(obj.project, self.project)

    def test_import_news_no_project(self):
        self.project.delete()
        call_command("import_news")
        obj = News.objects.first()
        self.assertEqual(obj.title, "The fight against disinformation")
        self.assertEqual(obj.project, None)

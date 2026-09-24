from django.urls import reverse

from dv.tests.test_search.base import SearchViewTestCase


class TestExport(SearchViewTestCase):
    export_url = reverse("frontend:project_export")

    def test_export_link_drops_pagination(self):
        resp = self.client.get(
            reverse("frontend:search_project"),
            {"page": 1, "paginate_by": 25, "country": "Poland"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context["export_url"], self.export_url + "?country=Poland"
        )

    def test_export_without_pagination_is_served(self):
        resp = self.client.get(self.export_url, {"country": "Poland"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp["Content-Disposition"])

    def test_robots_disallows_export(self):
        with self.settings(DEBUG=False):
            resp = self.client.get(reverse("frontend:robots"))
        self.assertIn("Disallow: /search/export/", resp.content.decode())

from collections import defaultdict
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from dv.views.frontend import ProgrammeFacetedSearchView


# Don't depend on a frontend build or a running Elasticsearch
@patch("dv.context.load_manifest", return_value=defaultdict(str))
@patch(
    "dv.lib.es7.CustomES7SearchBackend.search",
    return_value={"results": [], "hits": 0, "facets": {"fields": {}}},
)
class TestSearchPaginateBy(TestCase):
    url = reverse("frontend:search")

    def get_per_page(self, **params):
        resp = self.client.get(self.url, params)
        self.assertEqual(resp.status_code, 200)
        return resp.context["paginator"].per_page

    def test_allowed_sizes(self, *_mocks):
        for size in ProgrammeFacetedSearchView.page_sizes:
            with self.subTest(size=size):
                self.assertEqual(self.get_per_page(paginate_by=size), size)

    def test_invalid_values_fall_back_to_default(self, *_mocks):
        for value in ["abc", "", "0", "-10", "7", "100000", "10.5", "1e3"]:
            with self.subTest(value=value):
                self.assertEqual(self.get_per_page(paginate_by=value), 10)

    def test_missing_uses_default(self, *_mocks):
        self.assertEqual(self.get_per_page(), 10)

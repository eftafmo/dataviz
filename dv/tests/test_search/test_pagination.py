from django.urls import reverse

from dv.tests.test_search.base import SearchViewTestCase
from dv.views.frontend import ProgrammeFacetedSearchView


class TestSearchPaginateBy(SearchViewTestCase):
    url = reverse("frontend:search")

    def get_per_page(self, **params):
        resp = self.client.get(self.url, params)
        self.assertEqual(resp.status_code, 200)
        return resp.context["paginator"].per_page

    def test_allowed_sizes(self):
        for size in ProgrammeFacetedSearchView.page_sizes:
            with self.subTest(size=size):
                self.assertEqual(self.get_per_page(paginate_by=size), size)

    def test_invalid_values_fall_back_to_default(self):
        for value in ["abc", "", "0", "-10", "7", "100000", "10.5", "1e3"]:
            with self.subTest(value=value):
                self.assertEqual(self.get_per_page(paginate_by=value), 10)

    def test_missing_uses_default(self):
        self.assertEqual(self.get_per_page(), 10)

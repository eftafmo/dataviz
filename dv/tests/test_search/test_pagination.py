from django.test import RequestFactory, TestCase

from dv.views.frontend import ProgrammeFacetedSearchView


class TestPaginateBy(TestCase):
    def paginate_by(self, value):
        view = ProgrammeFacetedSearchView()
        view.setup(RequestFactory().get("/search/programme/", {"paginate_by": value}))
        return view.get_paginate_by(None)

    def test_allowed_sizes(self):
        for size in ProgrammeFacetedSearchView.page_sizes:
            with self.subTest(size=size):
                self.assertEqual(self.paginate_by(str(size)), size)

    def test_invalid_values_fall_back_to_default(self):
        for value in ["abc", "", "0", "-10", "7", "100000", "10.5", "1e3"]:
            with self.subTest(value=value):
                self.assertEqual(self.paginate_by(value), 10)

    def test_missing_uses_default(self):
        view = ProgrammeFacetedSearchView()
        view.setup(RequestFactory().get("/search/programme/"))
        self.assertEqual(view.get_paginate_by(None), 10)

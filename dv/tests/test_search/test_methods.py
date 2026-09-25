from django.urls import reverse

from dv.tests.test_search.base import SearchViewTestCase


class TestSearchNonGetRequests(SearchViewTestCase):
    url = reverse("frontend:search")

    def test_head_does_not_crash(self):
        # HEAD is routed to get(); haystack < 3.4 left the form unbound for it
        resp = self.client.head(self.url, {"q": "water"})
        self.assertEqual(resp.status_code, 200)

    def test_post_does_not_crash(self):
        # POST leaves the form unbound, so it has no cleaned_data
        resp = self.client.post(self.url, {"q": "water"})
        self.assertEqual(resp.status_code, 200)

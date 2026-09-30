from django.test import TestCase
from django.urls import reverse

from dv.lib.utils import FUNDING_PERIODS_DICT


class TestApiPeriod(TestCase):
    fixtures = ["initial/state"]
    urls = [
        reverse("api:bilateral-initiatives"),
        reverse("api:index"),
        reverse("api:indicators"),
        reverse("api:grants"),
        reverse("api:goals"),
        reverse("api:projects"),
        reverse("api:partners"),
        reverse("api:grants-beneficiary-detail", kwargs={"beneficiary": "RO"}),
        reverse("api:projects-beneficiary-detail", kwargs={"beneficiary": "RO"}),
        reverse("api:sdg-beneficiary-detail", kwargs={"beneficiary": "RO"}),
        reverse("api:project-list"),
    ]

    def test_invalid_period_is_bad_request(self):
        for url in self.urls:
            for period in ["bogus", "", "compare", '2009-2014") AND 1=1-- -']:
                with self.subTest(url=url, period=period):
                    resp = self.client.get(url, {"period": period})
                    self.assertEqual(resp.status_code, 400)

    def test_valid_periods(self):
        url = reverse("api:bilateral-initiatives")
        for period in FUNDING_PERIODS_DICT:
            with self.subTest(period=period):
                resp = self.client.get(url, {"period": period})
                self.assertEqual(resp.status_code, 200)

from django.test import TestCase
from django.urls import reverse
from dv.models import State
from dv.tests.factories.bilateral_initiative_factory import BilateralInitiativeFactory


class TestBilateralInitiativesApi(TestCase):
    fixtures = ["initial/state"]
    url = reverse("api:bilateral-initiatives")

    def setUp(self):
        self.state = State.objects.first()
        self.bi1 = BilateralInitiativeFactory(state=self.state, grant=10)
        self.bi2 = BilateralInitiativeFactory(state=self.state, grant=20)

    def test_api(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["allocation"], "30")
        self.assertEqual(data[0]["beneficiary"], self.state.code)

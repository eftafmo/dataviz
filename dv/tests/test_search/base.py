from collections import defaultdict
from unittest.mock import patch

from django.test import TestCase


class SearchViewTestCase(TestCase):
    """Test case for search views that runs without external services.

    Elasticsearch is replaced by a mock returning `search_results` (no hits by
    default), available as `self.search_mock`. The Vite manifest is mocked too,
    so templates render without a frontend build.
    """

    search_results = {"results": [], "hits": 0, "facets": {"fields": {}}}

    def setUp(self):
        super().setUp()
        self.search_mock = self.patch(
            "dv.lib.es7.CustomES7SearchBackend.search",
            return_value=self.search_results,
        )
        self.patch("dv.context.load_manifest", return_value=defaultdict(str))

    def patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

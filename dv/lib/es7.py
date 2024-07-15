from copy import deepcopy

from haystack.backends.elasticsearch7_backend import Elasticsearch7SearchBackend
from haystack.backends.elasticsearch7_backend import Elasticsearch7SearchEngine


_custom_settings = deepcopy(Elasticsearch7SearchBackend.DEFAULT_SETTINGS)
# For Organisation export, which has more than 10K entries
_custom_settings["settings"]["index"]["max_result_window"] = 20000


class CustomES7SearchBackend(Elasticsearch7SearchBackend):
    DEFAULT_SETTINGS = _custom_settings

    def build_search_kwargs(self, *args, **kwargs):
        query_args = super(CustomES7SearchBackend, self).build_search_kwargs(
            *args, **kwargs
        )
        # See https://helpdesk.eaudeweb.ro/issues/11216
        # See https://www.elastic.co/guide/en/elasticsearch/reference/7.x/search-your-data.html#track-total-hits
        query_args["track_total_hits"] = True
        return query_args


class CustomES7SearchEngine(Elasticsearch7SearchEngine):
    backend = CustomES7SearchBackend

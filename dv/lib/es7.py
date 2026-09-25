from copy import deepcopy

from haystack.backends.elasticsearch7_backend import (
    Elasticsearch7SearchBackend,
    Elasticsearch7SearchEngine,
    Elasticsearch7SearchQuery,
)

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


def _escape_phrase(value):
    # Only backslashes and double quotes are special inside a quoted phrase.
    return value.replace("\\", "\\\\").replace('"', '\\"')


class CustomES7SearchQuery(Elasticsearch7SearchQuery):
    def build_query_fragment(self, field, filter_type, value):
        # Haystack wraps each `__in` value in double quotes without escaping it,
        # so a value containing `"` produces an invalid query and ES errors with 400.
        if filter_type == "in" and isinstance(value, (list, tuple, set)):
            value = [_escape_phrase(v) if isinstance(v, str) else v for v in value]
        return super().build_query_fragment(field, filter_type, value)


class CustomES7SearchEngine(Elasticsearch7SearchEngine):
    backend = CustomES7SearchBackend
    query = CustomES7SearchQuery

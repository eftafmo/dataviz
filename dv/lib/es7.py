from copy import deepcopy

from haystack.backends.elasticsearch7_backend import Elasticsearch7SearchBackend
from haystack.backends.elasticsearch7_backend import Elasticsearch7SearchEngine


_custom_settings = deepcopy(Elasticsearch7SearchBackend.DEFAULT_SETTINGS)
# For Organisation export, which has more than 10K entries
_custom_settings["settings"]["index"]["max_result_window"] = 20000


class CustomES7SearchBackend(Elasticsearch7SearchBackend):
    DEFAULT_SETTINGS = _custom_settings


class CustomES7SearchEngine(Elasticsearch7SearchEngine):
    backend = CustomES7SearchBackend

from haystack import indexes
from dv.models import Programme


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    # TODO use template here to include more than summary
    text = indexes.CharField(document=True, model_attr='summary')

    status = indexes.CharField(model_attr='status', faceted=True)
    state_code = indexes.CharField(model_attr='state__code', faceted=True)
    state_name = indexes.CharField(model_attr='state__name')

    def get_model(self):
        return Programme


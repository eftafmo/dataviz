from haystack import indexes
from dv.models import Programme


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(index_fieldname='name_s', model_attr='name')
    text = indexes.CharField(document=True, model_attr='summary')

    def get_model(self):
        return Programme


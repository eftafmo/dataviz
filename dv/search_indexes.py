from haystack import indexes
from dv.models import Programme


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    # TODO use template here to include more than summary
    text = indexes.CharField(document=True, model_attr='summary')

    status = indexes.CharField(model_attr='status', faceted=True)
    state_code = indexes.CharField(model_attr='state__code', faceted=True)
    state_name = indexes.CharField(model_attr='state__name')

    programme_area_ss = indexes.FacetMultiValueField(model_attr='programme_areas__name')
    priority_sector_ss = indexes.FacetMultiValueField(model_attr='programme_areas__priority_sector__name')

    def get_model(self):
        return Programme

    def prepare_programme_area_ss(self, obj):
        return list(set([ pa.name for pa in obj.programme_areas.all() ]))

    def prepare_priority_sector_ss(self, obj):
        return list(set([ pa.priority_sector.name for pa in obj.programme_areas.all() ]))


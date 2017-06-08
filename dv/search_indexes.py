from haystack import indexes
from dv.models import Programme


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    # TODO use template here to include more than summary
    text = indexes.CharField(model_attr='summary', document=True)

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


class OrganizationINdex(indexes.SearchIndex, indexes.Idexable):
    text = indexes.CharField(model_attr='name', document=True)

    orgtype = indexes.FacetCharField(model_attr='orgtype')
    # TODO this is not a foreign key yet...
    country = indexes.FacetCharField(model_attr='country')
    nuts = indexes.FacetCharField(model_attr='nuts')
    # FIXME I don't get the OrganisationRole model - shouldn't it be a many-to-many? or many org to one role?
    # role =
    # FIXME import geographical target...

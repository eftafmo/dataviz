from haystack import indexes
from dv.models import Programme, Project, Organisation, Allocation, ProgrammeOutcome


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    # some non-DRY code here, but the factor out is not trivial due to common indexes having different model lookup
    state_name = indexes.FacetCharField(model_attr='state__name')
    programme_area_ss = indexes.FacetMultiValueField(model_attr='programme_areas__name')
    priority_sector_ss = indexes.FacetMultiValueField(model_attr='programme_areas__priority_sector__name')
    financial_mechanism_ss = indexes.FacetMultiValueField()
    outcome_ss = indexes.FacetMultiValueField()
    programme_name = indexes.FacetCharField(model_attr='name')
    programme_status = indexes.FacetCharField(model_attr='status')

    kind = indexes.FacetCharField()

    # specific facets

    # specific fields
    # TODO use template here to include more than summary
    text = indexes.CharField(model_attr='summary', document=True)


    def get_model(self):
        return Programme

    def prepare_kind(self, obj):
        return 'Programme'

    def prepare_programme_area_ss(self, obj):
        return list(obj.programme_areas.values_list(
            'name', flat=True).distinct())

    def prepare_priority_sector_ss(self, obj):
        return list(obj.programme_areas.values_list(
            'priority_sector__name', flat=True).distinct())

    def prepare_financial_mechanism_ss(self, obj):
        pa = obj.programme_areas.all()
        return list(Allocation.objects.filter(
            programme_area__in=pa
        ).values_list(
            'financial_mechanism__name', flat=True
        ).distinct())

    def prepare_outcome_ss(self, obj):
        return list(ProgrammeOutcome.objects.filter(
            programme=obj,
        ).values_list(
            'outcome__name', flat=True
        ).distinct())


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    state_name = indexes.FacetCharField(model_attr='state__name')
    programme_area_ss = indexes.FacetMultiValueField(model_attr='programme__programme_areas__name')
    priority_sector_ss = indexes.FacetMultiValueField(model_attr='programme__programme_areas__priority_sector__name')
    programme_name = indexes.FacetCharField(model_attr='programme__name')
    programme_status = indexes.FacetCharField(model_attr='programme__status')

    kind = indexes.FacetCharField()

    # specific facets
    project_status = indexes.FacetCharField(model_attr='status')
    geotarget = indexes.FacetCharField(model_attr='geotarget')

    # specific fields
    text = indexes.CharField(model_attr='name', document=True)

    def get_model(self):
        return Project

    def prepare_kind(self, obj):
        return 'Project'

    def prepare_programme_area_ss(self, obj):
        return list(obj.programme.programme_areas.values_list(
            'name', flat=True).distinct())

    def prepare_priority_sector_ss(self, obj):
        return list(obj.programme.programme_areas.values_list(
            'priority_sector__name', flat=True).distinct())


class OrganisationIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    # this should be *_ss for this model, but we want the same name across indexes for this logical entity
    # This will upgrade the previous definitions from CharField to MultiValue
    # make sure you rebuild_index from zero when adding such "upgrade" here
    state_name = indexes.FacetMultiValueField()
    # programme_status = indexes.FacetMultiValueField(model_attr='programme__status')
    programme_name = indexes.FacetMultiValueField()
    project_name = indexes.FacetMultiValueField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()

    text = indexes.CharField(model_attr='name', document=True)

    kind = indexes.FacetCharField()

    # specific facets
    # haystack handles null apparently
    org_type_caegory = indexes.FacetCharField(model_attr='orgtype__category')
    org_type = indexes.FacetCharField(model_attr='orgtype__name')
    country = indexes.FacetCharField(model_attr='country')
    nuts = indexes.FacetCharField(model_attr='nuts')
    role_ss = indexes.FacetMultiValueField()

    def get_model(self):
        return Organisation

    def prepare_kind(self, obj):
        return 'Organisation'

    def prepare_state_name(self, obj):
        result = set()
        result = result.union(obj.roles.filter(is_programme=False).values_list(
            'project__state__name', flat=True).distinct())
        result = result.union(obj.roles.filter(is_programme=True).values_list(
            'programme__state__name', flat=True).distinct())
        return list(result)

    def prepare_programme_area_ss(self, obj):
        result = set()
        result = result.union(obj.roles.filter(is_programme=False).values_list(
            'project__programme_area__name', flat=True).distinct())
        result = result.union(obj.roles.filter(is_programme=True).values_list(
            'programme__programme_areas__name', flat=True).distinct())
        return list(result)

    def prepare_priority_sector(self, obj):
        result = set()
        result = result.union(obj.roles.filter(is_programme=False).values_list(
            'project__programme_area__priority_sector__name', flat=True).distinct())
        result = result.union(obj.roles.filter(is_programme=True).values_list(
            'programme__programme_areas__priority_sector__name', flat=True).distinct())
        return list(result)

    def prepare_programme_name(self, obj):
        return list(obj.roles.filter(is_programme=True).values_list(
            'programme__name', flat=True).distinct())

    def prepare_project_name(self, obj):
        return list(obj.roles.filter(is_programme=False).values_list(
            'project__name', flat=True).distinct())

    def prepare_role_ss(self, obj):
        return list(obj.role.all().values_list('code', flat=True).distinct())

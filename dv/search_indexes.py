from haystack import indexes
from haystack import exceptions
from django_countries import countries

from dv.models import (
    Allocation,
    Organisation,
    Programme,
    ProgrammeOutcome,
    Project,
    State,
)

STATES = dict(countries)


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    # some non-DRY code here, but the factor out is not trivial due to common indexes having different model lookup
    state_name = indexes.FacetMultiValueField(model_attr='state__name')
    programme_area_ss = indexes.FacetMultiValueField(model_attr='programme_areas__name')
    priority_sector_ss = indexes.FacetMultiValueField(model_attr='programme_areas__priority_sector__name')
    financial_mechanism_ss = indexes.FacetMultiValueField()
    outcome_ss = indexes.FacetMultiValueField()
    outcome_ss_auto = indexes.EdgeNgramField()
    programme_name = indexes.FacetMultiValueField(model_attr='name')
    programme_status = indexes.FacetMultiValueField(model_attr='status')

    kind = indexes.FacetCharField()

    # specific facets

    # specific fields
    text = indexes.CharField(document=True, use_template=True)

    # extra data; avoid db hit
    url = indexes.CharField(model_attr='url', indexed=False, null=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)
    name = indexes.CharField(model_attr='name', indexed=False)
    code = indexes.FacetCharField(model_attr='code')
    grant = indexes.DecimalField()

    def get_model(self):
        return Programme

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_tap=False)

    def prepare_kind(self, obj):
        return 'Programme'

    def prepare_state_name(self, obj):
        # Get this from ProgrammeOutcome, because of IN22
        return list(ProgrammeOutcome.objects.filter(
            programme__code=obj.code,
        ).values_list(
            'state__name', flat=True
        ).distinct())

    def prepare_programme_name(self, obj):
        return ['{}: {}'.format(obj.code, obj.name)]

    def prepare_programme_area_ss(self, obj):
        return list(obj.programme_areas.values_list(
            'name', flat=True).distinct())

    def prepare_priority_sector_ss(self, obj):
        return list(obj.programme_areas.values_list(
            'priority_sector__name', flat=True).distinct())

    def prepare_financial_mechanism_ss(self, obj):
        pa = obj.programme_areas.all()
        # TODO: get via PA > PS > FM instead of Allocation
        return list(Allocation.objects.filter(
            programme_area__in=pa
        ).values_list(
            'financial_mechanism__grant_name', flat=True
        ).distinct())

    def prepare_outcome_ss(self, obj):
        return list(ProgrammeOutcome.objects.filter(
            programme=obj,
        ).exclude(
            outcome__fixed_budget_line=True,
        ).values_list(
            'outcome__name', flat=True
        ).distinct())

    def prepare_outcome_ss_auto(self, obj):
        return ' '.join(self.prepare_outcome_ss(obj))

    def prepare_grant(self, obj):
        return obj.allocation_eea + obj.allocation_norway


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    state_name = indexes.FacetMultiValueField(model_attr='state__name')
    financial_mechanism_ss = indexes.FacetMultiValueField(model_attr='financial_mechanism__grant_name')
    programme_area_ss = indexes.FacetMultiValueField(model_attr='programme_area__name')
    priority_sector_ss = indexes.FacetMultiValueField(model_attr='programme_area__priority_sector__name')
    programme_name = indexes.FacetMultiValueField(model_attr='programme__name')
    programme_status = indexes.FacetMultiValueField(model_attr='programme__status')
    outcome_ss = indexes.FacetMultiValueField(model_attr='outcome__name')

    kind = indexes.FacetCharField()

    # specific facets
    project_status = indexes.FacetMultiValueField(model_attr='status')
    geotarget = indexes.FacetCharField(model_attr='geotarget')
    # geotarget_auto = indexes.EdgeNgramField(model_attr='geotarget')
    theme_ss = indexes.FacetMultiValueField(model_attr='themes__name')

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)

    # extra data; avoid db hit
    url = indexes.CharField(model_attr='url', indexed=False, null=True)
    name = indexes.CharField(model_attr='name', indexed=False)
    code = indexes.FacetCharField(model_attr='code')
    grant = indexes.DecimalField(model_attr='allocation')

    def get_model(self):
        return Project

    def prepare_kind(self, obj):
        return 'Project'

    def prepare_financial_mechanism_ss(self, obj):
        return [obj.financial_mechanism.grant_name]

    def prepare_programme_area_ss(self, obj):
        return [obj.programme_area.name]

    def prepare_priority_sector_ss(self, obj):
        return [obj.programme_area.priority_sector.name]

    def prepare_programme_name(self, obj):
        return ['{}: {}'.format(obj.programme.code, obj.programme.name)]

    def prepare_outcome_ss(self, obj):
        return [obj.outcome.name]

    def prepare_geotarget(self, obj):
        if len(obj.nuts) > 2:
            return ['{}: {}, {}'.format(obj.nuts, obj.geotarget, STATES[obj.nuts[:2]])]
        else:
            return ['{}: {}'.format(obj.nuts, obj.geotarget)]


class OrganisationIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    # this should be *_ss for this model, but we want the same name across indexes for this logical entity
    # This will upgrade the previous definitions from CharField to MultiValue
    # make sure you rebuild_index from zero when adding such "upgrade" here
    state_name = indexes.FacetMultiValueField()
    programme_status = indexes.FacetMultiValueField()
    financial_mechanism_ss = indexes.FacetMultiValueField()
    programme_name = indexes.FacetMultiValueField()
    programme_name_auto = indexes.EdgeNgramField()
    project_name = indexes.FacetMultiValueField()
    project_name_auto = indexes.EdgeNgramField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()

    text = indexes.CharField(document=True, use_template=True)

    kind = indexes.FacetCharField()

    # specific facets
    # haystack handles null apparently
    project_status = indexes.FacetMultiValueField()
    org_type_category = indexes.FacetCharField(model_attr='orgtype__category')
    org_type = indexes.FacetCharField(model_attr='orgtype__name')
    country = indexes.FacetCharField(model_attr='country')
    city = indexes.FacetCharField(model_attr='city')
    # nuts = indexes.FacetCharField(model_attr='nuts')
    geotarget = indexes.FacetCharField(model_attr='geotarget', null=True)
    # nuts_auto = indexes.EdgeNgramField(model_attr='nuts')
    role_ss = indexes.FacetMultiValueField()

    # extra data; avoid db hit
    name = indexes.CharField(model_attr='name', indexed=False)
    domestic_name = indexes.CharField(model_attr='domestic_name', indexed=False, null=True)

    def get_model(self):
        return Organisation

    def prepare_kind(self, obj):
        return 'Organisation'

    def prepare_financial_mechanism_ss(self, obj):
        result = set()
        result = result.union(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).values_list(
            'project__programme_area__allocation__financial_mechanism__grant_name',
            flat=True,
        ).distinct())
        result = result.union(obj.roles.filter(
            is_programme=True, programme__isnull=False
        ).values_list(
            'programme__programme_areas__allocation__financial_mechanism__grant_name',
            flat=True,
        ).distinct())
        return list(result)

    def prepare_state_name(self, obj):
        result = set()
        result = result.union(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).values_list(
            'project__state__name', flat=True).distinct())

        result = result.union(obj.roles.filter(
            is_programme=True, programme__isnull=False
        ).values_list(
            'programme__outcomes__state__name', flat=True).distinct())
        return list(result)

    # we don't union here because we have two different fields on each Organisation
    # one telling us the programme statuses related to it and another the project statuses
    def prepare_programme_status(self, obj):
        return list(obj.roles.filter(
            is_programme=True, programme__isnull=False
        ).distinct().values_list(
            'programme__status', flat=True
        ))

    def prepare_project_status(self, obj):
        return list(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).distinct().values_list(
            'project__status', flat=True
        ))

    def prepare_programme_area_ss(self, obj):
        result = set()
        result = result.union(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).values_list(
            'project__programme_area__name', flat=True).distinct())
        result = result.union(obj.roles.filter(
            is_programme=True, programme__isnull=False
        ).values_list(
            'programme__programme_areas__name', flat=True).distinct())
        return list(result)

    def prepare_priority_sector_ss(self, obj):
        result = set()
        result = result.union(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).values_list(
            'project__programme_area__priority_sector__name', flat=True).distinct())
        result = result.union(obj.roles.filter(
            is_programme=True, programme__isnull=False
        ).values_list(
            'programme__programme_areas__priority_sector__name', flat=True).distinct())
        return list(result)

    def prepare_programme_name(self, obj):
        programmes = obj.roles.filter(
            programme__isnull=False,
            programme__is_tap=0,
        ).values(
            'programme__code',
            'programme__name',
        ).distinct()
        result = []
        for prg in programmes:
            result.append('{}: {}'.format(prg['programme__code'], prg['programme__name']))
        return result

    def prepare_programme_name_auto(self, obj):
        return ' '.join(self.prepare_programme_name(obj))

    def prepare_project_name(self, obj):
        return list(obj.roles.filter(
            is_programme=False, project__isnull=False
        ).values_list(
            'project__name', flat=True
        ).distinct())

    def prepare_project_name_auto(self, obj):
        return ' '.join(self.prepare_project_name(obj))

    def prepare_role_ss(self, obj):
        # skip Donor States
        roles = list(
            obj.role.exclude(
                code='DS',
            ).values_list(
                'role', flat=True
            ).distinct())
        if len(roles) == 0:
            raise exceptions.SkipDocument
        return roles

    def prepare_geotarget(self, obj):
        # obj.nuts and obj.geotarget can be empty string
        if not obj.nuts:
            if obj.geotarget:
                return [obj.geotarget]
            else:
                return None
        if len(obj.nuts) > 2:
            return ['{}: {}, {}'.format(obj.nuts, obj.geotarget, STATES[obj.nuts[:2]])]
        else:
            return ['{}: {}'.format(obj.nuts, obj.geotarget)]

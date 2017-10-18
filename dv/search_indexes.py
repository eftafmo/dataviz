from functools import reduce

from django.db.models import Q, F
from haystack import indexes
from haystack import exceptions
from django_countries import countries

from dv.models import (
    Organisation,
    Programme,
    Project,
    News)

STATES = dict(countries)


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets
    # some non-DRY code here, but the factor out is not trivial due to common indexes
    # having different model lookup
    state_name = indexes.FacetMultiValueField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()
    financial_mechanism_ss = indexes.FacetMultiValueField()
    outcome_ss = indexes.FacetMultiValueField()
    outcome_ss_auto = indexes.EdgeNgramField()
    programme_name = indexes.FacetMultiValueField()
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
        return (
            self.get_model().objects
            .filter(is_tap=False)
            .prefetch_related(
                'outcomes',
                'outcomes__state',
                'programme_areas',
                'programme_areas__priority_sector',
            )
        )

    def prepare_kind(self, obj):
        return 'Programme'

    def prepare_state_name(self, obj):
        # Get this from ProgrammeOutcome, because of IN22
        return list(set([outcome['state_name'] for outcome in self.programme_outcomes]))

    def prepare_programme_name(self, obj):
        return ['{}: {}'.format(obj.code, obj.name.strip())]

    def prepare_programme_area_ss(self, obj):
        return list(set([area['name'] for area in self.programme_areas]))

    def prepare_priority_sector_ss(self, obj):
        return list(set([area['sector'] for area in self.programme_areas]))

    def prepare_financial_mechanism_ss(self, obj):
        return list(set([area['mechanism'] for area in self.programme_areas]))

    def prepare_outcome_ss(self, obj):
        outcomes = [
            outcome['outcome_name'].strip()
            for outcome in self.programme_outcomes
        ]
        return [o.strip() for o in outcomes]

    def prepare_grant(self, obj):
        return obj.allocation_eea + obj.allocation_norway

    def prepare(self, obj):
        self.programme_outcomes = (
            obj.outcomes
            .exclude(
                outcome__fixed_budget_line=True
            ).annotate(
                outcome_name=F('outcome__name'),
                state_name=F('state__name'),
            )
            .values('outcome_name', 'state_name')
        )

        self.programme_areas = (
            obj.programme_areas
            .annotate(
                mechanism=F('financial_mechanism__grant_name'),
                sector=F('priority_sector__name'),
            )
            .values('mechanism', 'name', 'sector')
        )

        self.prepared_data = super().prepare(obj)
        self.prepared_data['outcome_ss_auto'] = (
            ' '.join(self.prepared_data['outcome_ss'])
            if self.prepared_data['outcome_ss'] else None
        )
        return self.prepared_data


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets
    state_name = indexes.FacetMultiValueField()
    financial_mechanism_ss = indexes.FacetMultiValueField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()
    programme_name = indexes.FacetMultiValueField()
    programme_status = indexes.FacetMultiValueField()
    outcome_ss = indexes.FacetMultiValueField()
    outcome_ss_auto = indexes.EdgeNgramField()

    kind = indexes.FacetCharField()

    # specific facets
    project_status = indexes.FacetMultiValueField(model_attr='status')
    geotarget = indexes.FacetCharField(model_attr='geotarget')
    geotarget_auto = indexes.EdgeNgramField(model_attr='geotarget')
    theme_ss = indexes.FacetMultiValueField()

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)

    # extra data; avoid db hit
    url = indexes.CharField(model_attr='url', indexed=False, null=True)
    name = indexes.CharField(model_attr='name', indexed=False)
    code = indexes.FacetCharField(model_attr='code')
    grant = indexes.DecimalField(model_attr='allocation')

    def index_queryset(self, using=None):
        return (
            self.get_model().objects
            .select_related(
                'financial_mechanism',
                'outcome',
                'programme',
                'programme_area',
                'programme_area__priority_sector',
                'state',
            )
           .prefetch_related('themes')
        )

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
        return ['{}: {}'.format(obj.programme.code, obj.programme.name.strip())]

    def prepare_outcome_ss(self, obj):
        return [obj.outcome.name.strip()]

    def prepare_geotarget(self, obj):
        if len(obj.nuts) > 2:
            return ['{}: {}, {}'.format(obj.nuts, obj.geotarget, STATES[obj.nuts[:2]])]
        else:
            return ['{}: {}'.format(obj.nuts, obj.geotarget)]

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        self.prepared_data['outcome_ss_auto'] = (
            ' '.join(self.prepared_data['outcome_ss'])
                     if self.prepared_data['outcome_ss'] else None
            )
        self.prepared_data['geotarget_auto'] = (
            ' '.join(self.prepared_data['geotarget'])
            if self.prepared_data['geotarget'] else None
        )
        return self.prepared_data


class OrganisationIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets
    # This should be *_ss for this model, but we want the same name across
    # indexes for this logical entity

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
    project_status = indexes.FacetMultiValueField()
    org_type_category = indexes.FacetCharField(model_attr='orgtype__category')
    org_type = indexes.FacetCharField(model_attr='orgtype__name')
    country = indexes.FacetCharField(model_attr='country')
    city = indexes.FacetCharField(model_attr='city')
    city_auto = indexes.EdgeNgramField(model_attr='city')
    geotarget = indexes.FacetCharField(null=True)
    geotarget_auto = indexes.EdgeNgramField(null=True)
    role_ss = indexes.FacetMultiValueField()
    role_max_priority_code = indexes.IntegerField()

    # extra data; avoid db hit
    name = indexes.CharField(model_attr='name', indexed=False)
    domestic_name = indexes.CharField(model_attr='domestic_name', indexed=False, null=True)

    # Highest number = max priority for role. Others default to priority 0.
    ROLE_PRIORITIES = {
        'National Focal Point': 7,  # NFP
        'Programme Operator': 6,  # PO
        'Donor Programme Partner': 5,  # DPP
        'Donor Project Partner': 4,  # PJDPP
        'Programme Partner': 3,  # PP
        'Project Partner': 2,  # PJPP
        'Project Promoter': 1,  # PJPT
    }

    def index_queryset(self, using=None):
        return (
            self.get_model().objects
            .select_related('orgtype')
            .prefetch_related('roles')
        )

    def get_model(self):
        return Organisation

    def prepare_kind(self, obj):
        return 'Organisation'

    def prepare_financial_mechanism_ss(self, obj):
        return [area['mechanism'] for area in self.programme_areas]

    def prepare_state_name(self, obj):
        result = set()
        result = result.union([project['state'] for project in self.projects])
        result = result.union([programme['state'] for programme in self.programmes])
        return list(result)

    def prepare_programme_status(self, obj):
        return [programme['status'] for programme in self.programmes]

    def prepare_project_status(self, obj):
        return [project['status'] for project in self.projects]

    def prepare_programme_area_ss(self, obj):
        return [area['name'] for area in self.programme_areas]

    def prepare_priority_sector_ss(self, obj):
        return [area['sector'] for area in self.programme_areas]

    def prepare_programme_name(self, obj):
        return [
            '{}: {}'.format(programme['code'], programme['name'].strip())
            for programme in self.programmes
        ]

    def prepare_project_name(self, obj):
        return [
            '{}: {}'.format(project['code'], project['name'])
            for project in self.projects
        ]

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

    def prepare(self, obj):
        self.projects = (
            obj.roles
            .filter(is_programme=False, project__isnull=False)
            .annotate(
                code=F('project__code'),
                name=F('project__name'),
                state=F('project__state__name'),
                status=F('project__status'),
            )
            .values('code', 'name', 'state', 'status')
            .distinct()
        )

        self.programmes = list()
        # organisations can be involved directly in a programme
        self.programmes += list(
            obj.roles
            .filter(is_programme=True, programme__isnull=False)
            .annotate(
                code=F('programme__code'),
                name=F('programme__name'),
                state=F('programme__outcomes__state__name'),
                status=F('programme__status'),
            )
            .values('code', 'name', 'state', 'status')
            .distinct()
        )
        # or in a project related to a programme
        self.programmes += list(
            obj.roles.filter(is_programme=False, project__isnull=False)
            .annotate(
                code=F('project__programme__code'),
                name=F('project__programme__name'),
                state=F('project__programme__state__name'),
                status=F('project__programme__status'),
            )
            .values('code', 'name', 'state', 'status')
            .distinct()
        )
        self.programmes = [
            item for item in {v['code']:v for v in self.programmes}.values()
        ]

        self.programme_areas = list()
        # organisations can be involved in a programme area by participating in a
        # programme in that area
        self.programme_areas += list(
            obj.roles
            .filter(is_programme=True, programme__isnull=False,
                    programme__programme_areas__is_not_ta=True)
            .annotate(
                code=F('programme__programme_areas__code'),
                mechanism=F(
                    'programme__programme_areas__financial_mechanism__grant_name'),
                name=F('programme__programme_areas__name'),
                sector=F('programme__programme_areas__priority_sector__name'),
            )
            .values('code', 'mechanism', 'name', 'sector')
            .distinct()
        )
        # or by participating in a project in that area
        self.programme_areas += list(
            obj.roles
            .filter(is_programme=False, project__isnull=False,
                    project__programme_area__is_not_ta=True)
            .annotate(
                code=F('project__programme_area__code'),
                mechanism=F('project__programme_area__financial_mechanism__grant_name'),
                name=F('project__programme_area__name'),
                sector=F('project__programme_area__priority_sector__name'),
            )
            .values('code', 'mechanism', 'name', 'sector')
            .distinct()
        )
        self.programme_areas = [
            item for item in {v['code']:v for v in self.programme_areas}.values()
        ]

        self.prepared_data = super().prepare(obj)

        self.prepared_data['programme_name_auto'] = (
            ' '.join(self.prepared_data['programme_name'])
            if self.prepared_data['programme_name'] else None
        )
        self.prepared_data['project_name_auto'] = (
            ' '.join(self.prepared_data['project_name'])
            if self.prepared_data['project_name'] else None
        )
        self.prepared_data['geotarget_auto'] = (
            ' '.join(self.prepared_data['geotarget'])
            if self.prepared_data['geotarget'] else None
        )

        if self.prepared_data['role_ss']:
            self.prepared_data['role_max_priority_code'] = reduce(
                lambda max_value, role:
                    max(max_value, self.ROLE_PRIORITIES.get(role, 0)),
                self.prepared_data['role_ss'],
                0)
        else:
            self.prepared_data['role_max_priority_code'] = None
        return self.prepared_data


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets;
    state_name = indexes.FacetMultiValueField()
    financial_mechanism_ss = indexes.FacetMultiValueField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()
    programme_name = indexes.FacetMultiValueField()
    programme_status = indexes.FacetMultiValueField()
    outcome_ss = indexes.FacetMultiValueField()

    kind = indexes.FacetCharField()

    # specific facets
    project_name = indexes.FacetMultiValueField()
    project_status = indexes.FacetMultiValueField()
    geotarget = indexes.FacetCharField()
    geotarget_auto = indexes.EdgeNgramField()
    theme_ss = indexes.FacetMultiValueField()

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)

    # extra data; avoid db hit
    name = indexes.CharField(model_attr='title', indexed=False)
    url = indexes.CharField(model_attr='link', indexed=False)
    image = indexes.CharField(model_attr='image', indexed=False)
    created_dt = indexes.DateTimeField(model_attr='created', indexed=False, null=True)

    def get_model(self):
        return News

    def prepare_kind(self, obj):
        return 'News'

    def index_queryset(self, using=None):
        return (
            self.get_model().objects
            .select_related(
                'project',
                'project__financial_mechanism',
                'project__outcome',
                'project__programme',
                'project__programme_area',
                'project__programme_area__priority_sector',
                'project__state',
            )
            .prefetch_related('programmes', 'project__themes')
        )

    def prepare_state_name(self, obj):
        if self.project:
            return [self.project.state.name]
        elif self.programmes:
            # Get this from ProgrammeOutcome, because of IN22
            return list(set([
                state
                for programme in self.programmes
                for state in programme['states']
            ]))
        return None

    def prepare_financial_mechanism_ss(self, obj):
        if self.project:
            return [self.project.financial_mechanism.grant_name]
        if self.programmes:
            return set(list([
                mechanism
                for programme in self.programmes
                for mechanism in programme['mechanisms']
            ]))
        return None

    def prepare_programme_area_ss(self, obj):
        if self.project:
            return [self.project.programme_area.name]
        if self.programmes:
            return list(set([
                area
                for programme in self.programmes
                for area in programme['areas']
            ]))
        return None

    def prepare_priority_sector_ss(self, obj):
        if self.project:
            return [self.project.programme_area.priority_sector.name]
        if self.programmes.exists():
            return list(set([
                sector
                for programme in self.programmes
                for sector in programme['sectors']
            ]))
        return None

    def prepare_programme_name(self, obj):
        if self.project:
            return ['{}: {}'.format(self.project.programme.code,
                                    self.project.programme.name)]
        if self.programmes:
            return ['{}: {}'.format(programme['code'], programme['name'])
                    for programme in self.programmes]
        return None

    def prepare_project_name(self, obj):
        if self.project:
            return ['{}: {}'.format(self.project.code, self.project.name)]
        return None

    def prepare_programme_status(self, obj):
        if self.project:
            return [self.project.programme.status]
        if self.programmes:
            return list(set([programme['status'] for programme in self.programmes]))
        return None

    def prepare_outcome_ss(self, obj):
        if self.project:
            return [self.project.outcome.name.strip()]
        if self.programmes.exists():
            return set([
                outcome
                for programme in self.programmes
                for outcome in programme['outcome_names']
            ])
        return None

    def prepare_project_status(self, obj):
        if self.project:
            return [self.project.status]
        return None

    def prepare_geotarget(self, obj):
        if self.project:
            if len(self.project.nuts) > 2:
                return ['{}: {}, {}'.format(self.project.nuts, self.project.geotarget,
                                            STATES[self.project.nuts[:2]])]
            else:
                return ['{}: {}'.format(self.project.nuts, self.project.geotarget)]
        return None

    def prepare_theme_ss(self, obj):
        if self.project:
            return list(set([theme.name for theme in self.project.themes.all()]))
        return None

    def prepare(self, obj):
        self.project = None
        self.programmes = list()
        try:
            if obj.project:
                self.project = obj.project
        except Project.DoesNotExist:
            pass
        if obj.programmes.exists():
            self.programmes = (
                obj.programmes
                .annotate(
                    areas=F('programme_areas__name'),
                    mechanisms=F('programme_areas__financial_mechanism__grant_name'),
                    outcome_names=F('outcomes__outcome__name'),
                    sectors=F('programme_areas__priority_sector__name'),
                    states=F('outcomes__state__name')
                )
                .values('areas', 'code', 'mechanisms', 'name', 'outcome_names',
                        'sectors', 'states', 'status')
            )
        self.prepared_data = super().prepare(obj)
        self.prepared_data['geotarget_auto'] = (
            ' '.join(self.prepared_data['geotarget'])
            if self.prepared_data['geotarget'] else None
        )
        return self.prepared_data

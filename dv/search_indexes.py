from collections import defaultdict
from functools import reduce

from django.db.models import F
from haystack import indexes
from haystack import exceptions
from django_countries import countries

from dv.models import (
    Organisation,
    OrganisationRole,
    Programme,
    ProgrammeOutcome,
    Project,
    News,
)

STATES = dict(countries)


class ProgrammeIndex(indexes.SearchIndex, indexes.Indexable):
    # common facets
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
    code = indexes.FacetCharField(model_attr='code')

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    url = indexes.CharField(model_attr='url', indexed=False, null=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)
    name = indexes.CharField(model_attr='name', indexed=False)
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
    state_name = indexes.FacetMultiValueField(model_attr='state__name')
    financial_mechanism_ss = indexes.FacetMultiValueField()
    programme_area_ss = indexes.FacetMultiValueField()
    priority_sector_ss = indexes.FacetMultiValueField()
    programme_name = indexes.FacetMultiValueField()
    programme_status = indexes.FacetMultiValueField(model_attr='programme__status')
    outcome_ss = indexes.FacetMultiValueField()
    outcome_ss_auto = indexes.EdgeNgramField()

    kind = indexes.FacetCharField()

    # specific facets
    code = indexes.FacetCharField(model_attr='code')
    project_status = indexes.FacetMultiValueField(model_attr='status')
    geotarget = indexes.FacetCharField(model_attr='geotarget')
    geotarget_auto = indexes.EdgeNgramField(model_attr='geotarget')
    theme_ss = indexes.FacetMultiValueField()

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)
    url = indexes.CharField(model_attr='url', indexed=False, null=True)
    name = indexes.CharField(model_attr='name', indexed=False)
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
            ).prefetch_related('themes')
            # using prefetch_related may require --batch-size 999 to avoid
            # sqlite3.OperationalError: too many SQL variables
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

    def prepare_theme_ss(self, obj):
        return list(set([theme.name for theme in obj.themes.all()]))

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
    org_type_category = indexes.FacetCharField(model_attr='orgtypecateg')
    org_type = indexes.FacetCharField(model_attr='orgtype')
    country = indexes.FacetCharField(model_attr='country')
    city = indexes.FacetCharField(model_attr='city')
    city_auto = indexes.EdgeNgramField(model_attr='city')
    geotarget = indexes.FacetCharField(null=True)
    geotarget_auto = indexes.EdgeNgramField(null=True)
    role_ss = indexes.FacetMultiValueField()
    role_max_priority_code = indexes.IntegerField()

    # extra data; avoid db hit
    org_name = indexes.FacetCharField(model_attr='name')
    org_name_auto = indexes.EdgeNgramField()
    domestic_name = indexes.CharField(model_attr='domestic_name', null=True)

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

    # Caches, lazy init
    ALL_PROGRAMMES = {}
    ALL_PROJECTS = {}
    ALL_ROLES = {}

    def __init__(self):
        super().__init__()
        if not self.ALL_PROGRAMMES:
            OrganisationIndex.init_caches()

    @classmethod
    def init_caches(cls):
        # Cache programmes
        _fields = {
            'prg_code': F('programme__code'),
            'prg_name': F('programme__name'),
            'area': F('outcome__programme_area__name'),
            'sector': F('outcome__programme_area__priority_sector__name'),
            'fm': F('outcome__programme_area__financial_mechanism__grant_name'),
            'state_name': F('state__name'),
            'status': F('programme__status'),
        }
        _all_programmes_raw = (
            ProgrammeOutcome.objects.all().select_related(
                'programme',
                'outcome',
                'outcome__programe_area__financial_mechanism',
                'outcome__programe_area__priority_sector',
                'outcome__programe_area',
                'state',
            ).exclude(programme__isnull=True)
            .exclude(programme__is_tap=True)
            .annotate(**_fields)
            .values(*_fields.keys())
            .distinct()
        )
        ALL_PROGRAMMES = defaultdict(lambda: {
            'fms': set(),
            'sectors': set(),
            'areas': set(),
            'states': set(),
        })
        for prg in _all_programmes_raw:
            ALL_PROGRAMMES[prg['prg_code']]['name'] = prg['prg_name'].strip()
            ALL_PROGRAMMES[prg['prg_code']]['fms'].add(prg['fm'])
            ALL_PROGRAMMES[prg['prg_code']]['sectors'].add(prg['sector'])
            ALL_PROGRAMMES[prg['prg_code']]['areas'].add(prg['area'])
            ALL_PROGRAMMES[prg['prg_code']]['states'].add(prg['state_name'])
            ALL_PROGRAMMES[prg['prg_code']]['status'] = prg['status']

        cls.ALL_PROGRAMMES = ALL_PROGRAMMES

        # Cache projects
        _fields = {
            'prj_code': F('code'),
            'prj_name': F('name'),
            'prg_code': F('programme_id'),
            'area': F('programme_area__name'),
            'sector': F('priority_sector__name'),
            'fm': F('financial_mechanism__grant_name'),
            'state_name': F('state__name'),
            'prj_status': F('status'),
        }
        _all_projects_raw = (
            Project.objects.all().select_related(
                'financial_mechanism',
                'priority_sector',
                'programe_area',
                'state',
            ).annotate(**_fields)
            .values(*_fields.keys())
        )
        cls.ALL_PROJECTS = {
            prj['prj_code']: prj
            for prj in _all_projects_raw
        }

        cls.ALL_ROLES = {
            x.code: x.role for x in OrganisationRole.objects.all()
        }

    def index_queryset(self, using=None):
        return (
            self.get_model().objects
            .prefetch_related('roles')
        )

    def get_model(self):
        return Organisation

    def prepare_kind(self, obj):
        return 'Organisation'

    def prepare_financial_mechanism_ss(self, obj):
        fm = [
            self.ALL_PROJECTS[prj]['fm']
            for prj in self.projects
        ]
        for prg in self.programmes:
            fm += list(self.ALL_PROGRAMMES[prg]['fms'])
        return list(set(fm))

    def prepare_state_name(self, obj):
        # programme IN22 can have multiple states
        states = [
            self.ALL_PROJECTS[prj]['state_name']
            for prj in self.projects
        ]
        for prg in self.programmes:
            states += list(self.ALL_PROGRAMMES[prg]['states'])
        return list(set(states))

    def prepare_programme_status(self, obj):
        statuses = [
            self.ALL_PROGRAMMES[programme]['status']
            for programme in self.programmes
        ]
        # Add programme status from projects also
        statuses += [
            self.ALL_PROGRAMMES[
                self.ALL_PROJECTS[prj_code]['prg_code']
            ]['status']
            for prj_code in self.projects
        ]
        return list(set(statuses))

    def prepare_project_status(self, obj):
        return list(set([
            self.ALL_PROJECTS[project_code]['prj_status']
            for project_code in self.projects
        ]))

    def prepare_programme_area_ss(self, obj):
        areas = [
            self.ALL_PROJECTS[prj]['area']
            for prj in self.projects
        ]
        for prg in self.programmes:
            areas += list(self.ALL_PROGRAMMES[prg]['areas'])
        return list(set(areas))

    def prepare_priority_sector_ss(self, obj):
        sectors = [
            self.ALL_PROJECTS[prj]['sector']
            for prj in self.projects
        ]
        for prg in self.programmes:
            sectors += list(self.ALL_PROGRAMMES[prg]['sectors'])
        return list(set(sectors))

    def prepare_programme_name(self, obj):
        prg_codes = list(self.programmes)
        prg_codes += [
            self.ALL_PROJECTS[project_code]['prg_code']
            for project_code in self.projects
        ]
        return [
            '{}: {}'.format(
                prg_code,
                self.ALL_PROGRAMMES[prg_code]['name']
            )
            for prg_code in set(prg_codes)
        ]

    def prepare_project_name(self, obj):
        return [
            '{}: {}'.format(
                project_code,
                self.ALL_PROJECTS[project_code]['prj_name']
            )
            for project_code in self.projects
        ]

    def prepare_role_ss(self, obj):
        return [
            self.ALL_ROLES[role_code]
            for role_code in self.roles
        ]

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
        self.projects = list()
        self.programmes = list()
        self.roles = set()
        for role in obj.roles.all():
            if role.project_id and self.ALL_PROJECTS[role.project_id].get('prj_code'):
                # check prj_code because self.ALL_PROJECTS is defaultdict
                self.projects.append(role.project_id)
            elif role.programme_id and self.ALL_PROGRAMMES[role.programme_id].get('name'):
                # check programme name because self.ALL_PROGRAMMES is defaultdict
                self.programmes.append(role.programme_id)
            if role.organisation_role_id != 'DS' and (role.project_id or role.programme_id):
                # Skip donor states and organisations with no project nor programme
                self.roles.add(role.organisation_role_id)
        if len(self.roles) == 0:
            raise exceptions.SkipDocument
        self.prepared_data = super().prepare(obj)

        # Add extra data in text field to avoid extra queries in template
        self.prepared_data['text'] += ' '.join(
            self.prepared_data['state_name'] +
            self.prepared_data['programme_name'] +
            self.prepared_data['project_name']
        )

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
        self.prepared_data['org_name_auto'] = self.prepared_data['org_name']

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
    project_name_auto = indexes.EdgeNgramField()
    project_status = indexes.FacetMultiValueField()
    geotarget = indexes.FacetCharField()
    geotarget_auto = indexes.EdgeNgramField()
    theme_ss = indexes.FacetMultiValueField()

    # specific fields
    text = indexes.CharField(document=True, use_template=True)
    summary = indexes.CharField(model_attr='summary', indexed=False)
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
            .prefetch_related('programmes', 'programmes__outcomes', 'project__themes')
        )

    def prepare_state_name(self, obj):
        if self.project:
            return [self.project.state.name]
        elif self.programmes:
            # Get this from ProgrammeOutcome, because of IN22
            return list(set([
                programme['country']
                for programme in self.programmes
            ]))
        return None

    def prepare_financial_mechanism_ss(self, obj):
        if self.project:
            return [self.project.financial_mechanism.grant_name]
        if self.programmes:
            return list(set([
                programme['mechanism']
                for programme in self.programmes
            ]))
        return None

    def prepare_programme_area_ss(self, obj):
        if self.project:
            return [self.project.programme_area.name]
        if self.programmes:
            return list(set([
                programme['area']
                for programme in self.programmes
            ]))
        return None

    def prepare_priority_sector_ss(self, obj):
        if self.project:
            return [self.project.programme_area.priority_sector.name]
        if self.programmes.exists():
            return list(set([
                programme['sector']
                for programme in self.programmes
            ]))
        return None

    def prepare_programme_name(self, obj):
        if self.project:
            return ['{}: {}'.format(self.project.programme.code,
                                    self.project.programme.name)]
        if self.programmes:
            return list(set([
                '{}: {}'.format(programme['code'], programme['name'])
                for programme in self.programmes
            ]))
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
            return list(set([
                programme['outcome_name']
                for programme in self.programmes
                if not programme['outcome_fbl']
            ]))
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
                    area=F('programme_areas__name'),
                    mechanism=F('programme_areas__financial_mechanism__grant_name'),
                    outcome_name=F('outcomes__outcome__name'),
                    outcome_fbl=F('outcomes__outcome__fixed_budget_line'),
                    sector=F('programme_areas__priority_sector__name'),
                    country=F('outcomes__state__name')
                )
                .values('area', 'code', 'mechanism', 'name',
                        'outcome_name', 'outcome_fbl',
                        'sector', 'country', 'status')
            )
        self.prepared_data = super().prepare(obj)
        self.prepared_data['geotarget_auto'] = (
            ' '.join(self.prepared_data['geotarget'])
            if self.prepared_data['geotarget'] else None
        )
        self.prepared_data['project_name_auto'] = (
            ' '.join(self.prepared_data['project_name'])
            if self.prepared_data['project_name'] else None
        )
        return self.prepared_data

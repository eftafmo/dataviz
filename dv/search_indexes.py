from collections import defaultdict
from functools import reduce

from django.db.models import F
from haystack.indexes import SearchIndex, Indexable
from haystack import fields
from haystack import exceptions
from django_countries import countries

from dv.models import FINANCIAL_MECHANISMS_DICT
from dv.models import (
    OrganisationRole,
    Programme,
    Project,
    News,
)

STATES = dict(countries)


class ProgrammeIndex(SearchIndex, Indexable):
    # common facets
    period = fields.FacetCharField()
    state_name = fields.FacetMultiValueField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()
    financial_mechanism_ss = fields.FacetMultiValueField()
    outcome_ss = fields.FacetMultiValueField()
    outcome_ss_auto = fields.EdgeNgramField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField(model_attr="status")

    kind = fields.FacetCharField()

    # specific facets
    code = fields.FacetCharField(model_attr="code")

    # specific fields
    text = fields.CharField(document=True, use_template=True)
    url = fields.CharField(model_attr="url", indexed=False, null=True)
    summary = fields.CharField(model_attr="summary", indexed=False)
    name = fields.CharField(model_attr="name", indexed=False)
    grant = fields.DecimalField()

    def get_model(self):
        return Programme

    def index_queryset(self, using=None):
        return (
            self.get_model()
            .objects.filter(is_tap=False, is_bfp=False)
            .prefetch_related(
                "indicators",
                "indicators__state",
                "states",
                "programme_areas",
                "programme_areas__priority_sector",
            )
        )

    def indicators_query(self, obj):
        return obj.indicators.all()

    def programme_area_query(self, obj):
        return obj.programme_areas.all()

    def prepare_kind(self, obj):
        return "Programme"

    def prepare_period(self, obj):
        return obj.get_funding_period_display()

    def prepare_state_name(self, obj):
        # Get this from ProgrammeOutcome, because of IN22
        return list(
            set(indicator.state.name for indicator in self.indicators_query(obj)).union(
                state.name for state in obj.states.all()
            )
        )

    def prepare_programme_name(self, obj):
        return ["{}: {}".format(obj.code, " ".join(obj.name.split()))]

    def prepare_programme_area_ss(self, obj):
        return list(set([area.name for area in self.programme_area_query(obj)]))

    def prepare_priority_sector_ss(self, obj):
        return list(
            set([area.priority_sector.name for area in self.programme_area_query(obj)])
        )

    def prepare_financial_mechanism_ss(self, obj):
        fms = []
        if obj.is_eea:
            fms.append(FINANCIAL_MECHANISMS_DICT["EEA"])
        if obj.is_norway:
            fms.append(FINANCIAL_MECHANISMS_DICT["NOR"])
        return fms

    def prepare_outcome_ss(self, obj):
        return list(
            set(
                " ".join(indicator.header.split()) for indicator in obj.indicators.all()
            )
        )

    def prepare_grant(self, obj):
        return obj.allocation_eea + obj.allocation_norway

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        self.prepared_data["outcome_ss_auto"] = (
            " ".join(self.prepared_data["outcome_ss"])
            if self.prepared_data["outcome_ss"]
            else None
        )
        return self.prepared_data


class ProjectIndex(SearchIndex, Indexable):
    # common facets
    period = fields.FacetCharField()
    state_name = fields.FacetMultiValueField(model_attr="state__name")
    financial_mechanism_ss = fields.FacetMultiValueField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField(model_attr="programme__status")
    outcome_ss = fields.FacetMultiValueField()
    outcome_ss_auto = fields.EdgeNgramField()

    kind = fields.FacetCharField()

    # specific facets
    code = fields.FacetCharField(model_attr="code")
    project_status = fields.FacetMultiValueField(model_attr="status")
    geotarget = fields.FacetCharField()
    geotarget_auto = fields.EdgeNgramField()
    theme_ss = fields.FacetMultiValueField()

    # specific fields
    text = fields.CharField(document=True, use_template=True)
    url = fields.CharField(model_attr="url", indexed=False, null=True)
    name = fields.CharField(model_attr="name", indexed=False)
    grant = fields.DecimalField(model_attr="allocation")

    def get_model(self):
        return Project

    def index_queryset(self, using=None):
        return (
            self.get_model()
            .objects.select_related(
                "programme",
                "state",
                "nuts",
            )
            .prefetch_related(
                "themes",
                "programme_areas",
                "priority_sectors",
            )
            # using prefetch_related may require --batch-size 999 to avoid
            # sqlite3.OperationalError: too many SQL variables
        )

    def programme_area_query(self, obj):
        return obj.programme_areas.all()

    def priority_sector_query(self, obj):
        return obj.priority_sectors.all()

    def themes_query(self, obj):
        return obj.themes.all()

    def prepare_kind(self, obj):
        return "Project"

    def prepare_period(self, obj):
        return obj.get_funding_period_display()

    def prepare_financial_mechanism_ss(self, obj):
        return [FINANCIAL_MECHANISMS_DICT[fmId] for fmId in obj.financial_mechanisms]

    def prepare_programme_area_ss(self, obj):
        return [area.name for area in self.programme_area_query(obj)]

    def prepare_priority_sector_ss(self, obj):
        return [sector.name for sector in self.priority_sector_query(obj)]

    def prepare_programme_name(self, obj):
        return [
            "{}: {}".format(obj.programme.code, " ".join(obj.programme.name.split()))
        ]

    def prepare_outcome_ss(self, obj):
        return list(
            set(
                " ".join(indicator.header.split())
                for indicator in obj.programme.indicators.all()
            )
        )

    def prepare_geotarget(self, obj):
        if not obj.nuts:
            return []
        elif len(obj.nuts.code) > 2:
            return ["{}: {}, {}".format(obj.nuts.code, obj.nuts.label, obj.state.name)]
        else:
            return ["{}: {}".format(obj.nuts.code, obj.nuts.label)]

    def prepare_theme_ss(self, obj):
        return list(set(theme.name for theme in self.themes_query(obj)))

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        self.prepared_data["outcome_ss_auto"] = (
            " ".join(self.prepared_data["outcome_ss"])
            if self.prepared_data["outcome_ss"]
            else None
        )
        self.prepared_data["geotarget_auto"] = (
            " ".join(self.prepared_data["geotarget"])
            if self.prepared_data["geotarget"]
            else None
        )
        return self.prepared_data


# class OrganisationIndex(SearchIndex, Indexable):
#     # common facets
#     state_name = fields.FacetMultiValueField()
#     programme_status = fields.FacetMultiValueField()
#     financial_mechanism_ss = fields.FacetMultiValueField()
#     programme_name = fields.FacetMultiValueField()
#     programme_name_auto = fields.EdgeNgramField()
#     project_name = fields.FacetMultiValueField()
#     project_name_auto = fields.EdgeNgramField()
#     programme_area_ss = fields.FacetMultiValueField()
#     priority_sector_ss = fields.FacetMultiValueField()
#
#     text = fields.CharField(document=True, use_template=True)
#
#     kind = fields.FacetCharField()
#
#     # specific facets
#     project_status = fields.FacetMultiValueField()
#     org_type_category = fields.FacetCharField(model_attr='orgtypecateg')
#     org_type = fields.FacetCharField(model_attr='orgtype')
#     country = fields.FacetCharField(model_attr='country')
#     city = fields.FacetCharField(model_attr='city')
#     city_auto = fields.EdgeNgramField(model_attr='city')
#     geotarget = fields.FacetCharField(null=True)
#     geotarget_auto = fields.EdgeNgramField(null=True)
#     role_ss = fields.FacetMultiValueField()
#     role_max_priority_code = fields.IntegerField()
#
#     # extra data; avoid db hit
#     org_name = fields.FacetCharField()
#     org_name_auto = fields.EdgeNgramField()
#     domestic_name = fields.CharField(model_attr='domestic_name', null=True)
#
#     # Highest number = max priority for role. Others default to priority 0.
#     ROLE_PRIORITIES = {
#         'National Focal Point': 7,  # NFP
#         'Programme Operator': 6,  # PO
#         'Donor Programme Partner': 5,  # DPP
#         'Donor Project Partner': 4,  # PJDPP
#         'Programme Partner': 3,  # PP
#         'Project Partner': 2,  # PJPP
#         'Project Promoter': 1,  # PJPT
#     }
#
#     # Caches, lazy init
#     ALL_PROGRAMMES = {}
#     ALL_PROJECTS = {}
#     ALL_ROLES = {}
#
#     def __init__(self):
#         super().__init__()
#         if not self.ALL_PROGRAMMES:
#             OrganisationIndex.init_caches()
#
#     @classmethod
#     def init_caches(cls):
#         return
#         # Cache programmes
#         _fields = {
#             'prg_code': F('programme__code'),
#             'prg_name': F('programme__name'),
#             'area': F('outcome__programme_area__name'),
#             'sector': F('outcome__programme_area__priority_sector__name'),
#             'fm': F('outcome__programme_area__financial_mechanism__grant_name'),
#             'state_name': F('state__name'),
#             'status': F('programme__status'),
#         }
#         _all_programmes_raw = (
#             # ProgrammeOutcome.objects.all().select_related(
#             #     'programme',
#             #     'outcome',
#             #     'outcome__programme_area__financial_mechanism',
#             #     'outcome__programme_area__priority_sector',
#             #     'outcome__programme_area',
#             #     'state',
#             # ).exclude(programme__isnull=True)
#             # .exclude(programme__is_tap=True)
#             # .annotate(**_fields)
#             # .values(*_fields.keys())
#             # .distinct()
#         )
#         ALL_PROGRAMMES = defaultdict(lambda: {
#             'fms': set(),
#             'sectors': set(),
#             'areas': set(),
#             'states': set(),
#         })
#         for prg in _all_programmes_raw:
#             ALL_PROGRAMMES[prg['prg_code']]['name'] = prg['prg_name'].strip()
#             ALL_PROGRAMMES[prg['prg_code']]['fms'].add(prg['fm'])
#             ALL_PROGRAMMES[prg['prg_code']]['sectors'].add(prg['sector'])
#             ALL_PROGRAMMES[prg['prg_code']]['areas'].add(prg['area'])
#             ALL_PROGRAMMES[prg['prg_code']]['states'].add(prg['state_name'])
#             ALL_PROGRAMMES[prg['prg_code']]['status'] = prg['status']
#
#         cls.ALL_PROGRAMMES = ALL_PROGRAMMES
#
#         # Cache projects
#         _fields = {
#             'prj_code': F('code'),
#             'prj_name': F('name'),
#             'prg_code': F('programme_id'),
#             'area': F('programme_area__name'),
#             'sector': F('priority_sector__name'),
#             'fm': F('financial_mechanism__grant_name'),
#             'state_name': F('state__name'),
#             'prj_status': F('status'),
#         }
#         _all_projects_raw = (
#             Project.objects.all().select_related(
#                 'financial_mechanism',
#                 'priority_sector',
#                 'programme_area',
#                 'state',
#             ).annotate(**_fields)
#             .values(*_fields.keys())
#         )
#         cls.ALL_PROJECTS = {
#             prj['prj_code']: prj
#             for prj in _all_projects_raw
#         }
#
#         cls.ALL_ROLES = {
#             x.code: x.role for x in OrganisationRole.objects.all()
#         }
#
#     def index_queryset(self, using=None):
#         return (
#             self.get_model().objects
#             .prefetch_related('roles')
#         )
#
#     def get_model(self):
#         return OrganisationRole
#
#     def prepare_kind(self, obj):
#         return 'OrganisationRole'
#
#     def prepare_financial_mechanism_ss(self, obj):
#         fm = [
#             self.ALL_PROJECTS[prj]['fm']
#             for prj in self.projects
#         ]
#         for prg in self.programmes:
#             fm += list(self.ALL_PROGRAMMES[prg]['fms'])
#         return list(set(fm))
#
#     def prepare_state_name(self, obj):
#         # programme IN22 can have multiple states
#         states = [
#             self.ALL_PROJECTS[prj]['state_name']
#             for prj in self.projects
#         ]
#         for prg in self.programmes:
#             states += list(self.ALL_PROGRAMMES[prg]['states'])
#         return list(set(states))
#
#     def prepare_programme_status(self, obj):
#         statuses = [
#             self.ALL_PROGRAMMES[programme]['status']
#             for programme in self.programmes
#         ]
#         # Add programme status from projects also
#         statuses += [
#             self.ALL_PROGRAMMES[
#                 self.ALL_PROJECTS[prj_code]['prg_code']
#             ]['status']
#             for prj_code in self.projects
#         ]
#         return list(set(statuses))
#
#     def prepare_project_status(self, obj):
#         return list(set([
#             self.ALL_PROJECTS[project_code]['prj_status']
#             for project_code in self.projects
#         ]))
#
#     def prepare_programme_area_ss(self, obj):
#         areas = [
#             self.ALL_PROJECTS[prj]['area']
#             for prj in self.projects
#         ]
#         for prg in self.programmes:
#             areas += list(self.ALL_PROGRAMMES[prg]['areas'])
#         return list(set(areas))
#
#     def prepare_priority_sector_ss(self, obj):
#         sectors = [
#             self.ALL_PROJECTS[prj]['sector']
#             for prj in self.projects
#         ]
#         for prg in self.programmes:
#             sectors += list(self.ALL_PROGRAMMES[prg]['sectors'])
#         return list(set(sectors))
#
#     def prepare_programme_name(self, obj):
#         prg_codes = list(self.programmes)
#         prg_codes += [
#             self.ALL_PROJECTS[project_code]['prg_code']
#             for project_code in self.projects
#         ]
#         return [
#             '{}: {}'.format(
#                 prg_code,
#                 ' '.join(self.ALL_PROGRAMMES[prg_code]['name'].split())
#             )
#             for prg_code in set(prg_codes)
#         ]
#
#     def prepare_project_name(self, obj):
#         return [
#             '{}: {}'.format(
#                 project_code,
#                 ' '.join(self.ALL_PROJECTS[project_code]['prj_name'].split())
#             )
#             for project_code in self.projects
#         ]
#
#     def prepare_role_ss(self, obj):
#         return [
#             self.ALL_ROLES[role_code]
#             for role_code in self.roles
#         ]
#
#     def prepare_geotarget(self, obj):
#         # obj.nuts and obj.geotarget can be empty string
#         if not obj.nuts:
#             if obj.geotarget:
#                 return [obj.geotarget]
#             else:
#                 return None
#         if len(obj.nuts) > 2:
#             return ['{}: {}, {}'.format(obj.nuts, obj.geotarget, STATES[obj.nuts[:2]])]
#         else:
#             return ['{}: {}'.format(obj.nuts, obj.geotarget)]
#
#     def prepare_org_name(self, obj):
#         return ' '.join(obj.name.split())
#
#     def prepare(self, obj):
#         self.projects = list()
#         self.programmes = list()
#         self.roles = set()
#         for role in obj.roles.all():
#             if role.project_id and self.ALL_PROJECTS[role.project_id].get('prj_code'):
#                 # check prj_code because self.ALL_PROJECTS is defaultdict
#                 self.projects.append(role.project_id)
#             elif role.programme_id and self.ALL_PROGRAMMES[role.programme_id].get('name'):
#                 # check programme name because self.ALL_PROGRAMMES is defaultdict
#                 self.programmes.append(role.programme_id)
#             if role.organisation_role_id != 'DS' and (role.project_id or role.programme_id):
#                 # Skip donor states and organisations with no project nor programme
#                 self.roles.add(role.organisation_role_id)
#         if len(self.roles) == 0:
#             raise exceptions.SkipDocument
#         self.prepared_data = super().prepare(obj)
#
#         # Add extra data in text field to avoid extra queries in template
#         self.prepared_data['text'] += ' '.join(
#             self.prepared_data['state_name'] +
#             self.prepared_data['programme_name'] +
#             self.prepared_data['project_name']
#         )
#
#         self.prepared_data['programme_name_auto'] = (
#             ' '.join(self.prepared_data['programme_name'])
#             if self.prepared_data['programme_name'] else None
#         )
#         self.prepared_data['project_name_auto'] = (
#             ' '.join(self.prepared_data['project_name'])
#             if self.prepared_data['project_name'] else None
#         )
#         self.prepared_data['geotarget_auto'] = (
#             ' '.join(self.prepared_data['geotarget'])
#             if self.prepared_data['geotarget'] else None
#         )
#         self.prepared_data['org_name_auto'] = self.prepared_data['org_name']
#
#         if self.prepared_data['role_ss']:
#             self.prepared_data['role_max_priority_code'] = reduce(
#                 lambda max_value, role:
#                     max(max_value, self.ROLE_PRIORITIES.get(role, 0)),
#                 self.prepared_data['role_ss'],
#                 0)
#         else:
#             self.prepared_data['role_max_priority_code'] = None
#         return self.prepared_data
#
#
# class NewsIndex(SearchIndex, Indexable):
#     # common facets;
#     state_name = fields.FacetMultiValueField()
#     financial_mechanism_ss = fields.FacetMultiValueField()
#     programme_area_ss = fields.FacetMultiValueField()
#     priority_sector_ss = fields.FacetMultiValueField()
#     programme_name = fields.FacetMultiValueField()
#     programme_status = fields.FacetMultiValueField()
#     outcome_ss = fields.FacetMultiValueField()
#
#     kind = fields.FacetCharField()
#
#     # specific facets
#     project_name = fields.FacetMultiValueField()
#     project_name_auto = fields.EdgeNgramField()
#     project_status = fields.FacetMultiValueField()
#     geotarget = fields.FacetCharField()
#     geotarget_auto = fields.EdgeNgramField()
#     theme_ss = fields.FacetMultiValueField()
#
#     # specific fields
#     text = fields.CharField(document=True, use_template=True)
#     summary = fields.CharField(model_attr='summary', indexed=False)
#     name = fields.CharField(model_attr='title', indexed=False)
#     url = fields.CharField(model_attr='link', indexed=False)
#     image = fields.CharField(model_attr='image', indexed=False)
#     created_dt = fields.DateTimeField(model_attr='created', indexed=False, null=True)
#
#     def get_model(self):
#         return News
#
#     def prepare_kind(self, obj):
#         return 'News'
#
#     def index_queryset(self, using=None):
#         return (
#             self.get_model().objects
#             .select_related(
#                 'project',
#                 'project__financial_mechanism',
#                 'project__outcome',
#                 'project__programme',
#                 'project__programme_area',
#                 'project__programme_area__priority_sector',
#                 'project__state',
#             )
#             .prefetch_related('programmes', 'programmes__outcomes', 'project__themes')
#         )
#
#     def prepare_state_name(self, obj):
#         if self.project:
#             return [self.project.state.name]
#         elif self.programmes:
#             # Get this from ProgrammeOutcome, because of IN22
#             return list(set([
#                 programme['country']
#                 for programme in self.programmes
#             ]))
#         return None
#
#     def prepare_financial_mechanism_ss(self, obj):
#         if self.project:
#             return [self.project.financial_mechanism.grant_name]
#         if self.programmes:
#             return list(set([
#                 programme['mechanism']
#                 for programme in self.programmes
#             ]))
#         return None
#
#     def prepare_programme_area_ss(self, obj):
#         if self.project:
#             return [self.project.programme_area.name]
#         if self.programmes:
#             return list(set([
#                 programme['area']
#                 for programme in self.programmes
#             ]))
#         return None
#
#     def prepare_priority_sector_ss(self, obj):
#         if self.project:
#             return [self.project.programme_area.priority_sector.name]
#         if self.programmes:
#             return list(set([
#                 programme['sector']
#                 for programme in self.programmes
#             ]))
#         return None
#
#     def prepare_programme_name(self, obj):
#         if self.project:
#             return ['{}: {}'.format(self.project.programme.code,
#                                     self.project.programme.name)]
#         if self.programmes:
#             return list(set([
#                 '{}: {}'.format(programme['code'], programme['name'])
#                 for programme in self.programmes
#             ]))
#         return None
#
#     def prepare_project_name(self, obj):
#         if self.project:
#             return ['{}: {}'.format(
#                 self.project.code,
#                 ' '.join(self.project.name.split())
#             )]
#         return None
#
#     def prepare_programme_status(self, obj):
#         if self.project:
#             return [self.project.programme.status]
#         if self.programmes:
#             return list(set([programme['status'] for programme in self.programmes]))
#         return None
#
#     def prepare_outcome_ss(self, obj):
#         if self.project:
#             return [self.project.outcome.name.strip()]
#         if self.programmes:
#             return list(set([
#                 programme['outcome_name']
#                 for programme in self.programmes
#                 if not programme['outcome_fbl']
#             ]))
#         return None
#
#     def prepare_project_status(self, obj):
#         if self.project:
#             return [self.project.status]
#         return None
#
#     def prepare_geotarget(self, obj):
#         if self.project:
#             if len(self.project.nuts) > 2:
#                 return ['{}: {}, {}'.format(self.project.nuts, self.project.geotarget,
#                                             STATES[self.project.nuts[:2]])]
#             else:
#                 return ['{}: {}'.format(self.project.nuts, self.project.geotarget)]
#         return None
#
#     def prepare_theme_ss(self, obj):
#         if self.project:
#             return list(set([theme.name for theme in self.project.themes.all()]))
#         return None
#
#     def prepare(self, obj):
#         self.project = None
#         self.programmes = list()
#         try:
#             if obj.project:
#                 self.project = obj.project
#         except Project.DoesNotExist:
#             pass
#         if obj.programmes:
#             self.programmes = (
#                 obj.programmes
#                 .annotate(
#                     area=F('programme_areas__name'),
#                     mechanism=F('programme_areas__financial_mechanism__grant_name'),
#                     outcome_name=F('outcomes__outcome__name'),
#                     outcome_fbl=F('outcomes__outcome__fixed_budget_line'),
#                     sector=F('programme_areas__priority_sector__name'),
#                     country=F('outcomes__state__name')
#                 )
#                 .values('area', 'code', 'mechanism', 'name',
#                         'outcome_name', 'outcome_fbl',
#                         'sector', 'country', 'status')
#             )
#         self.prepared_data = super().prepare(obj)
#         self.prepared_data['geotarget_auto'] = (
#             ' '.join(self.prepared_data['geotarget'])
#             if self.prepared_data['geotarget'] else None
#         )
#         self.prepared_data['project_name_auto'] = (
#             ' '.join(self.prepared_data['project_name'])
#             if self.prepared_data['project_name'] else None
#         )
#         return self.prepared_data

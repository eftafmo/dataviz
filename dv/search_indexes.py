import itertools
from functools import reduce

from haystack.indexes import SearchIndex, Indexable
from haystack import fields
from haystack import exceptions

from dv.models import News
from dv.models import Project
from dv.models import Programme
from dv.models import Organisation
from dv.models import BilateralInitiative


class BilateralInitiativeIndex(SearchIndex, Indexable):
    # common facets
    period = fields.FacetMultiValueField()
    state_name = fields.FacetMultiValueField()
    financial_mechanism_ss = fields.FacetMultiValueField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField(model_attr="status")
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()

    kind = fields.FacetCharField()

    # specific facets
    code = fields.FacetCharField(model_attr="code")
    project_name = fields.FacetMultiValueField()
    project_name_auto = fields.EdgeNgramField()
    project_status = fields.FacetMultiValueField()
    level = fields.FacetCharField(model_attr="level")
    status = fields.FacetCharField(model_attr="status")
    promoter_state_name = fields.FacetCharField()

    # specific fields
    text = fields.CharField(document=True, use_template=True)
    title = fields.CharField(indexed=False)
    url = fields.CharField(indexed=False, model_attr="url", null=True)
    promoter_organization = fields.CharField(
        indexed=False, model_attr="promoter_organization"
    )
    grant = fields.DecimalField()

    def get_model(self):
        return BilateralInitiative

    def index_queryset(self, using=None):
        return (
            self.get_model()
            .objects.select_related("project", "programme", "state")
            .prefetch_related(
                "programme_areas",
                "project__programme_areas",
                "project__priority_sectors",
                "programme__programme_areas",
                "programme__programme_areas__priority_sector",
            )
        )

    def prepare_kind(self, obj):
        return "BilateralInitiative"

    def prepare_period(self, obj):
        return [obj.get_funding_period_display()]

    def prepare_state_name(self, obj):
        return obj.state and [obj.state.name]

    def prepare_financial_mechanism_ss(self, obj):
        return obj.programme.financial_mechanisms_display

    def prepare_programme_name(self, obj):
        return obj.programme and [obj.programme.display_name]

    def prepare_programme_status(self, obj):
        return obj.programme and [obj.programme.status]

    def prepare_programme_area_ss(self, obj):
        return [area.name for area in obj.programme_areas.all()]

    def prepare_priority_sector_ss(self, obj):
        return list(
            set(area.priority_sector.name for area in obj.programme_areas.all())
        )

    def prepare_project_name(self, obj):
        return obj.project and [obj.project.display_name]

    def prepare_project_status(self, obj):
        return obj.project and obj.project.status

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        self.prepared_data["project_name_auto"] = (
            " ".join(self.prepared_data["project_name"])
            if self.prepared_data["project_name"]
            else None
        )
        return self.prepared_data

    def prepare_title(self, obj):
        return obj.display_name

    def prepare_grant(self, obj):
        return obj.grant

    def prepare_promoter_state_name(self, obj):
        return obj.promoter_state and obj.promoter_state.name


class ProgrammeIndex(SearchIndex, Indexable):
    # common facets
    period = fields.FacetMultiValueField()
    state_name = fields.FacetMultiValueField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()
    financial_mechanism_ss = fields.FacetMultiValueField()
    outcome_ss = fields.FacetMultiValueField()
    outcome_ss_auto = fields.EdgeNgramField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField(model_attr="status")
    organisation = fields.FacetMultiValueField()

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
                "organisation_roles",
                "organisation_roles__organisation",
            )
        )

    def indicators_query(self, obj):
        return obj.indicators.all()

    def programme_area_query(self, obj):
        return obj.programme_areas.all()

    def prepare_kind(self, obj):
        return "Programme"

    def prepare_period(self, obj):
        return [obj.get_funding_period_display()]

    def prepare_state_name(self, obj):
        # Get this from ProgrammeOutcome, because of IN22
        return list(
            set(indicator.state.name for indicator in self.indicators_query(obj)).union(
                state.name for state in obj.states.all()
            )
        )

    def prepare_programme_name(self, obj):
        return [obj.display_name]

    def prepare_programme_area_ss(self, obj):
        return list(set([area.name for area in self.programme_area_query(obj)]))

    def prepare_priority_sector_ss(self, obj):
        return list(
            set([area.priority_sector.name for area in self.programme_area_query(obj)])
        )

    def prepare_financial_mechanism_ss(self, obj):
        return obj.financial_mechanisms_display

    def prepare_outcome_ss(self, obj):
        return list(
            set(
                " ".join(indicator.header.split()) for indicator in obj.indicators.all()
            )
        )

    def prepare_grant(self, obj):
        return obj.allocation_eea + obj.allocation_norway

    def prepare_organisation(self, obj):
        return list(
            set(role.organisation.name for role in obj.organisation_roles.all())
        )

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
    period = fields.FacetMultiValueField()
    state_name = fields.FacetMultiValueField(model_attr="state__name")
    financial_mechanism_ss = fields.FacetMultiValueField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField(model_attr="programme__status")
    outcome_ss = fields.FacetMultiValueField()
    outcome_ss_auto = fields.EdgeNgramField()
    organisation = fields.FacetMultiValueField()
    organisation_auto = fields.EdgeNgramField()
    kind = fields.FacetCharField()

    # specific facets
    code = fields.FacetCharField(model_attr="code")
    project_status = fields.FacetMultiValueField(model_attr="status")
    geotarget = fields.FacetMultiValueField()
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

    def indicator_query(self, obj):
        return obj.programme.indicators.all()

    def prepare_kind(self, obj):
        return "Project"

    def prepare_geotarget(self, obj):
        return obj.geotarget

    def prepare_period(self, obj):
        return [obj.get_funding_period_display()]

    def prepare_financial_mechanism_ss(self, obj):
        return obj.financial_mechanisms_display

    def prepare_programme_area_ss(self, obj):
        return [area.name for area in self.programme_area_query(obj)]

    def prepare_priority_sector_ss(self, obj):
        return [sector.name for sector in self.priority_sector_query(obj)]

    def prepare_programme_name(self, obj):
        return [obj.programme.display_name]

    def prepare_outcome_ss(self, obj):
        return list(
            set(
                " ".join(indicator.header.split())
                for indicator in self.indicator_query(obj)
            )
        )

    def prepare_theme_ss(self, obj):
        return list(set(theme.name for theme in self.themes_query(obj)))

    def prepare_organisation(self, obj):
        return list(
            set(role.organisation.name for role in obj.organisation_roles.all())
        )

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
        self.prepared_data["organisation_auto"] = (
            " ".join(self.prepared_data["organisation"])
            if self.prepared_data["organisation"]
            else None
        )
        return self.prepared_data


class NewsIndex(SearchIndex, Indexable):
    # common facets;
    period = fields.FacetMultiValueField()
    state_name = fields.FacetMultiValueField()
    financial_mechanism_ss = fields.FacetMultiValueField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()
    programme_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField()
    outcome_ss = fields.FacetMultiValueField()

    kind = fields.FacetCharField()

    # specific facets
    project_name = fields.FacetMultiValueField()
    project_name_auto = fields.EdgeNgramField()
    project_status = fields.FacetMultiValueField()
    geotarget = fields.FacetMultiValueField()
    geotarget_auto = fields.EdgeNgramField()
    theme_ss = fields.FacetMultiValueField()

    # specific fields
    text = fields.CharField(document=True, use_template=True)
    summary = fields.CharField(model_attr="summary", indexed=False, null=True)
    name = fields.CharField(model_attr="title", indexed=False)
    url = fields.CharField(model_attr="link", indexed=False)
    image = fields.CharField(model_attr="image", indexed=False)
    created_dt = fields.DateTimeField(model_attr="created", indexed=False, null=True)

    def get_model(self):
        return News

    def prepare_kind(self, obj):
        return "News"

    def index_queryset(self, using=None):
        return (
            self.get_model()
            .objects.select_related(
                "project",
                "project__state",
            )
            .prefetch_related(
                "programmes",
                "programmes__states",
                "programmes__indicators",
                "programmes__programme_areas",
                "programmes__programme_areas__priority_sector",
                "project__programme_areas",
                "project__priority_sectors",
                "project__themes",
            )
        )

    def prepare_period(self, obj):
        if obj.project:
            return [obj.project.get_funding_period_display()]
        return list(
            set(
                programme.get_funding_period_display()
                for programme in obj.programmes.all()
            )
        )

    def prepare_state_name(self, obj):
        if obj.project:
            return [obj.project.state.name]
        else:
            # Get this from ProgrammeOutcome, because of IN22
            return list(
                set(
                    state.name
                    for programme in obj.programmes.all()
                    for state in programme.states.all()
                )
            )

    def prepare_financial_mechanism_ss(self, obj):
        if obj.project:
            return obj.project.financial_mechanisms_display

        return list(
            set(
                fm
                for programme in obj.programmes.all()
                for fm in programme.financial_mechanisms_display
            )
        )

    def prepare_programme_area_ss(self, obj):
        if obj.project:
            return [
                programme_area.name
                for programme_area in obj.project.programme_areas.all()
            ]

        return list(
            set(
                area.name
                for programme in obj.programmes.all()
                for area in programme.programme_areas.all()
            )
        )

    def prepare_priority_sector_ss(self, obj):
        if obj.project:
            return [sector.name for sector in obj.project.priority_sectors.all()]

        return list(
            set(
                area.priority_sector.name
                for programme in obj.programmes.all()
                for area in programme.programme_areas.all()
            )
        )

    def prepare_programme_name(self, obj):
        if obj.project:
            return [obj.project.programme.display_name]
        return list(set([programme.display_name for programme in obj.programmes.all()]))

    def prepare_project_name(self, obj):
        return obj.project and obj.project.display_name

    def prepare_programme_status(self, obj):
        if obj.project:
            return [obj.project.programme.status]
        return list(set([programme.status for programme in obj.programmes.all()]))

    def prepare_outcome_ss(self, obj):
        if obj.project:
            return list(
                set(
                    " ".join(indicator.header.split())
                    for indicator in obj.project.programme.indicators.all()
                )
            )
        return list(
            set(
                " ".join(indicator.header.split())
                for programme in obj.programmes.all()
                for indicator in programme.indicators.all()
            )
        )

    def prepare_project_status(self, obj):
        if obj.project:
            return [obj.project.status]
        return None

    def prepare_geotarget(self, obj):
        return obj.project and obj.project.geotarget

    def prepare_theme_ss(self, obj):
        if obj.project:
            return list(set([theme.name for theme in obj.project.themes.all()]))
        return None

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        self.prepared_data["geotarget_auto"] = (
            " ".join(self.prepared_data["geotarget"])
            if self.prepared_data["geotarget"]
            else None
        )
        self.prepared_data["project_name_auto"] = (
            " ".join(self.prepared_data["project_name"])
            if self.prepared_data["project_name"]
            else None
        )
        return self.prepared_data


class OrganisationIndex(SearchIndex, Indexable):
    # common facets
    period = fields.FacetMultiValueField()
    state_name = fields.FacetMultiValueField()
    programme_status = fields.FacetMultiValueField()
    financial_mechanism_ss = fields.FacetMultiValueField()
    programme_name = fields.FacetMultiValueField()
    programme_name_auto = fields.EdgeNgramField()
    project_name = fields.FacetMultiValueField()
    project_name_auto = fields.EdgeNgramField()
    programme_area_ss = fields.FacetMultiValueField()
    priority_sector_ss = fields.FacetMultiValueField()

    text = fields.CharField(document=True, use_template=True)

    kind = fields.FacetCharField()

    # specific facets
    project_status = fields.FacetMultiValueField()
    org_type_category = fields.FacetCharField(model_attr="category")
    org_type = fields.FacetCharField(model_attr="subcategory")
    country = fields.FacetCharField(model_attr="country")
    city = fields.FacetCharField(model_attr="city")
    city_auto = fields.EdgeNgramField()
    geotarget = fields.FacetCharField(null=True)
    geotarget_auto = fields.EdgeNgramField(null=True)
    role_ss = fields.FacetMultiValueField()
    role_max_priority_code = fields.IntegerField()

    # extra data; avoid db hit
    org_name = fields.FacetCharField()
    org_name_auto = fields.EdgeNgramField()

    # Highest number = max priority for role. Others default to priority 0.
    ROLE_PRIORITIES = {
        "National Focal Point": 7,  # NFP
        "Programme Operator": 6,  # PO
        "Donor Programme Partner": 5,  # DPP
        "Donor Project Partner": 4,  # PJDPP
        "Programme Partner": 3,  # PP
        "Project Partner": 2,  # PJPP
        "Project Promoter": 1,  # PJPT
    }

    def __init__(self):
        super().__init__()

    def index_queryset(self, using=None):
        return self.get_model().objects.prefetch_related(
            "roles",
            "roles__state",
            "roles__project",
            "roles__project__state",
            "roles__project__programme",
            "roles__project__programme_areas",
            "roles__programme",
            "roles__programme__states",
            "roles__programme__programme_areas",
        )

    def get_model(self):
        return Organisation

    def prepare_kind(self, obj):
        return "Organisation"

    def prepare_period(self, obj):
        return [role.get_funding_period_display() for role in obj.roles.all()]

    def prepare_financial_mechanism_ss(self, obj):
        return list(
            set(
                fm
                for item in itertools.chain(obj.projects, obj.programmes)
                for fm in item.financial_mechanisms_display
            )
        )

    def prepare_state_name(self, obj):
        # programme IN22 can have multiple states
        states = set()
        for role in obj.roles.all():
            if role.state:
                states.add(role.state.name)
        for project in obj.projects:
            states.add(project.state.name)
        for programme in obj.programmes:
            for state in programme.states.all():
                states.add(state.name)

        return list(states)

    def prepare_programme_status(self, obj):
        statuses = set(programme.status for programme in obj.programmes)
        # Add programme status from projects also
        return list(
            statuses.union(project.programme.status for project in obj.projects)
        )

    def prepare_project_status(self, obj):
        return list(set(project.status for project in obj.projects))

    def prepare_programme_area_ss(self, obj):
        areas = set()
        for project in obj.projects:
            for area in project.programme_areas.all():
                areas.add(area.name)
        for programme in obj.programmes:
            for area in programme.programme_areas.all():
                areas.add(area.name)

        return list(areas)

    def prepare_priority_sector_ss(self, obj):
        sectors = set()
        for project in obj.projects:
            for sector in project.priority_sectors.all():
                sectors.add(sector.name)
        for programme in obj.programmes:
            for area in programme.programme_areas.all():
                sectors.add(area.priority_sector.name)

        return list(sectors)

    def prepare_programme_name(self, obj):
        names = set()
        for project in obj.projects:
            names.add(project.programme.display_name)
        for programme in obj.programmes:
            names.add(programme.display_name)

        return list(names)

    def prepare_project_name(self, obj):
        return list(set(project.display_name for project in obj.projects))

    def prepare_role_ss(self, obj):
        return list(set(role.role_name for role in obj.roles.all()))

    def prepare_geotarget(self, obj):
        return obj.geotarget

    def prepare_org_name(self, obj):
        return " ".join(obj.name.split())

    def prepare(self, obj):
        if len(obj.roles.all()) == 0:
            raise exceptions.SkipDocument

        self.prepared_data = super().prepare(obj)

        # Add extra data in text field to avoid extra queries in template
        self.prepared_data["text"] += " ".join(
            self.prepared_data["state_name"]
            + self.prepared_data["programme_name"]
            + self.prepared_data["project_name"]
        )

        self.prepared_data["programme_name_auto"] = (
            " ".join(self.prepared_data["programme_name"])
            if self.prepared_data["programme_name"]
            else None
        )
        self.prepared_data["project_name_auto"] = (
            " ".join(self.prepared_data["project_name"])
            if self.prepared_data["project_name"]
            else None
        )
        self.prepared_data["geotarget_auto"] = (
            " ".join(self.prepared_data["geotarget"])
            if self.prepared_data["geotarget"]
            else None
        )
        self.prepared_data["org_name_auto"] = self.prepared_data["org_name"]

        if self.prepared_data["role_ss"]:
            self.prepared_data["role_max_priority_code"] = reduce(
                lambda max_value, role: max(
                    max_value, self.ROLE_PRIORITIES.get(role, 0)
                ),
                self.prepared_data["role_ss"],
                0,
            )
        else:
            self.prepared_data["role_max_priority_code"] = None
        return self.prepared_data

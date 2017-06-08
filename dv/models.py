# -*- coding: utf-8 -*-
import bleach
import re
from django.db import models
from enumfields import EnumField, Enum
from django.utils.translation import ugettext_lazy as _
from dv.lib.models import ImportableModelMixin
from dv.lib import utils


class _BaseManager(models.Manager):
    pass


class _BaseModel(ImportableModelMixin, models.Model):
    objects = _BaseManager()

    class Meta:
        abstract = True


class _MainManager(_BaseManager):
    def get_by_natural_key(self, nkey):
        return self.get(**{self.model.NATURAL_KEY_FIELD: nkey})

    def filter_by_natural_keys(self, nkeys):
        lookup = "%s__in" % self.model.NATURAL_KEY_FIELD
        return self.filter(**{lookup: nkeys})


class _MainModel(_BaseModel):
    # all main models have a unique code
    NATURAL_KEY_FIELD = 'code'

    objects = _MainManager()

    @property
    def natural_key(self):
        return getattr(self, self.NATURAL_KEY_FIELD)

    __ENDING_STR_RE = re.compile(r'[^\w]+$')
    def __str__(self):
        # output the code, and shorten long names
        _MINW, _MAXW = 5, 7

        words = self.name.split()
        if len(words) <= _MAXW:
            short_name = self.name
        else:
            short_name = "%s …" % (
                self.__ENDING_STR_RE.sub("", " ".join(words[:_MINW])))

        return "%s - %s" % (self.natural_key, short_name)

    class Meta(_BaseModel.Meta):
        abstract = True


class FinancialMechanism(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'PrioritySector',
            'map': {
                'code': 'FMCode',
                'name': 'FinancialMechanism',
                'grant_name': 'GrantName',
            }
        },
    ]

    code = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    grant_name = models.CharField(max_length=128, unique=True)


# TODO: fix NUTS data issues and use this as foreign key below
class NUTS(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 0,
            'map': {
                'code': 'CODE',
                'label': 'LABEL',
            }
        },
    ]

    code = models.CharField(max_length=2, primary_key=True)
    label = models.CharField(max_length=128)

    @property
    def level(self):
        """The NUTS level."""
        return len(self.code) - 2

    class Meta(_BaseModel.Meta):
        ordering = ['code']

    def __str__(self):
        return self.code


class State(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'BeneficiaryState',
            'map': {
                'code': 'Abbreviation',
                'name': 'BeneficiaryState',
                'url': 'UrlBSPage',
            }
        },
    ]

    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    url = models.TextField()


class PrioritySector(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'PrioritySector',
            'map': {
                'type': 'FMCode',
                'code': 'PSCode',
                'name': 'PrioritySector',
            }
        },
    ]

    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)  # not unique

    type = models.ForeignKey(FinancialMechanism)


class ProgrammeArea(_MainModel):
    # programme areas are defined in the same sheet with priority sectors
    IMPORT_SOURCES = [
        {
            'src': 'PrioritySector',
            'map': {
                'priority_sector': 'PSCode',
                'code': 'PACode',
                'name': 'ProgrammeArea',
                'short_name': 'ProgrammeAreaShortName',
                'order': 'SortOrder',
                'objective': 'ProgrammeAreaObjective',
            }
        },
    ]

    # each PA code is duplicated for the 2 FM present now
    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=256)  # not unique because of FM
    short_name = models.CharField(max_length=32)  # not unique
    order = models.SmallIntegerField()
    objective = models.TextField()

    priority_sector = models.ForeignKey(PrioritySector)
    # Allocation also branches off towards FM
    allocations = models.ManyToManyField(State, through="Allocation")


class Allocation(_MainModel):
    NATURAL_KEY_FIELD = None
    IMPORT_SOURCES = [
        {
            'src': 'BeneficiaryStatePrioritySector',
            'map': {
                'state': ('name', 'BeneficiaryState'),
                'programme_area': 'PACode',
                'financial_mechanism': 'FMCode',
                'gross_allocation': 'GrossAllocation',
                'net_allocation': 'NetAllocation',
                'order': 'SortOrder',
            }
        },
    ]

    state = models.ForeignKey(State)
    programme_area = models.ForeignKey(ProgrammeArea)
    # PA is already including FM, but add this so we have more data traversal paths
    financial_mechanism = models.ForeignKey(FinancialMechanism)

    gross_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    net_allocation = models.DecimalField(max_digits=15, decimal_places=2)

    order = models.SmallIntegerField()

    def __str__(self):
        return "{} / {} / {} of gross: {} (net: {})".format(
            self.financial_mechanism_id,
            self.state_id,
            self.programme_area_id,
            self.gross_allocation,
            self.net_allocation
        )

    class Meta(_MainModel.Meta):
        unique_together = ('state', 'programme_area', 'financial_mechanism')


class Programme(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'Programme',
            'map': {
                'state': ('name', 'BeneficiaryState'),
                # skipping this, as we can't import m2ms before the instance is saved
                #'programme_areas': 'PAListWithShortName', # this needs special massaging
                'code': 'ProgrammeCode',
                'name': 'Programme',
                'summary': 'ProgrammeSummary',
                'allocation_eea': 'AllocatedProgrammeGrantEEA',
                'allocation_norway': 'AllocatedProgrammeGrantNorway',
                'co_financing': 'ProgrammeCoFinancing',
                'status': 'ProgrammeStatus',
                'url': 'UrlProgrammePage',
                # TODO: leftovers
                #IsDirectlyContracted
                'is_tap': 'IsTAProgramme'
            }
        },
    ]

    class STATUS(Enum):
        APPROVED = 'approved'
        IMPLEMENTATION = 'implementation'

        class Labels:
            APPROVED = _('Approved'),
            IMPLEMENTATION = _('Implementation')

    @classmethod
    def from_data(cls, data, src_idx):
        """ Mutates its data! """
        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        data[mapping['summary']] = bleach.clean(
            data[mapping['summary']], strip=True, strip_comments=True)

        return super().from_data(data, src_idx)

    state = models.ForeignKey(State)
    programme_areas = models.ManyToManyField(ProgrammeArea,
                                             through="Programme_ProgrammeArea")

    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=256)  # not unique

    status = EnumField(STATUS, max_length=14)

    url = models.CharField(max_length=256, null=True)
    summary = models.TextField()

    allocation_eea = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_norway = models.DecimalField(max_digits=15, decimal_places=2)

    is_tap = models.BooleanField()

    @property
    def allocation(self):
        return self.allocation_eea + self.allocation_norway

    co_financing = models.DecimalField(max_digits=15, decimal_places=2)

    @property
    def is_eea(self):
        return self.allocation_eea != 0

    @property
    def is_norway(self):
        return self.allocation_norway != 0


class Programme_ProgrammeArea(_BaseModel):
    """
    A m2m-through table, defined explicitly only so it can be used during import
    """
    IMPORT_SOURCES = [
        {
            'src': 'Programme',
            'map': {
                'programme': 'programme',
                'programme_area': 'programme_area',
            },
            # note the leading underscore, this won't hit ImportableModelMixin.from_data
            '_map': {
                'programme': 'ProgrammeCode',
                'programme_area': 'PAListWithShortName',
            }
        },
    ]

    __PA_RE = re.compile(r'(?:^|,)([A-Z]{2}[0-9]{2}) - ')

    @classmethod
    def from_data(cls, data, src_idx):
        # this isn't a regular from_data() method, because
        # it returns multiple instances!

        private_mapping = cls.IMPORT_SOURCES[src_idx]['_map']
        p_column = private_mapping['programme']
        programme = data[p_column]

        pa_column = private_mapping['programme_area']
        # we need to extract the programme area codes from the input
        programme_areas = re.findall(cls.__PA_RE, data[pa_column])

        def _generate_data():
            for pa in programme_areas:
                yield {
                    'programme': programme,
                    'programme_area': pa,
                }

        # weird - we can't get away with bare super()...
        return ( super(cls, cls).from_data(subdata, src_idx) for subdata in _generate_data())

    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)

    class Meta(_MainModel.Meta):
        unique_together = ('programme', 'programme_area')

    def __str__(self):
        return "%s _ %s" % (self.programme.code, self.programme_area.code)


class _FussyOutcomeCode(object):
    @classmethod
    def from_data(cls, data, src_idx):
        # fix non-unique FBL outcome codes
        # FBL = Fund for bilateral cooperation
        data = data.copy()
        if data['OutcomeCode'] == 'FBL':
            # derive a unique key from the outcome name
            uniq = utils.uniq_hash(data['Outcome'])[:5]
            code = '%sFBL%s' % (data['PACode'], uniq)
            data['OutcomeCode'] = code

        return super().from_data(data, src_idx)


class Outcome(_FussyOutcomeCode, _MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'ProgrammeOutcomes',
            'map': {
                'programme_area': 'PACode',
                'code': 'OutcomeCode',
                'name': 'Outcome',
                'fixed_budget_line': 'IsFixedBudgetline',
                # TODO: leftovers
                #'IsProgrammeArea',
                #'IsForReportingOnly'
            }
        },
    ]

    programme_area = models.ForeignKey(ProgrammeArea, related_name='outcomes')

    code = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=512)  # not unique

    fixed_budget_line = models.BooleanField()


class ProgrammeOutcome(_FussyOutcomeCode, _BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'ProgrammeOutcomes',
            'map': {
                'programme': 'ProgrammeCode',
                'outcome': 'OutcomeCode',
                'state': ('name', 'BeneficiaryState'),
                'allocation': 'GrantAmount',
                'co_financing': 'ProgrammeCoFinancing',
            }
        },
        # Update ProgrammeOutcom based on info from ProgrammeIndicators
        # make sure you identify same row (all uniq constraints present)
        {
            'src': 'ProgrammeIndicators',
            'map': {
                'programme': 'ProgrammeCode',
                'outcome': 'OutcomeCode',
                'result_text': 'ResultText',
            }
        },
    ]

    programme = models.ForeignKey(Programme, null=True)  # because "Reserve FM2004-09"
    outcome = models.ForeignKey(Outcome, related_name='programmes')
    state = models.ForeignKey(State)

    allocation = models.FloatField()
    co_financing = models.FloatField()
    result_text = models.CharField(max_length=300, default='')  # see "Well-functioning..."

    class Meta:
        unique_together = ('programme', 'outcome', 'state')

    def __str__(self):
        return "%s _ %s" % (self.programme.code, self.outcome.code)


class Project(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'Project',
            'map': {
                'state': ('name', 'BeneficiaryState'),
                'programme': 'ProgrammeCode',
                'programme_area': 'PACode',
                'outcome': 'OutcomeCode',
                'financial_mechanism': 'FMCode',
                'status': 'ProjectStatus',
                'code': 'ProjectCode',
                'name': 'Project',
                'allocation': 'GrantAmount',
                'geotarget': 'GeographicalTarget',
                'nuts': 'NUTSCode',
                'programme_co_financing': 'ProgrammeCoFinancing',
                'project_co_financing': 'ProjectCoFinancing',
                'is_eea': 'IsEEA',
                'is_norway': 'IsNorway',
                'url': 'UrlProjectPage',
                'has_ended': 'HasEnded',
                'is_dpp': 'HasDpp',
                'is_positive_fx': 'ResultPositiveEffects',
                'is_improved_knowledge': 'ResultImprovedKnowledge',
                'is_continued_coop': 'ResultContinuedCooperation',
                'is_published': 'IsPublished',

                # TODO: leftovers
                #'Predefined',
                #'PlannedSummary',
                #'ActualSummary',
                #'IsSmallGrantScheme',
                #'IsPredefined',
                #'IsBestPracticeProject',
                #'IsMobility',
            }
        },
    ]

    class STATUS(Enum):
        IN_PROGRESS = 'in progress'
        COMPLETED = 'completed'
        TERMINATED = 'terminated'
        NON_COMPLETED = 'non completed'

        class Labels:
            IN_PROGRESS = _('In Progress')
            COMPLETED = _('Completed')
            TERMINATED = _('Terminated')
            NON_COMPLETED = _('Non Completed')

    state = models.ForeignKey(State)
    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)
    outcome = models.ForeignKey(Outcome)
    financial_mechanism = models.ForeignKey(FinancialMechanism)

    status = EnumField(STATUS, max_length=11)

    code = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=512)  # not unique
    nuts = models.CharField(max_length=5)
    geotarget = models.CharField(max_length=256)
    url = models.CharField(max_length=256, null=True)
    allocation = models.DecimalField(max_digits=15, decimal_places=2)
    programme_co_financing = models.DecimalField(max_digits=15, decimal_places=2)
    project_co_financing = models.DecimalField(max_digits=15, decimal_places=2)
    is_eea = models.BooleanField()
    is_norway = models.BooleanField()
    has_ended = models.BooleanField()
    is_dpp = models.BooleanField()
    is_positive_fx = models.BooleanField()
    is_improved_knowledge = models.BooleanField()
    is_continued_coop = models.BooleanField()
    is_published = models.BooleanField()


class ProjectTheme(_BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'ProjectThemes',
            'map': {
                'project': 'ProjectCode',
                'name': 'Theme',
            }
        },
    ]

    project = models.ForeignKey(Project, related_name='themes')
    name = models.CharField(max_length=512)  # not unique

    def __str__(self):
        return "%s - %s" % (self.project_id, self.name)


class Indicator(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'ProgrammeIndicators',
            'map': {
                'code': 'IndicatorCode',
                'name': 'Indicator',
            }
        },
    ]

    code = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=256)


class ProgrammeIndicator(_BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'ProgrammeIndicators',
            'map': {
                'indicator': 'IndicatorCode',
                'programme': 'ProgrammeCode',
                'programme_area': 'ProgrammeAreaCode',
                'outcome': 'OutcomeCode',
                'result_text': 'ResultText',
                'state': ('name', 'BeneficiaryState'),
                'achievement': 'Achievement',
            }
        },
    ]

    # TODO: assess linking (all 3? of) these to ProgrammeOutcome
    #'ProgrammeCode',
    #'ProgrammeAreaCode',
    #'OutcomeCode',

    indicator = models.ForeignKey(Indicator)

    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)
    outcome = models.ForeignKey(Outcome)
    state = models.ForeignKey(State, null=True)
    # this is also on ProgrammeOutcome...
    result_text = models.CharField(max_length=300, default='')  # see "Well-functioning..."

    achievement = models.IntegerField()

    def __str__(self):
        return "%s - %s" % (self.programme.code, self.indicator.code)


class OrganisationType(_BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'Organisation',
            'map': {
                'category': 'OrganisationTypeCategory',
                'name': 'OrganisationType',
            }
        },
    ]

    @classmethod
    def from_data(cls, data, src_idx):
        # skip empty stuff
        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        if data[mapping['name']] is None:
            return

        return super().from_data(data, src_idx)

    class CATEGORY(Enum):
        PRIVATE_SECTOR = 'private sector'
        PUBLIC_SECTOR = 'public sector'
        CIVIL_SOCIETY = 'civil society'
        EDUCATION = 'education'

        INTERNATIONAL_INSTITUTIONS = 'international institutions'
        OTHER = 'other'

        class Labels:
            PRIVATE_SECTOR = _('Private sector')
            PUBLIC_SECTOR = _('Public sector')
            CIVIL_SOCIETY = _('Civil society')
            EDUCATION = _('Education')
            INTERNATIONAL_INSTITUTIONS = _('International institutions')
            OTHER = _('Other')

    category = EnumField(CATEGORY, max_length=26)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return "%s / %s" % (self.category, self.name)


class OrganisationRole(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'OrganisationRoles',
            'map': {
                'code': 'OrganisationRoleCode',
                'role': 'OrganisationRole',
            }
        },
    ]

    code = models.CharField(max_length=8, primary_key=True)
    role = models.CharField(max_length=64)


class Organisation(_BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'Organisation',
            'map': {
                'id': 'IdOrganisation',
                'name': 'Organisation',
                'ptype': 'IsProgrammeOrProjectOrg',
                'orgtype': ('name', 'OrganisationType'),
                'nuts': 'NUTSCode',
                'country': 'Country',
                'geotarget': 'GeographicalTarget',

                # leftovers
                #'City',
            }
        },
    ]

    class ORGANISATION_TYPE(Enum):
        PROGRAMME = 'programme'
        PROJECT = 'project'

        class Labels:
            PROGRAMME = _('Programme')
            PROJECT = _('Project')

    ptype = EnumField(ORGANISATION_TYPE, max_length=9)
    orgtype = models.ForeignKey(OrganisationType, null=True)
    # the countries can be different from member states; that's why we don't use FK
    country = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    geotarget = models.CharField(max_length=256)
    nuts = models.CharField(max_length=5)

    role = models.ManyToManyField(OrganisationRole, through="Organisation_OrganisationRole")

    # TODO: can't unique, as organisations are duplicate if they're both programme & project level.

    def __str__(self):
        return "%s _ %s" % (self.country, self.name)


class Organisation_OrganisationRole(_MainModel, ImportableModelMixin):
    IMPORT_SOURCES = [
        {
            'src': 'OrganisationRoles',
            'map': {
                'organisation': ('id', 'IdOrganisation'),
                'organisation_role': 'OrganisationRoleCode',
                'programme': 'ProgrammeCode',
                'project': 'ProjectCode',
                'is_programme': 'IsProgrammeOrProjectOrg',
                'is_implementing_partner': 'IsImplementingPartner',
            }
        },
    ]

    @classmethod
    def from_data(cls, data, src_idx):
        """ Warning: mutates its input data"""

        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        excel_value = data[mapping['is_programme']].lower()

        # If not str then perheps we somehow already processed this.
        # If bad, non-str data, let Field exception tell us
        if isinstance(excel_value, str):
            model_value = None
            if excel_value == 'programme':
                model_value = True
            elif excel_value == 'project':
                model_value = False
            data[mapping['is_programme']] = model_value

        return super().from_data(data, src_idx)

    organisation = models.ForeignKey(Organisation, related_name='roles')
    organisation_role = models.ForeignKey(OrganisationRole, related_name='organisations')


    # TODO 1: this shouldn't be stored in case the org is a project one
    # TODO 2: this makes no sense, both of them nullable
    # programme and project are denormalised to include BS
    programme = models.ForeignKey(Programme, null=True)
    project = models.ForeignKey(Project, null=True)
    is_programme = models.NullBooleanField(default=None)
    is_implementing_partner = models.BooleanField()

    class Meta(_BaseModel.Meta):
        unique_together = (
            'organisation',
            'organisation_role',
            'programme',
            'project',
        )

    def __str__(self):
        return "{} - {}".format(self.organisation_id, self.organisation_role_id)


class News(models.Model):
    title = models.TextField(null=False, blank=False)
    link = models.URLField(max_length=2000, null=False, blank=False)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(null=True)

    programmes = models.ManyToManyField(Programme)
    project = models.ForeignKey(Project, null=True)
    summary = models.TextField(null=True)
    image = models.URLField(max_length=2000)
    is_partnership = models.BooleanField(default=False)

    def __str__(self):
        return self.link

    class Meta:
        ordering = ('-created',)

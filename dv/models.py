# -*- coding: utf-8 -*-
import bleach
import re
from django.db import models
from enumfields import EnumField, Enum
from ckeditor.fields import RichTextField
from django.utils.translation import ugettext_lazy as _
from dv.lib.models import ImportableModelMixin
from dv.lib import utils


class _BaseManager(models.Manager):
    pass


class _BaseModel(ImportableModelMixin, models.Model):
    objects = _BaseManager()

    class Meta:
        abstract = True

    updated_at = models.DateTimeField(auto_now=True, null=True)


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
            'src': 'BeneficiaryStatePrioritySector',
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


class NUTS(models.Model):

    code = models.CharField(max_length=2, primary_key=True)
    label = models.CharField(max_length=128)

    @property
    def level(self):
        """The NUTS level."""
        return len(self.code) - 2

    class Meta(_BaseModel.Meta):
        ordering = ['code']
        verbose_name_plural = "NUTS"

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
            'src': 'BeneficiaryStatePrioritySector',
            'map': {
                'code': 'PSCode',
                'name': 'PrioritySector',
            }
        },
    ]

    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)  # not unique


class ProgrammeArea(_MainModel):
    # programme areas are defined in the same sheet with priority sectors
    IMPORT_SOURCES = [
        {
            'src': 'BeneficiaryStatePrioritySector',
            'map': {
                'financial_mechanism': 'FMCode',
                'priority_sector': 'PSCode',
                'code': 'PACode',
                'name': 'ProgrammeArea',
                'short_name': 'ProgrammeAreaShortName',
                'order': 'SortOrder',
                'objective': 'ProgrammeAreaObjective',
                'url': 'UrlPAPage',
                'is_not_ta': 'IsProgrammeArea',
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
    financial_mechanism = models.ForeignKey(FinancialMechanism)
    # Allocation also branches off towards FM
    allocations = models.ManyToManyField(State, through="Allocation")

    # Technical assistance sectors and programme areas are not always displayed
    is_not_ta = models.BooleanField()
    url = models.CharField(max_length=256, null=True)


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

    @classmethod
    def from_data(cls, data, src_idx):
        """ add fake code field """
        obj = super().from_data(data, src_idx)
        obj.code = obj.state_id + obj.programme_area_id
        return obj

    code = models.CharField(max_length=6, primary_key=True)
    state = models.ForeignKey(State)
    programme_area = models.ForeignKey(ProgrammeArea)
    # PA is already including FM, but add this so we have more data traversal paths
    financial_mechanism = models.ForeignKey(FinancialMechanism)

    gross_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    net_allocation = models.DecimalField(max_digits=15, decimal_places=2)

    order = models.SmallIntegerField()

    def __str__(self):
        return "{} / {} / {} gross: {}".format(
            self.financial_mechanism_id,
            self.state_id,
            self.programme_area_id,
            self.gross_allocation,
        )

    class Meta(_MainModel.Meta):
        unique_together = ('state', 'programme_area', 'financial_mechanism')


class ProgrammeStatus(Enum):
    APPROVED = 'approved'
    IMPLEMENTATION = 'implementation'
    COMPLETED = 'completed'
    CLOSED = 'closed'
    WITHDRAWN = 'withdrawn'
    RETURNED = 'returned'

    class Labels:
        APPROVED = _('Approved')
        IMPLEMENTATION = _('Implementation')
        COMPLETED = _('Completed')
        CLOSED = _('Closed')
        WITHDRAWN = _('Withdrawn')
        RETURNED = _('Returned to po')


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
                'is_tap': 'IsTAProgramme'
            }
        },
    ]

    __post_bleach_comments_re = re.compile(r'&lt;!--.*--&gt;')

    @classmethod
    def from_data(cls, data, src_idx):
        """ Mutates its data! """
        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        data[mapping['summary']] = bleach.clean(
            data[mapping['summary']] or '', strip=True, strip_comments=True)
        data[mapping['summary']] = cls.__post_bleach_comments_re.sub('', data[mapping['summary']])

        return super().from_data(data, src_idx)

    state = models.ForeignKey(State)
    programme_areas = models.ManyToManyField(ProgrammeArea,
                                             through="Programme_ProgrammeArea")

    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=256)  # not unique

    status = EnumField(ProgrammeStatus, max_length=14)

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
                'code': ['programme', 'programme_area']
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

    code = models.CharField(max_length=9, primary_key=True)
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
            'src': 'ProgrammeOutcome',
            'map': {
                'programme_area': 'PACode',
                'code': 'OutcomeCode',
                'name': 'Outcome',
                'fixed_budget_line': 'IsFixedBudgetline',
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
            'src': 'ProgrammeOutcome',
            'map': {
                'programme': 'ProgrammeCode',
                'outcome': 'OutcomeCode',
                'state': ('name', 'BeneficiaryState'),
                'allocation': 'GrantAmount',
                'co_financing': 'ProgrammeCoFinancing',
            }
        },
        # Update ProgrammeOutcome based on info from ProgrammeIndicators
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

    @classmethod
    def from_data(cls, data, src_idx):
        """ add fake code field """
        obj = super(cls, cls).from_data(data, src_idx)
        if obj is not None:
            obj.code = (
                obj.state_id +
                (obj.programme_id if obj.programme_id else '') +
                obj.outcome_id
            )
        return obj

    code = models.CharField(max_length=20, primary_key=True)
    # programme can be null, e.g. "Reserve FM2004-09"
    programme = models.ForeignKey(Programme, null=True, related_name='outcomes')
    outcome = models.ForeignKey(Outcome, related_name='programmes')
    state = models.ForeignKey(State)

    allocation = models.FloatField()
    co_financing = models.FloatField()
    result_text = models.CharField(max_length=300, default='')  # see "Well-functioning..."

    class Meta:
        unique_together = ('programme', 'outcome', 'state')

    def __str__(self):
        return "%s _ %s" % (self.programme.code, self.outcome.code)


class ProjectStatus(Enum):
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    TERMINATED = 'terminated'
    NON_COMPLETED = 'non completed'

    class Labels:
        IN_PROGRESS = _('In Progress')
        COMPLETED = _('Completed')
        TERMINATED = _('Terminated')
        NON_COMPLETED = _('Non Completed')


class Project(_MainModel):
    IMPORT_SOURCES = [
        {
            'src': 'Project',
            'map': {
                'state': ('name', 'BeneficiaryState'),
                'programme': 'ProgrammeCode',
                'outcome': 'OutcomeCode',
                'financial_mechanism': 'FMCode',
                'priority_sector': 'PSCode',
                'programme_area': 'PACode',
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
                'summary': 'PlannedSummary',
            }
        },
    ]

    __post_bleach_comments_re = re.compile(r'&lt;!--.*--&gt;')


    @classmethod
    def from_data(cls, data, src_idx):
        """ Mutates its data! """
        mapping = cls.IMPORT_SOURCES[src_idx]['map']
        data[mapping['summary']] = bleach.clean(
            data[mapping['summary']] or '', strip=True, strip_comments=True)
        data[mapping['summary']] = cls.__post_bleach_comments_re.sub('', data[mapping['summary']])

        return super().from_data(data, src_idx)

    state = models.ForeignKey(State)
    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)
    outcome = models.ForeignKey(Outcome)
    financial_mechanism = models.ForeignKey(FinancialMechanism)
    priority_sector = models.ForeignKey(PrioritySector)

    status = EnumField(ProjectStatus, max_length=11)

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
    summary = models.TextField()


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

    @classmethod
    def from_data(cls, data, src_idx):
        """ add fake code field """
        obj = super().from_data(data, src_idx)
        obj.code = obj.project_id + obj.name
        return obj

    code = models.CharField(max_length=512, primary_key=True)
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
                'order': 'SortOrder',
            }
        },
    ]

    # TODO: assess linking (all 3? of) these to ProgrammeOutcome
    #'ProgrammeCode',
    #'ProgrammeAreaCode',
    #'OutcomeCode',


    @classmethod
    def from_data(cls, data, src_idx):
        """ add fake code field """
        obj = super().from_data(data, src_idx)
        if obj is not None:
            obj.code = (
                obj.state_id +
                (obj.programme_id if obj.programme_id else '') +
                obj.outcome_id +
                obj.indicator_id
            )
        return obj

    code = models.CharField(max_length=255, primary_key=True)

    indicator = models.ForeignKey(Indicator)

    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)
    outcome = models.ForeignKey(Outcome)
    state = models.ForeignKey(State, null=True)
    # this is also on ProgrammeOutcome...
    result_text = models.CharField(max_length=300, default='')  # see "Well-functioning..."

    achievement = models.IntegerField()
    order = models.SmallIntegerField()

    def __str__(self):
        return "%s - %s" % (self.programme.code, self.indicator.code)


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

    def __str__(self):
        return "%s _ %s" % (self.code, self.role)


class OrganisationPType(Enum):
    PROGRAMME = 'programme'
    PROJECT = 'project'

    class Labels:
        PROGRAMME = _('Programme')
        PROJECT = _('Project')


class Organisation(_BaseModel):
    IMPORT_SOURCES = [
        {
            'src': 'Organisation',
            'map': {
                'id': 'IdOrganisation',
                'name': 'Organisation',
                'domestic_name': 'OrganisationDomesticName',
                'ptype': 'IsProgrammeOrProjectOrg',
                'orgtype': 'OrganisationType',
                'orgtypecateg': 'OrganisationTypeCategory',
                'nuts': 'NUTSCode',
                'country': 'Country',
                'city': 'City',
                'geotarget': 'GeographicalTarget',
            }
        },
    ]

    ptype = EnumField(OrganisationPType, max_length=9)
    # the countries can be different from member states; that's why we don't use FK
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    domestic_name = models.CharField(max_length=256, null=True)
    geotarget = models.CharField(max_length=256)
    nuts = models.CharField(max_length=5)
    orgtype = models.CharField(max_length=256)
    orgtypecateg = models.CharField(max_length=256)

    role = models.ManyToManyField(OrganisationRole, through="Organisation_OrganisationRole")

    # TODO: can't unique, as organisations are duplicate if they're both programme & project level.

    def __str__(self):
        return "%s _ %s" % (self.country, self.name)


class Organisation_OrganisationRole(_MainModel, ImportableModelMixin):
    IMPORT_SOURCES = [
        {
            'src': 'OrganisationRoles',
            'map': {
                'code': ['IdOrganisation', 'OrganisationRoleCode', 'ProgrammeCode', 'ProjectCode'],
                'organisation': ('id', 'IdOrganisation'),
                'organisation_role': 'OrganisationRoleCode',
                'programme': 'ProgrammeCode',
                'project': 'ProjectCode',
                'is_programme': 'IsProgrammeOrProjectOrg',
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

    code = models.CharField(max_length=64, primary_key=True)
    organisation = models.ForeignKey(Organisation, related_name='roles')
    organisation_role = models.ForeignKey(OrganisationRole, related_name='organisations')

    # programme and project are denormalised to include BS
    programme = models.ForeignKey(Programme, null=True, related_name='organisation_roles')
    project = models.ForeignKey(Project, null=True, related_name='organisation_roles')
    is_programme = models.NullBooleanField(default=None)

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

    programmes = models.ManyToManyField(Programme, related_name='news')
    project = models.ForeignKey(Project, null=True, related_name='news')
    summary = models.TextField(null=True)
    image = models.URLField(max_length=2000)
    is_partnership = models.BooleanField(default=False)

    def __str__(self):
        return self.link

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = "news"


class StaticContent(models.Model):

    name = models.CharField(
        max_length=64, null=False, blank=False, unique=True)

    body = RichTextField(null=False, blank=False)

    def __str__(self):
        return self.name


class ImportLog(models.Model):

    created_at = models.DateTimeField(auto_now=True, null=True)
    data = models.TextField()

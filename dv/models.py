# -*- coding: utf-8 -*-
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


class FINANCIAL_MECHANISM(Enum):
    EEA = 'eea'
    NORWAY = 'norway'

    class Labels:
        EEA = _('EEA')
        NORWAY = _('Norway')


# TODO: fix NUTS data issues and use this as foreign key below
class NUTS(_MainModel):
    IMPORT_MAPPING = {
        'code': 'NUTS CODE',
        'label': 'NUTS LABEL',
    }

    code = models.CharField(max_length=2, primary_key=True)
    label = models.CharField(max_length=128)

    @property
    def level(self):
        """The NUTS level."""
        return len(self.code) - 2


class State(_MainModel):
    IMPORT_SOURCE = 'BeneficiaryState'
    IMPORT_MAPPING = {
        'name': 'BeneficaryState',
        'code': 'Abbreviation',
    }

    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    # these should be moved away
    gross_allocation_eea = models.PositiveIntegerField()
    gross_allocation_norway = models.PositiveIntegerField()

    @property
    def gross_allocation(self):
        return self.gross_allocation_eea + self.gross_allocation_norway

    # as well as these
    net_allocation_eea = models.PositiveIntegerField()
    net_allocation_norway = models.PositiveIntegerField()

    @property
    def net_allocation(self):
        return self.net_allocation_eea + self.net_allocation_norway


class PrioritySector(_MainModel):
    IMPORT_SOURCE = 'PrioritySector'
    IMPORT_MAPPING = {
        'type': 'GrantName', # this needs special handling
        'code': 'PSCode',
        'name': 'PrioritySector',
    }

    @classmethod
    def from_data(cls, data):
        # our grant type identifier is the first word of the GrantName
        data = data.copy()
        type_column = cls.IMPORT_MAPPING['type']
        data[type_column] = data[type_column].split()[0]
        return super().from_data(data)

    type = EnumField(FINANCIAL_MECHANISM, max_length=6)

    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=64) # not unique


class ProgrammeArea(_MainModel):
    # programme areas are defined in the same sheet with priority sectors
    IMPORT_SOURCE = 'PrioritySector'
    IMPORT_MAPPING = {
        'priority_sector': 'PSCode',
        'code': 'PACode',
        'name': 'ProgrammeArea',
        'short_name': 'ProgrammeAreaShortName',
        'order': 'SortOrder',
        'objective': 'ProgrammeAreaObjective',
    }

    priority_sector = models.ForeignKey(PrioritySector)

    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=256) # not unique
    short_name = models.CharField(max_length=32) # not unique

    order = models.SmallIntegerField()

    objective = models.TextField()

    # TODO: bad decimal field, go sit in a corner
    #gross_allocation = models.PositiveIntegerField()
    gross_allocation = models.FloatField()
    net_allocation = models.PositiveIntegerField()


class Programme(_MainModel):
    IMPORT_SOURCE = 'Programme'
    IMPORT_MAPPING = {
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
        # TODO: leftovers
        #IsDirectlyContracted
        #IsTAProgramme
    }

    class STATUS(Enum):
        APPROVED = 'approved'
        IMPLEMENTATION = 'implementation'

        class Labels:
            APPROVED = _('Approved'),
            IMPLEMENTATION = _('Implementation')

    #@classmethod
    #def from_data(cls, data):
    #    # we need to extract the programme area codes from the input
    #    data = data.copy()
    #    pa_column = cls.IMPORT_MAPPING['programme_areas']
    #    data[pa_column] = data[pa_column].split()[0]
    #    return super().from_data(data)

    state = models.ForeignKey(State)
    programme_areas = models.ManyToManyField(ProgrammeArea,
                                             through="Programme_ProgrammeArea")

    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=256) # not unique

    status = EnumField(STATUS, max_length=14)

    summary = models.TextField()

    allocation_eea = models.PositiveIntegerField()
    allocation_norway = models.PositiveIntegerField()

    @property
    def allocation(self):
        return self.allocation_eea + self.allocation_norway

    # TODO: another decimal field. must... fix...
    #co_financing = models.PositiveIntegerField()
    co_financing = models.FloatField()

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
    IMPORT_SOURCE = 'Programme'
    # note the leading underscore, this won't hit ImportableModelMixin.from_data
    _IMPORT_MAPPING = {
        'programme': 'ProgrammeCode',
        'programme_area': 'PAListWithShortName',
    }

    __PA_RE = re.compile(r'(?:^|,)([A-Z]{2}[0-9]{2}) - ')
    @classmethod
    def from_data(cls, data):
        # this isn't a regular from_data() method, because
        # it returns multiple instances!

        p_column = cls._IMPORT_MAPPING['programme']
        programme = data[p_column]

        pa_column = cls._IMPORT_MAPPING['programme_area']
        # we need to extract the programme area codes from the input
        programme_areas = re.findall(cls.__PA_RE, data[pa_column])

        return list(map(
            super().from_data,
            ({
                'programme': programme,
                'programme_area': pa,
            } for pa in programme_areas)
        ))

    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)

    class Meta(_MainModel.Meta):
        unique_together = ('programme', 'programme_area')

    def __str__(self):
        return "%s _ %s" % (self.programme.code, self.programme_area.code)


class _FussyOutcomeCode(object):
    @classmethod
    def from_data(cls, data):
        # fix non-unique FBL outcome codes
        # FBL = Fund for bilateral cooperation
        data = data.copy()
        if data['OutcomeCode'] == 'FBL':
            # derive a unique key from the outcome name
            uniq = utils.uniq_hash(data['Outcome'])[:5]
            code = '%sFBL%s' % (data['PACode'], uniq)
            data['OutcomeCode'] = code

        return super().from_data(data)


class Outcome(_FussyOutcomeCode, _MainModel):
    IMPORT_SOURCE = 'ProgrammeOutcomes'
    IMPORT_MAPPING = {
        'programme_area': 'PACode',
        'code': 'OutcomeCode',
        'name': 'Outcome',
        'fixed_budget_line': 'IsFixedBudgetline',
        # TODO: leftovers
        #'IsProgrammeArea',
        #'IsForReportingOnly'
    }

    programme_area = models.ForeignKey(ProgrammeArea)

    code = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=512) # not unique

    fixed_budget_line = models.BooleanField()


class ProgrammeOutcome(_FussyOutcomeCode, _BaseModel):
    IMPORT_SOURCE = 'ProgrammeOutcomes'
    IMPORT_MAPPING = {
        'programme': 'ProgrammeCode',
        'outcome': 'OutcomeCode',
        'state': ('name', 'BeneficiaryState'),
        'allocation': 'GrantAmount',
        'co_financing': 'ProgrammeCoFinancing',
    }

    programme = models.ForeignKey(Programme, null=True) # because "Reserve FM2004-09"
    outcome = models.ForeignKey(Outcome)
    state = models.ForeignKey(State)

    # TODO: fix decimal fields
    #allocation = models.PositiveIntegerField()
    #co_financing = models.PositiveIntegerField()
    allocation = models.FloatField()
    co_financing = models.FloatField()

    class Meta:
        unique_together = ('programme', 'outcome', 'state')

    def __str__(self):
        return "%s _ %s" % (self.programme.code, self.outcome.code)

    #@property
    #def state(self):
    #    return self.programme.state


class Project(_MainModel):
    IMPORT_SOURCE = 'Project'
    IMPORT_MAPPING = {
        'state': ('name', 'BeneficiaryState'),
        'programme': 'ProgrammeCode',
        'outcome': 'OutcomeCode',
        'status': 'ProjectStatus',
        'code': 'ProjectCode',
        'name': 'Project',
        'allocation': 'GrantAmount',
        #'geotarget': 'NUTSCode',
        'nuts': 'NUTSCode',

        # TODO: leftovers
        #'Predefined',
        #'PlannedSummary',
        #'ActualSummary',
        #'IsPublished',
        #'IsSmallGrantScheme',
        #'IsPredefined',
        #'IsBestPracticeProject',
        #'IsMobility',
        #'HasEnded'
    }

    class STATUS(Enum):
        IN_PROGRESS = 'in progress'
        COMPLETED = 'completed'
        TERMINATED = 'terminated'

        class Labels:
            IN_PROGRESS = _('In Progress')
            COMPLETED = _('Completed')
            TERMINATED = _('Terminated')

    state = models.ForeignKey(State)
    programme = models.ForeignKey(Programme)
    outcome = models.ForeignKey(Outcome)

    status = EnumField(STATUS, max_length=11)

    code = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=512) # not unique

    #geotarget = models.ForeignKey(NUTS)
    nuts = models.CharField(max_length=5)

    allocation = models.PositiveIntegerField()
    programme_co_financing = models.PositiveIntegerField()
    project_co_financing = models.PositiveIntegerField()

    is_eea = models.BooleanField()
    is_norway = models.BooleanField()


class Indicator(_MainModel):
    IMPORT_SOURCE = 'ProgrammeIndicators'
    IMPORT_MAPPING = {
        'code': 'IndicatorCode',
        'name': 'Indicator',
    }

    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=128, unique=True)


class ProgrammeIndicator(_BaseModel):
    IMPORT_SOURCE = 'ProgrammeIndicators'
    IMPORT_MAPPING = {
        'indicator': 'IndicatorCode',

        'programme': 'ProgrammeCode',
        'programme_area': 'ProgrammeAreaCode',
        'outcome': 'OutcomeCode',
    }

    # TODO: assess linking (all 3? of) these to ProgrammeOutcome
    #'ProgrammeCode',
    #'ProgrammeAreaCode',
    #'OutcomeCode',

    indicator = models.ForeignKey(Indicator)

    programme = models.ForeignKey(Programme)
    programme_area = models.ForeignKey(ProgrammeArea)
    outcome = models.ForeignKey(Outcome)

    achievement = models.IntegerField()

    def __str__(self):
        return "%s _ %s" % ('self.programme.code', self.indicator.code)


class OrganisationType(_BaseModel):
    IMPORT_SOURCE = 'Organisation'
    IMPORT_MAPPING = {
        'category': 'OrganisationTypeCategory',
        'name': 'OrganisationType',
    }

    @classmethod
    def from_data(cls, data):
        # skip empty stuff
        if data[cls.IMPORT_MAPPING['name']] is None:
            return

        return super().from_data(data)

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


class Organisation(_BaseModel):
    IMPORT_SOURCE = 'Organisation'
    IMPORT_MAPPING = {
        'id': 'IdOrganisation',
        'name': 'Organisation',
        'ptype': 'IsProgrammeOrProjectOrg',
        'orgtype': ('name', 'OrganisationType'),
        #'geotarget': 'NUTSCode',
        'nuts': 'NUTSCode',

        # TODO: use proper states/countries table
        #'country': ('name', 'Country'),
    }
    # TODO: leftovers
    #'City',

    class ORGANISATION_TYPE(Enum):
        PROGRAMME = 'programme'
        PROJECT = 'project'

        class Labels:
            PROGRAMME = _('Programme')
            PROJECT = _('Project')

    # TODO: find a better name for this
    ptype = EnumField(ORGANISATION_TYPE, max_length=9)
    # TODO: and this
    orgtype = models.ForeignKey(OrganisationType, null=True)
    # TODO: the countries can be different from member states.
    # TODO: unify.
    #country = models.ForeignKey(State)
    country = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    #geotarget = models.ForeignKey(NUTS)
    nuts = models.CharField(max_length=5)

    class Meta(_BaseModel.Meta):
        # TODO: this isn't unique, as organisations are duplicate
        # if they're both programme- & project-level.
        # TODO: fix it?
        #unique_together = ('country', 'name')
        pass

    def __str__(self):
        return "%s _ %s" % (self.country, self.name)


class OrganisationRole(_BaseModel):
    IMPORT_SOURCE = 'OrganisationRoles'
    IMPORT_MAPPING = {
        'role': 'OrganisationRoleCode',
        'organisation': ('id', 'IdOrganisation'),

        'programme': 'ProgrammeCode',
        'project': 'ProjectCode',
    }
    # TODO: leftovers
    #'Country',
    #'IsProgrammeOrProjectOrg',
    #'IsImplementingPartner'


    @classmethod
    def from_data(cls, data):
        # TODO: temporary fix for bad data. remove.
        if data[cls.IMPORT_MAPPING['programme']] in (
                'RO16', 'GR50', 'PL11', 'RO08'):
            return
        if data[cls.IMPORT_MAPPING['organisation'][1]] in (
                73, 117, 89, 104, 850, 1089):
            return
        return super().from_data(data)

    class ROLE(Enum):
        NFP = 'national focal point'
        DS = 'donor state'
        PO = 'programme operator'
        DPP = 'donor programme partner'
        PP = 'programme partner'
        PJPT = 'project promoter'
        PJDPP = 'donor project partner'
        PJPP = 'project partner'

        class Labels:
            NFP = _('National Focal Point')
            DS = _('Donor State')
            PO = _('Programme Operator')
            DPP = _('Donor Programme Partner')
            PP = _('Programme Partner')
            PJPT = _('Project Promoter')
            PJDPP = _('Donor Project Partner')
            PJPP = _('Project Partner')

    organisation = models.ForeignKey(Organisation)
    role = EnumField(ROLE, max_length=23)

    # TODO 1: this shouldn't be stored in case the org is a project one
    # TODO 2: this makes no sense, both of them nullable
    programme = models.ForeignKey(Programme, null=True)
    # TODO: this structure smells
    project = models.ForeignKey(Project, null=True)

from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _

FM_EEA = 'EEA'
FM_NORWAY = 'NOR'
FM_EEA_FULL_NAME = 'EEA Grants'
FM_NORWAY_FULL_NAME = 'Norway Grants'
FINANCIAL_MECHANISMS = [
    (FM_EEA, 'EEA Grants'),
    (FM_NORWAY, 'Norway Grants'),
]
FINANCIAL_MECHANISMS_DICT = dict(FINANCIAL_MECHANISMS)
# TODO add table for financing periods?
FUNDING_PERIODS = [
    (1, '2004-2009'),
    (2, '2009-2014'),
    (3, '2014-2021'),
]
FUNDING_PERIODS_DICT = dict(FUNDING_PERIODS)


class NUTS(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    label = models.CharField(max_length=128)
    # TODO field to differentiate between NUTS in different periods?

    class Meta:
        ordering = ['code']
        verbose_name_plural = "NUTS"

    @property
    def level(self):
        """The NUTS level."""
        return len(self.code) - 2

    def __str__(self):
        return self.code


class State(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    url = models.TextField()

    def __str__(self):
        return self.name


# TODO have priority sectors changed between periods? i.e. same code, different names
class PrioritySector(models.Model):
    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)  # not unique


class ProgrammeArea(models.Model):
    # each PA code is duplicated for the 2 FM present now
    # TODO what are slogan elements?
    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=256)  # not unique because of FM
    short_name = models.CharField(max_length=32)  # not unique
    # order = models.SmallIntegerField()  # TODO where from?
    objective = models.TextField()

    priority_sector = models.ForeignKey(PrioritySector, on_delete=models.CASCADE)
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)


class Allocation(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    financial_mechanism = models.CharField(max_length=3, choices=FINANCIAL_MECHANISMS)

    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE, null=True)

    gross_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    net_allocation = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('state', 'programme_area', 'financial_mechanism', 'funding_period')


class Programme(models.Model):
    class Status:
        APPROVED = 'approved'
        IMPLEMENTATION = 'implementation'
        COMPLETED = 'completed'
        CLOSED = 'closed'
        WITHDRAWN = 'withdrawn'
        RETURNED = 'returned'
        CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (Status.APPROVED, _('Approved')),
        (Status.IMPLEMENTATION, _('Implementation')),
        (Status.COMPLETED, _('Completed')),
        (Status.CLOSED, _('Closed')),
        (Status.WITHDRAWN, _('Withdrawn')),
        (Status.RETURNED, _('Returned to po')),
        (Status.CANCELLED, _('Cancelled')),
    )

    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    states = models.ManyToManyField(State)
    # TODO see if we need to declare the m2m table explicitly
    programme_areas = models.ManyToManyField(ProgrammeArea)

    short_name = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=256)  # not unique

    status = models.CharField(max_length=16, choices=STATUS_CHOICES)

    url = models.CharField(max_length=256, null=True)
    summary = models.TextField()

    allocation_eea = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_norway = models.DecimalField(max_digits=15, decimal_places=2)
    co_financing = models.DecimalField(max_digits=15, decimal_places=2)

    is_tap = models.BooleanField(help_text='Technical Assistance Programme')
    is_bfp = models.BooleanField(help_text='Bilateral Fund Programme')

    @property
    def allocation(self):
        return self.allocation_eea + self.allocation_norway

    @property
    def is_eea(self):
        return self.allocation_eea != 0

    @property
    def is_norway(self):
        return self.allocation_norway != 0


class Project(models.Model):
    class Status:
        SIGNED = 'signed'
        PLANNED = 'planned'
        IN_PROGRESS = 'in progress'
        COMPLETED = 'completed'
        TERMINATED = 'terminated'
        NON_COMPLETED = 'non completed'
        PARTIALLY_COMPLETED = 'partially completed'

    STATUS_CHOICES = (
        (Status.SIGNED, _('Signed')),
        (Status.PLANNED, _('Planned')),
        (Status.IN_PROGRESS, _('In Progress')),
        (Status.COMPLETED, _('Completed')),
        (Status.TERMINATED, _('Terminated')),
        (Status.NON_COMPLETED, _('Non Completed')),
        (Status.PARTIALLY_COMPLETED, _('Partially Completed')),
    )

    # financial_mechanism = models.CharField(choices=FINANCIAL_MECHANISMS)
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=512)  # not unique
    status = models.CharField(max_length=19, choices=STATUS_CHOICES)

    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    programme_areas = models.ManyToManyField(ProgrammeArea)
    priority_sectors = models.ManyToManyField(PrioritySector)

    nuts_code = models.CharField(max_length=5)
    url = models.CharField(max_length=256, null=True)
    allocation = models.DecimalField(max_digits=15, decimal_places=2)
    is_eea = models.BooleanField()
    is_norway = models.BooleanField()
    has_ended = models.BooleanField()
    is_dpp = models.BooleanField()
    is_positive_fx = models.BooleanField()
    is_improved_knowledge = models.BooleanField()
    is_continued_coop = models.BooleanField()
    initial_description = models.TextField()
    results_description = models.TextField()


class ProjectTheme(models.Model):
    project = models.ForeignKey(Project, related_name='themes', on_delete=models.CASCADE)
    name = models.CharField(max_length=512)  # not unique


class ProgrammeIndicator(models.Model):
    # TODO refine this
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)

    indicator = models.CharField(max_length=256)
    outcome = models.CharField(max_length=256)

    result_text = models.CharField(max_length=300, default='')  # see "Well-functioning..."

    achievement = models.IntegerField()
    order = models.SmallIntegerField()

    def __str__(self):
        return "%s - %s" % (self.programme.code, self.indicator)


class OrganisationRole(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    role_code = models.CharField(max_length=8)
    role_name = models.CharField(max_length=64)

    organisation_country = models.CharField(max_length=64)
    organisation_name = models.CharField(max_length=256)

    nuts_code = models.CharField(max_length=5)  # FK to NUTS table?

    # programme and project are denormalised to include BS
    programme = models.ForeignKey(Programme, null=True, related_name='organisation_roles',
                                  on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, related_name='organisation_roles',
                                on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)  # TODO see if we need this


class BilateralInitiative(models.Model):
    class Level:
        COUNTRY = 'country'
        PROGRAMME = 'programme'

    LEVEL_CHOICES = (
        (Level.COUNTRY, _('Country')),
        (Level.PROGRAMME, _('Programme')),
    )

    class Status:
        COMPLETED = 'completed'
        COMPLETION_UNDER_REVIEW_FMO = 'compl review fmo'
        COMPLETION_UNDER_REVIEW_NFP = 'compl review nfp'
        DRAFT_COMPLETION = 'draft completion'
        ON_GOING = 'on-going'
        UNDER_REVIEW_FMO = 'review fmo'

    STATUS_CHOICES = (
        (Status.COMPLETED, _('Completed')),
        (Status.COMPLETION_UNDER_REVIEW_FMO, _('Completion under review by FMO')),
        (Status.COMPLETION_UNDER_REVIEW_NFP, _('Completion under review by NFP')),
        (Status.DRAFT_COMPLETION, _('Draft Completion')),
        (Status.ON_GOING, _('On-going')),
        (Status.UNDER_REVIEW_FMO, _('Under review by FMO')),
    )

    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    code = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=512)  # not unique

    programme = models.ForeignKey(Programme, related_name='bilateral_initiatives',
                                  on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, related_name='bilateral_initiatives',
                                on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    programme_areas = models.ManyToManyField(ProgrammeArea)

    level = models.CharField(max_length=16, choices=LEVEL_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)


class News(models.Model):
    title = models.TextField(null=False, blank=False)
    link = models.URLField(max_length=2000, null=False, blank=False)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(null=True)

    programmes = models.ManyToManyField(Programme, related_name='news')
    project = models.ForeignKey(Project, null=True, default=None, related_name='news',
                                on_delete=models.CASCADE, db_constraint=False)
    summary = models.TextField(null=True)
    image = models.URLField(max_length=2000)
    is_partnership = models.BooleanField(default=False)

    def __str__(self):
        return self.link

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = "news"


class StaticContent(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False, unique=True)
    body = RichTextField(null=False, blank=False)

    def __str__(self):
        return self.name

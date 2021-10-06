from ckeditor.fields import RichTextField
from django.db import models
from django.utils.functional import cached_property

from dv.lib.utils import FM_EEA, FM_NORWAY, FINANCIAL_MECHANISMS, FM_DICT, FUNDING_PERIODS, STATES


class NUTSVersion(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class NUTS(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    label = models.CharField(max_length=128)
    nuts_versions = models.ManyToManyField(NUTSVersion)

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
    name = models.CharField(max_length=64)
    url = models.TextField()

    def __str__(self):
        return self.name


class PrioritySector(models.Model):
    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)  # not unique


class ProgrammeArea(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    priority_sector = models.ForeignKey(PrioritySector, on_delete=models.CASCADE)

    code = models.CharField(max_length=4)  # not unique because of period
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=32)  # not unique
    order = models.SmallIntegerField(null=True)
    objective = models.TextField()

    class Meta:
        unique_together = ('funding_period', 'code')

    def __str__(self):
        return self.name


class Allocation(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    financial_mechanism = models.CharField(max_length=3, choices=FINANCIAL_MECHANISMS)

    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE, null=True, related_name="allocations")

    gross_allocation = models.DecimalField(max_digits=15, decimal_places=2)
    net_allocation = models.DecimalField(max_digits=15, decimal_places=2)

    thematic = models.CharField(max_length=16, blank=True)

    class Meta:
        unique_together = ('funding_period', 'state', 'programme_area', 'financial_mechanism')


class Programme(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    states = models.ManyToManyField(State)
    programme_areas = models.ManyToManyField(ProgrammeArea)

    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=256)  # not unique

    status = models.CharField(max_length=16)

    url = models.CharField(max_length=256, blank=True)
    summary = models.TextField()

    allocation_eea = models.DecimalField(max_digits=15, decimal_places=2)
    allocation_norway = models.DecimalField(max_digits=15, decimal_places=2)
    co_financing = models.DecimalField(max_digits=15, decimal_places=2)

    is_tap = models.BooleanField(help_text='Technical Assistance Programme')
    is_bfp = models.BooleanField(default=False, help_text='Bilateral Fund Programme')

    @property
    def allocation(self):
        return self.allocation_eea + self.allocation_norway

    @property
    def is_eea(self):
        return self.allocation_eea != 0

    @property
    def is_norway(self):
        return self.allocation_norway != 0

    @cached_property
    def financial_mechanisms(self):
        financial_mechanisms = []
        if self.is_eea:
            financial_mechanisms.append(FM_EEA)
        if self.is_norway:
            financial_mechanisms.append(FM_NORWAY)
        return financial_mechanisms

    @cached_property
    def financial_mechanisms_display(self):
        return [FM_DICT[fm] for fm in self.financial_mechanisms]

    @cached_property
    def display_name(self):
        return f"{self.code}: {' '.join(self.name.split())}"


class ProgrammeAllocation(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    financial_mechanism = models.CharField(max_length=3, choices=FINANCIAL_MECHANISMS)

    state = models.ForeignKey(State, on_delete=models.CASCADE)
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE, null=True)
    priority_sector = models.ForeignKey(PrioritySector, on_delete=models.CASCADE, null=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True)

    allocation = models.DecimalField(max_digits=15, decimal_places=2)

    thematic = models.CharField(max_length=16, blank=True)
    sdg_no = models.IntegerField(null=True)


class Project(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    code = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=512)  # not unique
    status = models.CharField(max_length=19)

    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    programme_areas = models.ManyToManyField(ProgrammeArea)
    priority_sectors = models.ManyToManyField(PrioritySector)

    nuts = models.ForeignKey(NUTS, on_delete=models.SET_NULL, null=True)
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

    @cached_property
    def financial_mechanisms(self):
        financial_mechanisms = []
        if self.is_eea:
            financial_mechanisms.append(FM_EEA)
        if self.is_norway:
            financial_mechanisms.append(FM_NORWAY)
        return financial_mechanisms

    @cached_property
    def financial_mechanisms_display(self):
        return [FM_DICT[fm] for fm in self.financial_mechanisms]

    @cached_property
    def geotarget(self):
        if not self.nuts:
            return []
        elif len(self.nuts.code) > 2:
            return [f"{self.nuts.code}: {self.nuts.label}, {STATES[self.nuts.code[:2]]}"]
        else:
            return [f"{self.nuts.code}: {self.nuts.label}"]

    @cached_property
    def display_name(self):
        return f"{self.code}: {' '.join(self.name.split())}"


class ProjectAllocation(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    financial_mechanism = models.CharField(max_length=3, choices=FINANCIAL_MECHANISMS)

    state = models.ForeignKey(State, on_delete=models.CASCADE)
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE)
    priority_sector = models.ForeignKey(PrioritySector, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    allocation = models.DecimalField(max_digits=15, decimal_places=2)


class ProjectTheme(models.Model):
    project = models.ForeignKey(Project, related_name='themes', on_delete=models.CASCADE)
    name = models.CharField(max_length=512)  # not unique


class Indicator(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name="indicators")
    programme_area = models.ForeignKey(ProgrammeArea, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)

    indicator = models.CharField(max_length=256)
    outcome = models.CharField(max_length=256)
    header = models.CharField(max_length=256)

    unit_of_measurement = models.CharField(max_length=8)

    achievement_eea = models.DecimalField(max_digits=9, decimal_places=2)
    achievement_norway = models.DecimalField(max_digits=9, decimal_places=2)
    order = models.SmallIntegerField(null=True)

    is_core = models.BooleanField(default=False)
    is_common = models.BooleanField(default=False)

    thematic = models.CharField(max_length=16, blank=True)
    sdg_no = models.IntegerField(null=True)

    def __str__(self):
        return "%s - %s" % (self.programme.code, self.indicator)

    @property
    def is_eea(self):
        return self.achievement_eea != 0

    @property
    def is_norway(self):
        return self.achievement_norway != 0


class Organisation(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)
    name = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    country = models.CharField(max_length=64)
    category = models.CharField(max_length=256)
    subcategory = models.CharField(max_length=256)
    nuts = models.ForeignKey(NUTS, on_delete=models.SET_NULL, null=True)

    @property
    def projects(self):
        return [role.project for role in self.roles.all() if role.project]

    @property
    def programmes(self):
        return [role.programme for role in self.roles.all() if role.programme]

    @cached_property
    def geotarget(self):
        if not self.nuts:
            return []
        elif len(self.nuts.code) > 2:
            return [f"{self.nuts.code}: {self.nuts.label}, {STATES[self.nuts.code[:2]]}"]
        else:
            return [f"{self.nuts.code}: {self.nuts.label}"]


class OrganisationRole(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    role_code = models.CharField(max_length=8)
    role_name = models.CharField(max_length=64)

    organisation = models.ForeignKey(Organisation, related_name='roles',
                                     on_delete=models.CASCADE)

    # programme and project are denormalised to include BS
    programme = models.ForeignKey(Programme, null=True, related_name='organisation_roles',
                                  on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, related_name='organisation_roles',
                                on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, on_delete=models.CASCADE)


class BilateralInitiative(models.Model):
    funding_period = models.IntegerField(choices=FUNDING_PERIODS)

    code = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=512)  # not unique
    url = models.CharField(max_length=256, blank=True)

    grant = models.DecimalField(max_digits=15, decimal_places=2)
    programme = models.ForeignKey(Programme, related_name='bilateral_initiatives',
                                  on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, related_name='bilateral_initiatives',
                                on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True,
                              related_name='bilateral_initiatives')
    programme_areas = models.ManyToManyField(ProgrammeArea)

    level = models.CharField(max_length=16)
    status = models.CharField(max_length=16)

    initial_description = models.TextField()
    results_description = models.TextField()

    promoter_state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    promoter_organization = models.CharField(max_length=256, blank=True)

    @cached_property
    def display_name(self):
        return f"{self.code}: {' '.join(self.title.split())}"


class News(models.Model):
    title = models.TextField()
    link = models.URLField(max_length=2000)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(null=True)

    programmes = models.ManyToManyField(Programme, related_name='news')
    project = models.ForeignKey(Project, null=True, default=None, related_name='news',
                                on_delete=models.CASCADE)
    summary = models.TextField(blank=True)
    image = models.URLField(max_length=2000)
    is_partnership = models.BooleanField(default=False)

    def __str__(self):
        return self.link

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = "news"


class StaticContent(models.Model):
    name = models.CharField(max_length=64, unique=True)
    body = RichTextField()

    def __str__(self):
        return self.name

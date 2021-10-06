from django.contrib import admin
from django.db.models.functions import Length
from .models import *


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = (
        'state',
        'programme_area',
        'financial_mechanism',
        'gross_allocation',
    )
    list_filter = ('funding_period', 'financial_mechanism', 'programme_area', 'state')
    search_fields = (
        'state__code', 'state__name',
        'programme_area__code', 'programme_area__name',
        'financial_mechanism'
    )


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('funding_period', 'programme', 'programme_area', 'state', 'indicator', 'header')
    search_fields = ('id', 'indicator')
    list_filter = ('funding_period',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    list_display = ('title', 'project', 'is_partnership', 'created', 'updated')
    list_filter = ('is_partnership', 'programmes', 'created')
    search_fields = (
        'title', 'summary', 'link',
        'project__code', 'project__name',
    )
    ordering = ('-created',)


class CountryFilter(admin.SimpleListFilter):
    title = 'Country code'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        nuts0 = (
            qs.annotate(code_len=Length('code'))
            .filter(code_len=2)
            .values('code', 'label')
            .distinct()
        )

        for nn in nuts0:
            yield nn['code'], f'{nn["code"]} ({nn["label"]})'

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(code__startswith=self.value())
        else:
            return queryset


@admin.register(NUTS)
class NutsAdmin(admin.ModelAdmin):
    list_display = ('code', 'label')
    list_filter = (CountryFilter,)
    search_fields = ('code', 'label')
    ordering = ('code',)


@admin.register(OrganisationRole)
class OrganisationRoleAdmin(admin.ModelAdmin):
    list_display = ('funding_period', 'programme', 'state')
    ordering = ('role_code',)


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'country', 'city',
        'category', 'subcategory',
    )
    list_filter = ('funding_period', 'category', 'country', 'subcategory', )
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(PrioritySector)
class PrioritySectorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
    search_fields = ('code', 'name')


@admin.register(ProgrammeArea)
class ProgrammeAreaAdmin(admin.ModelAdmin):
    list_display = (
        'priority_sector', 'code', 'name', 'short_name',
    )
    list_filter = ('funding_period', 'priority_sector', 'objective',)
    search_fields = ('code', 'name')
    ordering = ('order',)


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'get_states',
        'status', 'is_tap',
    )
    list_filter = ('funding_period', 'states', 'status', 'is_tap')
    search_fields = ('name',)
    ordering = ('code',)

    def get_states(self, obj):
        return "\n".join(p.name for p in obj.states.all())

    get_states.short_description = 'States'


@admin.register(ProjectTheme)
class ProjectThemeAdmin(admin.ModelAdmin):
    list_display = (
        'project', 'name',
    )
    list_filter = (
        'name',
        'project__priority_sectors',
        'project__state',
        'project__programme_areas',
    )
    search_fields = (
        'project__name',
    )
    ordering = ('project__code',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'allocation',
        'status', 'nuts', 'geotarget',
        'has_ended', 'is_dpp', 'is_positive_fx',
        'is_improved_knowledge', 'is_continued_coop',
    )
    list_filter = (
        'funding_period',
        'priority_sectors',
        'programme_areas',
        'state', 'status',
        'has_ended', 'is_dpp', 'is_positive_fx',
        'is_improved_knowledge', 'is_continued_coop',
    )
    search_fields = ('name',)
    ordering = ('code',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'url',)
    ordering = ('code',)


admin.site.register(BilateralInitiative)
admin.site.register(NUTSVersion)
admin.site.register(ProgrammeAllocation)
admin.site.register(ProjectAllocation)
admin.site.register(StaticContent)

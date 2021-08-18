# import inspect
# from django.contrib import admin
# from django.db import models
# from django.db.models.functions import Length
# from .models import *
#
#
# @admin.register(Allocation)
# class AllocationAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at', )
#     list_display = (
#         'state',
#         'programme_area',
#         'financial_mechanism',
#         'gross_allocation',
#         'updated_at'
#     )
#     list_filter = ('state', 'programme_area', 'financial_mechanism', 'updated_at')
#     search_fields = (
#         'state__code', 'state__name',
#         'programme_area__code', 'programme_area__name',
#         'financial_mechanism__code', 'financial_mechanism__name', 'financial_mechanism__grant_name',
#     )
#     ordering = ('order',)
#
#
# @admin.register(Indicator)
# class IndicatorAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at', )
#     list_display = ('code', 'name', 'updated_at')
#     search_fields = ('code', 'name')
#     ordering = ('-updated_at',)
#
#
# @admin.register(News)
# class NewsAdmin(admin.ModelAdmin):
#     readonly_fields = ('created', 'updated')
#     list_display = ('title', 'project', 'is_partnership', 'created', 'updated')
#     list_filter = ('is_partnership', 'programmes', 'created')
#     search_fields = (
#         'title', 'summary', 'link',
#         'project__code', 'project__name',
#     )
#     ordering = ('-created',)
#
#
# class CountryFilter(admin.SimpleListFilter):
#     title = 'Country code'
#     parameter_name = 'country'
#
#     def lookups(self, request, model_admin):
#         qs = model_admin.get_queryset(request)
#
#         nuts0 = (
#             qs.annotate(code_len=Length('code'))
#             .filter(code_len=2)
#             .values('code', 'label')
#             .distinct()
#         )
#         for nn in nuts0:
#             yield (nn['code'], '{} ({})'.format(nn['code'], nn['label']))
#
#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(code__startswith=self.value())
#         else:
#             return queryset
#
#
# @admin.register(NUTS)
# class NutsAdmin(admin.ModelAdmin):
#     list_display = ('code', 'label')
#     list_filter = (CountryFilter,)
#     search_fields = ('code', 'label')
#     ordering = ('code',)
#
#
# @admin.register(OrganisationRole)
# class OrganisationRoleAdmin(admin.ModelAdmin):
#     list_display = ('code', 'role')
#     ordering = ('code',)
#
#
# @admin.register(Organisation_OrganisationRole)
# class Organisation_OrganisationRoleAdmin(admin.ModelAdmin):
#
#     def org_name(self, obj):
#         return obj.organisation.name
#     org_name.admin_order_field = 'organisation__name'
#     org_name.short_description = 'Organisation name'
#
#     def org_id(self, obj):
#         return obj.organisation.id
#     org_id.admin_order_field = 'organisation__id'
#     org_id.short_description = 'Organisation ID'
#
#     def org_country(self, obj):
#         return obj.organisation.country
#     org_country.admin_order_field = 'organisation__country'
#     org_country.short_description = 'Country'
#
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'org_id', 'org_name', 'org_country',
#         'organisation_role_id', 'programme_id', 'project_id',
#         'is_programme', 'updated_at',
#     )
#     list_filter = ('organisation_role_id', 'organisation__country', 'programme_id')
#     search_fields = ('organisation__name', 'organisation__domestic_name')
#     ordering = ('organisation__id',)
#
#
# @admin.register(Organisation)
# class OrganisationAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'id', 'name', 'domestic_name',
#         'country', 'city',
#         'ptype', 'orgtypecateg', 'orgtype',
#     )
#     list_filter = ('ptype', 'country', 'orgtypecateg', 'orgtype')
#     search_fields = ('name', 'domestic_name')
#     ordering = ('id',)
#
#
# @admin.register(Outcome)
# class OutcomeAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'code', 'name', 'programme_area', 'fixed_budget_line',
#     )
#     list_filter = ('programme_area', 'fixed_budget_line')
#     search_fields = ('name',)
#     ordering = ('code',)
#
#
# @admin.register(PrioritySector)
# class PrioritySectorAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at', )
#     list_display = ('code', 'name', 'updated_at')
#     search_fields = ('code', 'name')
#     ordering = ('-updated_at',)
#
#
# @admin.register(ProgrammeArea)
# class ProgrammeAreaAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at', )
#     list_display = (
#         'code', 'name', 'short_name',
#         'financial_mechanism', 'priority_sector',
#         'is_not_ta',
#         'updated_at'
#     )
#     list_filter = ('financial_mechanism', 'priority_sector', 'is_not_ta')
#     search_fields = ('code', 'name')
#     ordering = ('order',)
#
#
# @admin.register(ProgrammeIndicator)
# class ProgrammeIndicatorAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at', )
#     list_display = (
#         'indicator',
#         'programme', 'programme_area', 'state',
#         'outcome', 'result_text', 'achievement',
#         'order', 'updated_at'
#     )
#     list_filter = ('state', 'programme_area', 'programme')
#     search_fields = ('indicator__code', 'indicator__name', 'outcome__name', 'result_text')
#     ordering = ('order',)
#
#
# @admin.register(ProgrammeOutcome)
# class ProgrammeOutcomeAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'programme', 'outcome', 'state', 'allocation', 'result_text'
#     )
#     list_filter = ('state', 'programme',)
#     search_fields = ('outcome__name',)
#     ordering = ('programme__code',)
#
#
# @admin.register(Programme_ProgrammeArea)
# class Programme_ProgrammeAreaAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'programme', 'programme_area'
#     )
#     list_filter = (
#         'programme_area__financial_mechanism',
#         'programme_area__priority_sector',
#         'programme__state',
#         'programme_area', 'programme',
#     )
#     search_fields = ('programme__name',)
#     ordering = ('programme__code',)
#
#
# @admin.register(Programme)
# class ProgrammeAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'code', 'name', 'state',
#         'status', 'is_tap',
#     )
#     list_filter = (
#         'state', 'status', 'is_tap',
#     )
#     search_fields = ('name',)
#     ordering = ('code',)
#
#
# @admin.register(ProjectTheme)
# class ProjectThemeAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'project', 'name',
#     )
#     list_filter = (
#         'name',
#         'project__financial_mechanism',
#         'project__priority_sector',
#         'project__state',
#         'project__programme_area',
#     )
#     search_fields = (
#         'project__name',
#     )
#     ordering = ('project__code',)
#
#
# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = (
#         'code', 'name', 'allocation',
#         'outcome',
#         'status', 'nuts', 'geotarget',
#         'has_ended', 'is_dpp', 'is_positive_fx',
#         'is_improved_knowledge', 'is_continued_coop',
#     )
#     list_filter = (
#         'financial_mechanism',
#         'priority_sector',
#         'programme_area',
#         'state', 'status',
#         'has_ended', 'is_dpp', 'is_positive_fx',
#         'is_improved_knowledge', 'is_continued_coop',
#         'updated_at',
#     )
#     search_fields = ('name',)
#     ordering = ('code',)
#
#
# @admin.register(State)
# class StateAdmin(admin.ModelAdmin):
#     readonly_fields = ('updated_at',)
#     list_display = ('code', 'name', 'url', 'updated_at')
#     ordering = ('code',)
#
#
# @admin.register(ImportLog)
# class ImportLogAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at', 'data', 'status')
#     list_display = ('created_at', 'updated_at', 'status')
#     ordering = ('-created_at',)
#
#
# # just register all the remaining models
# __models_module = '.'.join(__name__.split('.')[:-1] + ['models'])
# _models = [m for m in locals().values()
#            if inspect.isclass(m) and
#            m.__module__ == __models_module and
#            issubclass(m, models.Model) and
#            not (m._meta.abstract or m._meta.proxy)]
# for model in _models:
#     try:
#         admin.site.register(model)
#     except admin.sites.AlreadyRegistered:
#         pass

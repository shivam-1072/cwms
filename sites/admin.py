from django.contrib import admin
from .models import Site, Contractor, Subcontractor

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name', 'phone']

@admin.register(Subcontractor)
class SubcontractorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'site', 'contractor']
    list_filter = ['site', 'contractor']
    search_fields = ['name']

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'cubic_feet', 'square_feet', 'running_feet', 'status', 'contractor']
    list_filter = ['status', 'contractor']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'location', 'description', 'contractor')}),
        ('Measurements', {'fields': ('cubic_feet', 'square_feet', 'running_feet')}),
        ('Agreement Details', {'fields': ('agreement_file', 'agreement_date', 'agreement_party')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

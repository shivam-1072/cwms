from django.contrib import admin

# Register your models here.

from .models import Site

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']

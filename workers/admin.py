# Register your models here.

from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'joining_date', 'daily_wage']
    search_fields = ['name', 'phone']
    list_filter = ['joining_date']

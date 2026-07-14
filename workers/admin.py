from django.contrib import admin
from .models import Worker, Attendance, Payroll, Expense, WorkLog

# ===== Admin Site Customization =====
admin.site.site_header = "Administrator"
admin.site.site_title = "Construction MS Admin"
admin.site.index_title = "🏗️ Construction Management System"

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'joining_date', 'daily_wage', 'site', 'subcontractor']
    search_fields = ['name', 'phone']
    list_filter = ['site', 'subcontractor', 'joining_date']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['worker', 'date', 'status', 'is_far_site', 'extra_wage']
    list_filter = ['status', 'date', 'is_far_site']
    search_fields = ['worker__name']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['worker', 'month', 'working_days', 'gross_salary', 'deductions', 'net_salary']
    list_filter = ['month']
    search_fields = ['worker__name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['site', 'category', 'amount', 'date']
    list_filter = ['category', 'date', 'site']
    search_fields = ['description']

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['site', 'date', 'work_done', 'worker_count']
    list_filter = ['site', 'date']
    search_fields = ['work_done']
    filter_horizontal = ['workers']

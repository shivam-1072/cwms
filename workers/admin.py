from django.contrib import admin
from .models import Worker, Attendance, Payroll, Expense, WorkLog


# ===== Admin Site Customization =====
admin.site.site_header = "Administrator"
admin.site.site_title = "Construction MS Admin"
admin.site.index_title = "🏗️ Construction Management System"

# ===== Register Models =====
@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'joining_date', 'daily_wage', 'site']
    search_fields = ['name', 'phone']
    list_filter = ['site', 'joining_date']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['worker', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['worker__name']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['worker', 'month', 'working_days', 'gross_salary', 'net_salary']
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

from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Worker, Attendance, Payroll, Expense, WorkLog, IncomingPayment

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
    list_display = ['worker', 'date', 'status', 'extra_wage']
    list_filter = ['status', 'date']
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

@admin.register(IncomingPayment)
class IncomingPaymentAdmin(admin.ModelAdmin):
    list_display = ['site', 'amount', 'received_date']
    list_filter = ['site', 'received_date']
    search_fields = ['site__name', 'description']

# ===== CUSTOM ADMIN THEME =====
class CustomAdminSite(AdminSite):
    site_header = "Sompura Constructions Admin"
    site_title = "Sompura Admin"
    index_title = "🏗️ Construction Management System"

admin_site = CustomAdminSite(name='myadmin')

# Register all models with custom admin site
from .models import Worker, Attendance, Payroll, Expense, WorkLog, IncomingPayment
from sites.models import Site, Contractor, Subcontractor

admin_site.register(Worker)
admin_site.register(Attendance)
admin_site.register(Payroll)
admin_site.register(Expense)
admin_site.register(WorkLog)
admin_site.register(IncomingPayment)
admin_site.register(Site)
admin_site.register(Contractor)
admin_site.register(Subcontractor)
from django.urls import path
from . import views
from workers.admin import admin_site

urlpatterns = [
    
    path('admin/', admin_site.urls),
    
    # ========== AUTHENTICATION URLs ==========
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),  # Now shows confirmation
    
    # ========== WORKER URLs ==========
    path('', views.worker_list, name='worker_list'),
    path('create/', views.worker_create, name='worker_create'),
    path('<int:pk>/update/', views.worker_update, name='worker_update'),
    path('<int:pk>/delete/', views.worker_delete, name='worker_delete'),
    
    # ========== ATTENDANCE URLs ==========
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    
    # ========== PAYROLL URLs ==========
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/generate/', views.generate_payroll, name='generate_payroll'),
    path('payroll/export/', views.export_payroll_csv, name='export_payroll_csv'),
    
    # ========== EXPENSE URLs ==========
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # ========== DASHBOARD URL ==========
    path('dashboard/', views.dashboard, name='dashboard'),


    # ===== NEW: Attendance Summary URLs =====
    path('attendance/summary/', views.attendance_summary, name='attendance_summary'),
    path('attendance/export-summary/', views.attendance_export_summary, name='attendance_export_summary'),

     # ===== NEW: WorkLog URLs =====
    path('worklog/', views.worklog_list, name='worklog_list'),
    path('worklog/create/', views.worklog_create, name='worklog_create'),
    path('worklog/<int:pk>/update/', views.worklog_update, name='worklog_update'),
    path('worklog/<int:pk>/delete/', views.worklog_delete, name='worklog_delete'),

    # ====== Payslip ========
    path('payslip/', views.payslip_form, name='payslip_form'),
    path('payslip/generate/', views.generate_payslip, name='generate_payslip'),
    
    # ====== Incoming Payments ========
    path('incoming/', views.incoming_list, name='incoming_list'),
    path('incoming/create/', views.incoming_create, name='incoming_create'),
    
    
]

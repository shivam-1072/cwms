from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),

    path('', views.worker_list, name='worker_list'),
    path('create/', views.worker_create, name='worker_create'),
    path('<int:pk>/update/', views.worker_update, name='worker_update'),
    path('<int:pk>/delete/', views.worker_delete, name='worker_delete'),
    # Add these new lines
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),

    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/generate/', views.generate_payroll, name='generate_payroll'),
    path('payroll/export/', views.export_payroll_csv, name='export_payroll_csv'),

    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    path('dashboard/', views.dashboard, name='dashboard'),
]


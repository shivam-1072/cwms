from django.urls import path
from . import views

urlpatterns = [
    path('', views.worker_list, name='worker_list'),
    path('create/', views.worker_create, name='worker_create'),
    path('<int:pk>/update/', views.worker_update, name='worker_update'),
    path('<int:pk>/delete/', views.worker_delete, name='worker_delete'),
]

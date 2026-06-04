from django.urls import path
from django.shortcuts import redirect
from . import dashboard_views as views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('reviewer/', views.reviewer_dashboard, name='reviewer'),
    path('employer/', views.employer_dashboard, name='employer'),
    path('jobseeker/', views.jobseeker_dashboard, name='jobseeker'),
    path('profile/', lambda r: redirect('accounts:profile'), name='complete_profile'),
]

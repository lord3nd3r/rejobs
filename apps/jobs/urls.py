from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('jobs/post/', views.post_job, name='post'),
    path('jobs/<int:pk>/edit/', views.edit_job, name='edit'),
    path('jobs/<slug:slug>/', views.job_detail, name='detail'),
]

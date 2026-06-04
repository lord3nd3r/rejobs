from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('<slug:job_slug>/', views.apply, name='apply'),
    path('mine/', views.my_applications, name='mine'),
    path('detail/<int:pk>/', views.application_detail, name='detail'),
    path('job/<int:job_pk>/applicants/', views.job_applicants, name='job_applicants'),
]

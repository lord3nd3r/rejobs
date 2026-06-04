from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.reviewer_dashboard, name='dashboard'),
    path('assign/<int:application_pk>/', views.assign_review, name='assign'),
    path('<int:assignment_pk>/', views.review_application, name='review'),
]

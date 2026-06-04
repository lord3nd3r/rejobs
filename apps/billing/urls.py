from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('plans/', views.plans, name='plans'),
    path('checkout/<str:plan_tier>/', views.checkout, name='checkout'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('success/', views.checkout_success, name='success'),
]

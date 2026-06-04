from django.contrib import admin
from .models import Plan, EmployerSubscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'price_monthly', 'max_active_listings', 'is_active')
    list_filter = ('tier', 'is_active')


@admin.register(EmployerSubscription)
class EmployerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('employer', 'plan', 'status', 'current_period_end', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('employer__company_name', 'stripe_subscription_id')
    raw_id_fields = ('employer',)
    readonly_fields = ('created_at', 'updated_at')

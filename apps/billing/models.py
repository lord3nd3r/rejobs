from django.db import models
from django.utils import timezone


class Plan(models.Model):
    FREE = 'free'
    STARTER = 'starter'
    PROFESSIONAL = 'professional'
    ENTERPRISE = 'enterprise'
    TIER_CHOICES = [
        (FREE, 'Free'),
        (STARTER, 'Starter'),
        (PROFESSIONAL, 'Professional'),
        (ENTERPRISE, 'Enterprise'),
    ]

    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_active_listings = models.PositiveIntegerField(
        default=1,
        help_text='Maximum simultaneous active job listings.',
    )
    featured_listings_per_month = models.PositiveIntegerField(
        default=0,
        help_text='Number of featured listing slots included per month.',
    )
    stripe_price_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_monthly']

    def __str__(self):
        return f'{self.name} — ${self.price_monthly}/mo'

    @property
    def is_free(self):
        return self.tier == self.FREE


class EmployerSubscription(models.Model):
    ACTIVE = 'active'
    PAST_DUE = 'past_due'
    CANCELLED = 'cancelled'
    TRIALING = 'trialing'
    INCOMPLETE = 'incomplete'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (PAST_DUE, 'Past Due'),
        (CANCELLED, 'Cancelled'),
        (TRIALING, 'Trialing'),
        (INCOMPLETE, 'Incomplete'),
    ]

    employer = models.OneToOneField(
        'accounts.EmployerProfile',
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Employer Subscription'
        verbose_name_plural = 'Employer Subscriptions'

    def __str__(self):
        return f'{self.employer.company_name} — {self.plan.name}'

    @property
    def is_active(self):
        return self.status in (self.ACTIVE, self.TRIALING)

    @property
    def is_expired(self):
        if self.current_period_end:
            return timezone.now() > self.current_period_end
        return False

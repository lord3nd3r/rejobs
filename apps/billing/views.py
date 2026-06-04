import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def checkout_success(request):
    return render(request, 'billing/success.html')

from .models import Plan, EmployerSubscription

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def plans(request):
    active_plans = Plan.objects.filter(is_active=True)
    current_sub = None
    if request.user.is_employer_user:
        try:
            current_sub = request.user.employer_profile.subscription
        except (EmployerSubscription.DoesNotExist, Exception):
            pass
    return render(request, 'billing/plans.html', {
        'plans': active_plans,
        'current_sub': current_sub,
    })


@login_required
def checkout(request, plan_tier):
    if not request.user.is_employer_user:
        messages.error(request, 'Only employer accounts can subscribe to plans.')
        return redirect('billing:plans')

    plan = get_object_or_404(Plan, tier=plan_tier, is_active=True)
    if plan.is_free:
        # Assign free plan directly without Stripe
        sub, _ = EmployerSubscription.objects.update_or_create(
            employer=request.user.employer_profile,
            defaults={'plan': plan, 'status': EmployerSubscription.ACTIVE},
        )
        messages.success(request, f'Subscribed to the {plan.name} plan.')
        return redirect('dashboard:employer')

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Payment processing is not yet configured.')
        return redirect('billing:plans')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
            success_url=request.build_absolute_uri('/billing/success/'),
            cancel_url=request.build_absolute_uri('/billing/plans/'),
            metadata={'employer_id': request.user.employer_profile.pk, 'plan_tier': plan.tier},
        )
        return redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {e.user_message}')
        return redirect('billing:plans')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        employer_id = session.get('metadata', {}).get('employer_id')
        plan_tier = session.get('metadata', {}).get('plan_tier')
        if employer_id and plan_tier:
            from apps.accounts.models import EmployerProfile
            try:
                employer = EmployerProfile.objects.get(pk=employer_id)
                plan = Plan.objects.get(tier=plan_tier)
                EmployerSubscription.objects.update_or_create(
                    employer=employer,
                    defaults={
                        'plan': plan,
                        'stripe_subscription_id': session.get('subscription', ''),
                        'stripe_customer_id': session.get('customer', ''),
                        'status': EmployerSubscription.ACTIVE,
                    },
                )
            except Exception:
                pass

    return HttpResponse(status=200)

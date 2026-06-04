from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from apps.accounts.models import CustomUser, EmployerProfile, JobSeekerProfile
from apps.applications.models import Application
from apps.reviews.models import ReviewAssignment


def dashboard_home(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    user = request.user
    if user.is_admin_user:
        return redirect('dashboard:admin')
    if user.is_reviewer_user:
        return redirect('dashboard:reviewer')
    if user.is_employer_user:
        return redirect('dashboard:employer')
    return redirect('dashboard:jobseeker')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        return redirect('dashboard:home')

    # Applications with no review assignment yet
    assigned_app_ids = ReviewAssignment.objects.values_list('application_id', flat=True)
    unassigned = (
        Application.objects
        .exclude(pk__in=assigned_app_ids)
        .select_related('job__employer', 'applicant')
        .order_by('-applied_at')[:20]
    )

    # Recent assignments (all reviewers)
    recent_assignments = (
        ReviewAssignment.objects
        .select_related('application__job__employer', 'application__applicant', 'reviewer')
        .order_by('-assigned_at')[:10]
    )

    context = {
        'total_users': CustomUser.objects.count(),
        'total_employers': CustomUser.objects.filter(role=CustomUser.EMPLOYER).count(),
        'total_job_seekers': CustomUser.objects.filter(role=CustomUser.JOB_SEEKER).count(),
        'total_reviewers': CustomUser.objects.filter(role=CustomUser.REVIEWER).count(),
        'pending_reviews': ReviewAssignment.objects.filter(status=ReviewAssignment.PENDING).count(),
        'total_applications': Application.objects.count(),
        'unassigned_applications': unassigned,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def reviewer_dashboard(request):
    if not request.user.is_reviewer_user:
        return redirect('dashboard:home')
    assignments = (
        ReviewAssignment.objects
        .filter(reviewer=request.user)
        .select_related('application__job__employer', 'application__applicant')
        .order_by('status', '-assigned_at')
    )
    context = {
        'pending': assignments.filter(status=ReviewAssignment.PENDING),
        'in_progress': assignments.filter(status=ReviewAssignment.IN_PROGRESS),
        'completed': assignments.filter(status=ReviewAssignment.COMPLETED),
    }
    return render(request, 'dashboard/reviewer.html', context)


@login_required
def employer_dashboard(request):
    if not request.user.is_employer_user:
        return redirect('dashboard:home')
    try:
        profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        return redirect('dashboard:complete_profile')
    listings = profile.job_listings.order_by('-created_at')
    context = {
        'profile': profile,
        'listings': listings,
        'active_count': listings.filter(status='active').count(),
        'total_applications': Application.objects.filter(job__employer=profile).count(),
    }
    return render(request, 'dashboard/employer.html', context)


@login_required
def jobseeker_dashboard(request):
    if not request.user.is_job_seeker_user:
        return redirect('dashboard:home')
    applications = (
        request.user.applications
        .select_related('job__employer')
        .order_by('-applied_at')
    )
    context = {
        'applications': applications,
        'pending_count': applications.filter(status=Application.PENDING).count(),
        'under_review_count': applications.filter(status=Application.UNDER_REVIEW).count(),
        'shortlisted_count': applications.filter(status=Application.SHORTLISTED).count(),
    }
    return render(request, 'dashboard/jobseeker.html', context)

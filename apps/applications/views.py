from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.jobs.models import JobListing
from .forms import ApplicationForm, WorkExperienceFormSet, EducationFormSet, SkillFormSet
from .models import Application


@login_required
def apply(request, job_slug):
    if not request.user.is_job_seeker_user:
        messages.error(request, 'Only job seeker accounts can apply for jobs.')
        return redirect('jobs:detail', slug=job_slug)

    job = get_object_or_404(JobListing, slug=job_slug, status=JobListing.ACTIVE)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You have already applied for this position.')
        return redirect('jobs:detail', slug=job_slug)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        work_formset = WorkExperienceFormSet(request.POST, prefix='work')
        edu_formset = EducationFormSet(request.POST, prefix='edu')
        skill_formset = SkillFormSet(request.POST, prefix='skill')

        resume_method = request.POST.get('resume_method', 'upload')
        form_valid = form.is_valid()

        # Only validate builder formsets when using the built resume method
        if resume_method == 'build':
            formsets_valid = (
                work_formset.is_valid() and
                edu_formset.is_valid() and
                skill_formset.is_valid()
            )
        else:
            formsets_valid = True

        if form_valid and formsets_valid:
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            if resume_method == 'build':
                work_formset.instance = application
                edu_formset.instance = application
                skill_formset.instance = application
                work_formset.save()
                edu_formset.save()
                skill_formset.save()
            messages.success(request, 'Your application has been submitted.')
            return redirect('dashboard:jobseeker')
    else:
        form = ApplicationForm()
        work_formset = WorkExperienceFormSet(prefix='work')
        edu_formset = EducationFormSet(prefix='edu')
        skill_formset = SkillFormSet(prefix='skill')

    return render(request, 'applications/apply.html', {
        'job': job,
        'form': form,
        'work_formset': work_formset,
        'edu_formset': edu_formset,
        'skill_formset': skill_formset,
    })


@login_required
def my_applications(request):
    applications = (
        request.user.applications
        .select_related('job__employer')
        .order_by('-applied_at')
    )
    return render(request, 'applications/my_applications.html', {'applications': applications})


@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    # Applicant or reviewer/admin or the employer who owns the job can view
    is_owner = application.applicant == request.user
    is_reviewer_or_admin = request.user.is_reviewer_user or request.user.is_admin_user
    is_employer_owner = (
        request.user.is_employer_user
        and hasattr(request.user, 'employer_profile')
        and application.job.employer == request.user.employer_profile
    )
    if not (is_owner or is_reviewer_or_admin or is_employer_owner):
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('dashboard:home')
    return render(request, 'applications/detail.html', {'application': application})


@login_required
def job_applicants(request, job_pk):
    """Employer-only: list all applicants for one of their job listings."""
    if not request.user.is_employer_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    job = get_object_or_404(
        JobListing,
        pk=job_pk,
        employer=request.user.employer_profile,
    )
    applications = (
        job.applications
        .select_related('applicant')
        .prefetch_related('review_assignments')
        .order_by('-applied_at')
    )
    return render(request, 'applications/job_applicants.html', {
        'job': job,
        'applications': applications,
    })

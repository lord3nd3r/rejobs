from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import JobListing, JobCategory
from .forms import JobListingForm, JobSearchForm


def job_list(request):
    form = JobSearchForm(request.GET)
    listings = JobListing.objects.filter(status=JobListing.ACTIVE).select_related(
        'employer', 'category'
    )

    if form.is_valid():
        q = form.cleaned_data.get('q')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')
        work_mode = form.cleaned_data.get('work_mode')
        category_slug = form.cleaned_data.get('category')

        if q:
            listings = listings.filter(
                Q(title__icontains=q) |
                Q(employer__company_name__icontains=q) |
                Q(description__icontains=q)
            )
        if location:
            listings = listings.filter(
                Q(location__icontains=location) |
                Q(work_mode=JobListing.REMOTE)
            )
        if job_type:
            listings = listings.filter(job_type=job_type)
        if work_mode:
            listings = listings.filter(work_mode=work_mode)
        if category_slug:
            listings = listings.filter(category__slug=category_slug)

    featured = listings.filter(is_featured=True)[:3]
    paginator = Paginator(listings, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'jobs/list.html', {
        'form': form,
        'page': page,
        'featured': featured,
        'categories': JobCategory.objects.all(),
        'total': listings.count(),
    })


def job_detail(request, slug):
    job = get_object_or_404(JobListing, slug=slug, status=JobListing.ACTIVE)
    already_applied = False
    if request.user.is_authenticated and request.user.is_job_seeker_user:
        already_applied = job.applications.filter(applicant=request.user).exists()
    return render(request, 'jobs/detail.html', {
        'job': job,
        'already_applied': already_applied,
    })


@login_required
def post_job(request):
    if not request.user.is_employer_user:
        messages.error(request, 'Only employer accounts can post jobs.')
        return redirect('jobs:list')
    try:
        profile = request.user.employer_profile
    except Exception:
        messages.warning(request, 'Please complete your company profile first.')
        return redirect('dashboard:complete_profile')

    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.employer = profile
            listing.save()
            messages.success(request, 'Job listing saved.')
            return redirect('dashboard:employer')
    else:
        form = JobListingForm()
    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job(request, pk):
    listing = get_object_or_404(JobListing, pk=pk)
    if not request.user.is_employer_user or listing.employer.user != request.user:
        messages.error(request, 'You do not have permission to edit this listing.')
        return redirect('jobs:list')

    if request.method == 'POST':
        form = JobListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job listing updated.')
            return redirect('dashboard:employer')
    else:
        form = JobListingForm(instance=listing)
    return render(request, 'jobs/post_job.html', {'form': form, 'editing': True})

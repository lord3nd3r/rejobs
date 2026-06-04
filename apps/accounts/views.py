from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm, EmailAuthenticationForm, EmployerProfileForm, JobSeekerProfileForm
from .models import CustomUser, EmployerProfile, JobSeekerProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create the appropriate profile
            if user.role == CustomUser.EMPLOYER:
                EmployerProfile.objects.create(user=user, company_name='')
            elif user.role == CustomUser.JOB_SEEKER:
                JobSeekerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully. Please complete your profile.')
            return redirect('dashboard:complete_profile')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('jobs:list')


@login_required
def complete_profile_view(request):
    user = request.user
    if user.is_employer_user:
        profile, _ = EmployerProfile.objects.get_or_create(user=user, defaults={'company_name': ''})
        form_class = EmployerProfileForm
        template = 'accounts/employer_profile.html'
        instance = profile
    elif user.is_job_seeker_user:
        profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
        form_class = JobSeekerProfileForm
        template = 'accounts/jobseeker_profile.html'
        instance = profile
    else:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile saved.')
            return redirect('dashboard:home')
    else:
        form = form_class(instance=instance)
    return render(request, template, {'form': form})

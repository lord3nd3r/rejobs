from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.applications.models import Application
from .forms import ReviewNoteForm
from .models import ReviewAssignment, ReviewNote


def _require_reviewer_or_admin(user):
    return user.is_authenticated and (user.is_reviewer_user or user.is_admin_user)


@login_required
def reviewer_dashboard(request):
    if not _require_reviewer_or_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    assignments = (
        ReviewAssignment.objects
        .filter(reviewer=request.user)
        .select_related('application__job__employer', 'application__applicant')
        .prefetch_related('notes')
        .order_by('status', 'due_date')
    )
    return render(request, 'reviews/dashboard.html', {'assignments': assignments})


@login_required
def assign_review(request, application_pk):
    if not request.user.is_admin_user:
        messages.error(request, 'Only admins can assign reviews.')
        return redirect('dashboard:home')
    application = get_object_or_404(Application, pk=application_pk)
    from apps.accounts.models import CustomUser
    reviewers = CustomUser.objects.filter(role=CustomUser.REVIEWER, is_active=True)

    if request.method == 'POST':
        reviewer_id = request.POST.get('reviewer_id')
        due_date = request.POST.get('due_date') or None
        reviewer = get_object_or_404(CustomUser, pk=reviewer_id, role=CustomUser.REVIEWER)
        assignment, created = ReviewAssignment.objects.get_or_create(
            application=application,
            reviewer=reviewer,
            defaults={'due_date': due_date},
        )
        if created:
            # Update application status
            application.status = Application.UNDER_REVIEW
            application.save(update_fields=['status'])
            messages.success(request, f'Assigned to {reviewer.get_full_name()}.')
        else:
            messages.info(request, 'This reviewer is already assigned to this application.')
        return redirect('reviews:dashboard')

    return render(request, 'reviews/assign.html', {
        'application': application,
        'reviewers': reviewers,
    })


@login_required
def review_application(request, assignment_pk):
    if not _require_reviewer_or_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    assignment = get_object_or_404(
        ReviewAssignment,
        pk=assignment_pk,
        reviewer=request.user,
    )
    application = assignment.application

    if request.method == 'POST':
        form = ReviewNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.assignment = assignment
            note.save()
            # Update assignment status
            if assignment.status == ReviewAssignment.PENDING:
                assignment.status = ReviewAssignment.IN_PROGRESS
                assignment.save(update_fields=['status'])
            # If marked final, complete the assignment
            if note.is_final:
                assignment.mark_complete()
                application.status = Application.REVIEWED
                application.save(update_fields=['status'])
                messages.success(request, 'Review completed.')
                return redirect('reviews:dashboard')
            messages.success(request, 'Note saved.')
            return redirect('reviews:review', assignment_pk=assignment.pk)
    else:
        form = ReviewNoteForm()

    notes = assignment.notes.order_by('created_at')
    return render(request, 'reviews/review.html', {
        'assignment': assignment,
        'application': application,
        'form': form,
        'notes': notes,
    })

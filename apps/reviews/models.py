from django.db import models
from django.utils import timezone


class ReviewAssignment(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='review_assignments',
    )
    reviewer = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='review_assignments',
        limit_choices_to={'role': 'reviewer'},
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Review Assignment'
        verbose_name_plural = 'Review Assignments'
        unique_together = [('application', 'reviewer')]
        ordering = ['-assigned_at']

    def __str__(self):
        reviewer_email = self.reviewer.email if self.reviewer else 'Unassigned'
        return f'{self.application} → {reviewer_email}'

    def mark_complete(self):
        self.status = self.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])


class ReviewNote(models.Model):
    RECOMMEND = 'recommend'
    REJECT = 'reject'
    HOLD = 'hold'
    NEUTRAL = 'neutral'
    RECOMMENDATION_CHOICES = [
        (RECOMMEND, 'Recommend'),
        (REJECT, 'Reject'),
        (HOLD, 'Hold for Later'),
        (NEUTRAL, 'No Recommendation'),
    ]

    assignment = models.ForeignKey(
        ReviewAssignment,
        on_delete=models.CASCADE,
        related_name='notes',
    )
    note = models.TextField()
    recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        default=NEUTRAL,
    )
    is_final = models.BooleanField(
        default=False,
        help_text='Mark this as the final recommendation for this assignment.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Note ({self.recommendation}) on {self.assignment}'

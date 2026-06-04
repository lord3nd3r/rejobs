import os
from django.db import models
from django.utils import timezone


def resume_upload_path(instance, filename):
    """Store resumes under media/resumes/<user_id>/ with a timestamped filename."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'pdf'
    safe_name = f'resume_{int(timezone.now().timestamp())}.{ext}'
    return os.path.join('resumes', str(instance.applicant.id), safe_name)


class Application(models.Model):
    PENDING = 'pending'
    UNDER_REVIEW = 'under_review'
    REVIEWED = 'reviewed'
    SHORTLISTED = 'shortlisted'
    REJECTED = 'rejected'
    HIRED = 'hired'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (UNDER_REVIEW, 'Under Review'),
        (REVIEWED, 'Reviewed'),
        (SHORTLISTED, 'Shortlisted'),
        (REJECTED, 'Rejected'),
        (HIRED, 'Hired'),
    ]

    job = models.ForeignKey(
        'jobs.JobListing',
        on_delete=models.CASCADE,
        related_name='applications',
    )
    applicant = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='applications',
    )
    cover_letter = models.TextField(blank=True)

    # Option A: file upload
    resume_file = models.FileField(
        upload_to=resume_upload_path,
        null=True,
        blank=True,
        help_text='Upload PDF or DOCX (max 5 MB)',
    )

    # Option B: on-site builder — top-level fields
    resume_headline = models.CharField(max_length=200, blank=True)
    resume_summary = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-applied_at']
        unique_together = [('job', 'applicant')]

    def __str__(self):
        return f'{self.applicant.email} → {self.job.title}'

    @property
    def has_file_resume(self):
        return bool(self.resume_file)

    @property
    def has_built_resume(self):
        return bool(self.resume_headline or self.resume_summary)


class WorkExperience(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='work_experiences',
    )
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f'{self.job_title} at {self.company}'


class Education(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='educations',
    )
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_year']

    def __str__(self):
        return f'{self.degree} — {self.institution}'


class Skill(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
    PROFICIENCY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='skills',
    )
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, blank=True)

    def __str__(self):
        return self.name

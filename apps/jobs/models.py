from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class JobListing(models.Model):
    # Job type
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'
    TEMPORARY = 'temporary'
    INTERNSHIP = 'internship'
    JOB_TYPE_CHOICES = [
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time'),
        (CONTRACT, 'Contract'),
        (TEMPORARY, 'Temporary'),
        (INTERNSHIP, 'Internship'),
    ]

    # Listing status
    DRAFT = 'draft'
    ACTIVE = 'active'
    PAUSED = 'paused'
    CLOSED = 'closed'
    EXPIRED = 'expired'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (ACTIVE, 'Active'),
        (PAUSED, 'Paused'),
        (CLOSED, 'Closed'),
        (EXPIRED, 'Expired'),
    ]

    # Work mode
    ONSITE = 'onsite'
    REMOTE = 'remote'
    HYBRID = 'hybrid'
    WORK_MODE_CHOICES = [
        (ONSITE, 'On-site'),
        (REMOTE, 'Remote'),
        (HYBRID, 'Hybrid'),
    ]

    employer = models.ForeignKey(
        'accounts.EmployerProfile',
        on_delete=models.CASCADE,
        related_name='job_listings',
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_listings',
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default=FULL_TIME)
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default=ONSITE)
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    is_salary_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    is_featured = models.BooleanField(default=False)
    application_deadline = models.DateField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Listing'
        verbose_name_plural = 'Job Listings'
        ordering = ['-posted_at', '-created_at']

    def __str__(self):
        return f'{self.title} — {self.employer.company_name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.title}-{self.employer.company_name}')
            candidate = base
            counter = 1
            while JobListing.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{counter}'
                counter += 1
            self.slug = candidate
        if self.status == self.ACTIVE and not self.posted_at:
            self.posted_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status == self.ACTIVE

    @property
    def salary_display(self):
        if not self.is_salary_public:
            return 'Salary not disclosed'
        if self.salary_min and self.salary_max:
            return f'${self.salary_min:,.0f} – ${self.salary_max:,.0f} / yr'
        if self.salary_min:
            return f'From ${self.salary_min:,.0f} / yr'
        if self.salary_max:
            return f'Up to ${self.salary_max:,.0f} / yr'
        return 'Salary not listed'

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Manager that uses email as the unique identifier instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    REVIEWER = 'reviewer'
    EMPLOYER = 'employer'
    JOB_SEEKER = 'job_seeker'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (REVIEWER, 'Reviewer'),
        (EMPLOYER, 'Employer'),
        (JOB_SEEKER, 'Job Seeker'),
    ]

    # Override username: optional, non-unique (email is the login identifier)
    username = models.CharField(
        _('username'),
        max_length=150,
        blank=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOB_SEEKER)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return full or self.email

    @property
    def is_admin_user(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_reviewer_user(self):
        return self.role == self.REVIEWER

    @property
    def is_employer_user(self):
        return self.role == self.EMPLOYER

    @property
    def is_job_seeker_user(self):
        return self.role == self.JOB_SEEKER

    @property
    def display_role(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='employer_profile',
    )
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Employer Profile'
        verbose_name_plural = 'Employer Profiles'

    def __str__(self):
        return self.company_name


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='jobseeker_profile',
    )
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')
    summary = models.TextField(
        blank=True,
        help_text='Professional summary or objective statement',
    )
    linkedin_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Seeker Profile'
        verbose_name_plural = 'Job Seeker Profiles'

    def __str__(self):
        return self.user.get_full_name()

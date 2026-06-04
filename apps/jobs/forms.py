from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from .models import JobListing


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            'title', 'category', 'job_type', 'work_mode', 'location',
            'description', 'requirements', 'responsibilities',
            'salary_min', 'salary_max', 'salary_currency', 'is_salary_public',
            'application_deadline', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
            'requirements': forms.Textarea(attrs={'rows': 6}),
            'responsibilities': forms.Textarea(attrs={'rows': 6}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            Row(
                Column('category', css_class='col-md-4'),
                Column('job_type', css_class='col-md-4'),
                Column('work_mode', css_class='col-md-4'),
            ),
            'location',
            'description',
            'requirements',
            'responsibilities',
            Row(
                Column('salary_min', css_class='col-md-3'),
                Column('salary_max', css_class='col-md-3'),
                Column('salary_currency', css_class='col-md-2'),
                Column('is_salary_public', css_class='col-md-4 align-self-end'),
            ),
            Row(
                Column('application_deadline', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
            ),
            Submit('submit', 'Save Job Listing', css_class='btn btn-primary'),
        )


class JobSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Job title, keyword, or company'}),
    )
    location = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'City, state, or remote'}),
    )
    category = forms.CharField(required=False, widget=forms.HiddenInput)
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All types')] + JobListing.JOB_TYPE_CHOICES,
        label='Job type',
    )
    work_mode = forms.ChoiceField(
        required=False,
        choices=[('', 'All modes')] + JobListing.WORK_MODE_CHOICES,
        label='Work mode',
    )

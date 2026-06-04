from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from .models import CustomUser, EmployerProfile, JobSeekerProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    role = forms.ChoiceField(
        choices=[
            (CustomUser.EMPLOYER, 'I want to post jobs (Employer)'),
            (CustomUser.JOB_SEEKER, 'I am looking for work (Job Seeker)'),
        ],
        widget=forms.RadioSelect,
        label='Account type',
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            'role',
            'password1',
            'password2',
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100 mt-3'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email address', widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Sign In', css_class='btn btn-primary w-100 mt-3'),
        )


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'company_description', 'website',
            'phone', 'address', 'city', 'state', 'zip_code', 'country',
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'company_name',
            'company_description',
            Row(
                Column('website', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            'address',
            Row(
                Column('city', css_class='col-md-4'),
                Column('state', css_class='col-md-4'),
                Column('zip_code', css_class='col-md-4'),
            ),
            'country',
            Submit('submit', 'Save Profile', css_class='btn btn-primary'),
        )


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['phone', 'city', 'state', 'zip_code', 'country', 'summary', 'linkedin_url']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'summary',
            Row(
                Column('phone', css_class='col-md-6'),
                Column('linkedin_url', css_class='col-md-6'),
            ),
            Row(
                Column('city', css_class='col-md-4'),
                Column('state', css_class='col-md-4'),
                Column('zip_code', css_class='col-md-4'),
            ),
            'country',
            Submit('submit', 'Save Profile', css_class='btn btn-primary'),
        )

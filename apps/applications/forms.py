import os
from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML

from .models import Application, WorkExperience, Education, Skill


ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_RESUME_EXTENSIONS', ['.pdf', '.docx', '.doc'])


class ApplicationForm(forms.ModelForm):
    UPLOAD = 'upload'
    BUILD = 'build'
    RESUME_METHOD_CHOICES = [
        (UPLOAD, 'Upload a file (PDF or DOCX)'),
        (BUILD, 'Build resume on this site'),
    ]
    resume_method = forms.ChoiceField(
        choices=RESUME_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial=UPLOAD,
        label='How would you like to submit your resume?',
    )

    class Meta:
        model = Application
        fields = ['cover_letter', 'resume_file', 'resume_headline', 'resume_summary']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
            'resume_summary': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'resume_file': 'Resume file',
            'resume_headline': 'Professional headline',
            'resume_summary': 'Professional summary',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'resume_method',
            'cover_letter',
            HTML('<div id="upload-section">'),
            'resume_file',
            HTML('</div>'),
            HTML('<div id="build-section" style="display:none">'),
            'resume_headline',
            'resume_summary',
            HTML('</div>'),
            Submit('submit', 'Submit Application', css_class='btn btn-primary w-100 mt-3'),
        )

    def clean_resume_file(self):
        f = self.cleaned_data.get('resume_file')
        if f:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                )
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 5 MB.')
        return f


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_year', 'end_year', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency']


WorkExperienceFormSet = forms.inlineformset_factory(
    Application, WorkExperience, form=WorkExperienceForm, extra=1, can_delete=True
)
EducationFormSet = forms.inlineformset_factory(
    Application, Education, form=EducationForm, extra=1, can_delete=True
)
SkillFormSet = forms.inlineformset_factory(
    Application, Skill, form=SkillForm, extra=3, can_delete=True
)

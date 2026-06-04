from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import ReviewNote


class ReviewNoteForm(forms.ModelForm):
    class Meta:
        model = ReviewNote
        fields = ['note', 'recommendation', 'is_final']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'note',
            'recommendation',
            'is_final',
            Submit('submit', 'Save Review Note', css_class='btn btn-primary'),
        )

from django import forms

from .models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = (
            'exam_name',
            'subject',
            'semester',
            'exam_date',
            'start_time',
            'end_time',
            'status',
        )
        widgets = {
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'exam_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
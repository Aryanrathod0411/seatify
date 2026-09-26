from django import forms

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = (
            'name',
            'roll_number',
            'enrollment_number',
            'branch',
            'semester',
            'email',
        )
        widgets = {
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 12}),
        }
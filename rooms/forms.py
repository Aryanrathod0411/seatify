from django import forms
from django.db.models import Max

from seating.models import Seating
from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = (
            'room_number',
            'rows',
            'tables_per_row',
            'seats_per_table',
        )
        widgets = {
            'rows': forms.NumberInput(attrs={'min': 1}),
            'tables_per_row': forms.NumberInput(attrs={'min': 1}),
            'seats_per_table': forms.NumberInput(attrs={'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            return cleaned_data

        assigned_coordinates = Seating.objects.filter(
            room=self.instance
        ).aggregate(
            rows=Max('row_number'),
            tables=Max('table_number'),
            seats=Max('seat_number'),
        )
        for field, coordinate, label in (
            ('rows', 'rows', 'rows'),
            ('tables_per_row', 'tables', 'tables per row'),
            ('seats_per_table', 'seats', 'seats per table'),
        ):
            assigned_max = assigned_coordinates[coordinate]
            new_value = cleaned_data.get(field)
            if assigned_max is not None and new_value is not None and new_value < assigned_max:
                self.add_error(
                    field,
                    f"Room size cannot be smaller than its existing assigned {label}.",
                )

        return cleaned_data
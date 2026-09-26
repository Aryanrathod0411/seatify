from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=20, unique=True)
    rows = models.PositiveIntegerField()
    tables_per_row = models.PositiveIntegerField()
    seats_per_table = models.PositiveIntegerField(default=2)

    @property
    def capacity(self):
        return self.rows * self.tables_per_row * self.seats_per_table

    def __str__(self):
        return f"Room {self.room_number}"
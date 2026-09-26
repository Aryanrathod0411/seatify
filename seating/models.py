from django.db import models
from exams.models import Exam
from students.models import Student
from rooms.models import Room


class Seating(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    row_number = models.PositiveIntegerField()
    table_number = models.PositiveIntegerField()
    seat_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student.roll_number} - Room {self.room.room_number}"
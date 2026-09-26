from students.models import Student
from django.db import models


class Exam(models.Model):
    exam_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    semester = models.PositiveIntegerField()
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    students = models.ManyToManyField(Student, blank=True)

    branches = models.JSONField(default=list, blank=True)

    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    def __str__(self):
        return f"{self.subject} - Semester {self.semester}"



class TimetableUpload(models.Model):
    file = models.FileField(upload_to='timetables/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
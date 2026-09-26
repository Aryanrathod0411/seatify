from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    enrollment_number = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=100)
    semester = models.PositiveIntegerField()
    email = models.EmailField()

    def __str__(self):
        return f"{self.enrollment_number} - {self.name}"
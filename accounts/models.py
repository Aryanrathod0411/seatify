from django.db import models
from django.contrib.auth.models import User


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    faculty_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


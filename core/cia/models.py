from django.db import models
from django.contrib.auth.models import User
from main.models import Classroom

class CIARecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)
    cia_type = models.CharField(max_length=10)  # CIA1 / CIA2 / CIA3 / MOCK
    marks = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown'} - {self.cia_type}"

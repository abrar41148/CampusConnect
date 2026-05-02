from django.db import models
from django.contrib.auth.models import User
from main.models import Classroom

class AttendanceSession(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="attendance_sessions")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recorded_attendance_sessions")

    def __str__(self):
        return f"{self.classroom.name} - {self.date}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, null=True, blank=True, related_name="attendances")
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')
    time_marked = models.TimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown'} - {self.session.date if self.session else 'No Session'}"

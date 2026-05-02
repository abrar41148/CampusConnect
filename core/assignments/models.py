from django.db import models
from django.contrib.auth.models import User
from main.models import Classroom


class AssignmentQuerySet(models.QuerySet):

    def for_student(self, user):
        return self.filter(
            classroom__memberships__student=user
        )

    def for_teacher(self, user):
        return self.filter(
            classroom__teacher=user
        )


class Assignment(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="assignments/",
        null=True,
        blank=True
    )

    max_grade = models.PositiveIntegerField(default=100)
    
    allow_late_submissions = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = AssignmentQuerySet.as_manager()

    def __str__(self):
        return self.title


class AssignmentFile(models.Model):
    """Additional files attached to an assignment (multi-file support)."""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="extra_files"
    )
    file = models.FileField(upload_to="assignments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.assignment.title})"
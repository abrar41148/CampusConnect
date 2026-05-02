from django.db import models
from django.contrib.auth.models import User
from assignments.models import Assignment


class Submission(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(upload_to="submissions/", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)
    
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions"
    )

    feedback = models.TextField(blank=True)
    
    is_late = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class SubmissionFile(models.Model):
    """Additional files attached to a submission (multi-file support)."""
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="extra_files"
    )
    file = models.FileField(upload_to="submissions/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.submission.student.username})"
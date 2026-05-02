from django.db import models
from django.contrib.auth.models import User
from main.models import Classroom


class Resource(models.Model):

    title = models.CharField(max_length=200)

    content = models.TextField(
        blank=True
    )  # for announcements

    file = models.FileField(
        upload_to="resources/",
        blank=True,
        null=True
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="resources"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ResourceFile(models.Model):
    """Additional files attached to a resource/announcement (multi-file support)."""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="extra_files"
    )
    file = models.FileField(upload_to="resources/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.resource.title})"
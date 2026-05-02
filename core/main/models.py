from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role="student")


class Profile(models.Model):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    section = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

def generate_join_code():
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )
class Classroom(models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_classrooms")

    teachers = models.ManyToManyField(
        User,
        related_name="co_teaching_classrooms",
        blank=True
    )

    students = models.ManyToManyField(
        User,
        related_name="joined_classrooms",
        blank=True
    )

    join_code = models.CharField(
        max_length=8,
        unique=True,
        blank=True,
        null=True
    )


    def save(self, *args, **kwargs):
        if not self.join_code:
            # Retry on collision (unique constraint)
            for _ in range(10):
                code = generate_join_code()
                if not Classroom.objects.filter(join_code=code).exists():
                    self.join_code = code
                    break
            else:
                # Fallback: let the DB raise if still colliding after 10 tries
                self.join_code = generate_join_code()
        super().save(*args, **kwargs)

    def is_teacher(self, user):
        """Check if user is the owner or a co-teacher."""
        return self.teacher == user or self.teachers.filter(id=user.id).exists()

    def __str__(self):
        return self.name

class ClassroomMembership(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="classrooms_joined"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("classroom", "student")

    def __str__(self):
        return f"{self.student.username} -> {self.classroom.name}"

class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.user.username} - Read: {self.is_read}"

# --- Patch Django's default User model to allow spaces in usernames ---
from django.contrib.auth.validators import UnicodeUsernameValidator
import re

# Update the default validator class
UnicodeUsernameValidator.regex = re.compile(r'^[\w.@+ -]+\Z')
UnicodeUsernameValidator.message = 'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_/spaces.'

username_field = User._meta.get_field('username')
for validator in username_field.validators:
    if isinstance(validator, UnicodeUsernameValidator):
        validator.regex = re.compile(r'^[\w.@+ -]+\Z')
        validator.message = 'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_/spaces.'

username_field.help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_/spaces only.'

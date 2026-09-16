from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.JSONField(null=True, blank=True)  # Store analysis for history

    def __str__(self) -> str:
        return f"{self.user.username} - {self.file.name}"


class CareerGuidance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.TextField()
    suggested_careers = models.JSONField()  # Store AI results as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"


class SavedJob(models.Model):
    """
    User-bookmarked roles from the Explore Careers page.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_slug = models.CharField(max_length=200)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role_slug")
        indexes = [
            models.Index(fields=["user", "role_slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.role_slug}"


class ViewedRole(models.Model):
    """
    Used for activity timeline and "new jobs available" notifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_slug = models.CharField(max_length=200)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "role_slug", "viewed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.role_slug} at {self.viewed_at}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {'read' if self.is_read else 'unread'}"


class ResumeDraft(models.Model):
    """
    User-created resume / CV built from scratch using the Interactive Resume Builder.
    Supports real-time preview, multiple professional templates, theme colors, and ATS scanning.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_drafts')
    title = models.CharField(max_length=200, default='Untitled Resume')
    template_name = models.CharField(max_length=50, default='modern')  # modern, executive, minimal, creative
    theme_color = models.CharField(max_length=20, default='#2563eb')
    font_family = models.CharField(max_length=50, default='Inter')
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.title} ({self.template_name})"
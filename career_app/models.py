from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.JSONField(null=True, blank=True)  # Store analysis for history

class CareerGuidance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.TextField()
    suggested_careers = models.JSONField()  # Store AI results as JSON
    created_at = models.DateTimeField(auto_now_add=True)
from django.contrib import admin
from .models import Resume, CareerGuidance


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username',)


@admin.register(CareerGuidance)
class CareerGuidanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'skills')

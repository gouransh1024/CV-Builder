from django.contrib import admin
from .models import Resume, CareerGuidance, SavedJob, ViewedRole, Notification, ResumeDraft


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username', 'file')


@admin.register(CareerGuidance)
class CareerGuidanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'skills')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_slug', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'role_slug')


@admin.register(ViewedRole)
class ViewedRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_slug', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'role_slug')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')


@admin.register(ResumeDraft)
class ResumeDraftAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'template_name', 'theme_color', 'updated_at')
    list_filter = ('template_name', 'updated_at')
    search_fields = ('user__username', 'title')

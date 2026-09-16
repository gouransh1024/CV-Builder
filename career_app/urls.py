from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore_careers, name='explore_careers'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),
    path('guidance/', views.career_guidance, name='guidance'),
    path('analyzer/', views.resume_analyzer, name='analyzer'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='resume_delete'),
    path('resume/<int:resume_id>/download/', views.download_resume, name='resume_download'),

    # Resume / CV Builder Studio
    path('builder/', views.resume_builder, name='resume_builder'),
    path('resume-builder/', views.resume_builder, name='resume_builder_alias'),
    path('builder/<int:draft_id>/', views.resume_builder, name='resume_builder_edit'),
    path('api/builder/save/', views.api_save_resume_draft, name='api_builder_save'),
    path('api/builder/list/', views.api_list_resume_drafts, name='api_builder_list'),
    path('api/builder/<int:draft_id>/', views.api_get_resume_draft, name='api_builder_get'),
    path('api/builder/<int:draft_id>/delete/', views.api_delete_resume_draft, name='api_builder_delete'),
    path('api/builder/analyze/', views.api_analyze_draft_resume, name='api_builder_analyze'),

    # Interactive Explore Careers & Notifications API
    path('api/careers/', views.api_careers, name='api_careers'),
    path('api/role/<str:role_slug>/view/', views.api_view_role, name='api_role_view'),
    path('api/role/<str:role_slug>/bookmark/', views.api_toggle_bookmark, name='api_role_bookmark'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
]
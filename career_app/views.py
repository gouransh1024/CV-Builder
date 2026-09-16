import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .forms import SignUpForm, ResumeUploadForm, CareerGuidanceForm
from .models import Resume, CareerGuidance, SavedJob, ViewedRole, Notification, ResumeDraft
from .ml_models.resume_analyzer import analyze_resume, analyze_resume_text
from .ml_models.utils import get_career_suggestions
from .job_roles import list_roles, get_role_by_slug, get_apply_links
from .career_services import build_role_insights


def home(request):
    return render(request, 'home.html')


def signup(request):
    next_param = (request.POST.get('next') or request.GET.get('next') or '').strip()
    explicit_next = next_param if next_param and next_param not in ('dashboard', '/dashboard/') else ''
    redirect_target = next_param if next_param else 'dashboard'

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Smart Career Guidance.')
            return redirect(redirect_target)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'next': explicit_next})


def login_view(request):
    next_param = (request.POST.get('next') or request.GET.get('next') or '').strip()
    explicit_next = next_param if next_param and next_param not in ('dashboard', '/dashboard/') else ''
    redirect_target = next_param if next_param else 'dashboard'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html', {'next': explicit_next})
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(redirect_target)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {'next': explicit_next})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')


@login_required
def explore_careers(request):
    """
    Explore careers discovery page. Requires login.
    """
    return render(request, 'explore_careers.html', {
        'is_authenticated': request.user.is_authenticated
    })


def _latest_user_analysis(user):
    if not user or not getattr(user, "is_authenticated", False):
        return None
    resume = Resume.objects.filter(user=user, analysis_result__isnull=False).order_by("-uploaded_at").first()
    return resume.analysis_result if resume and resume.analysis_result else None


def _serialize_role(role, user_analysis=None, is_bookmarked=False):
    role_slug = role.get("slug")
    apply_links = get_apply_links(role)
    payload = {
        "slug": role_slug,
        "title": role.get("title"),
        "domain": role.get("domain"),
        "experience": role.get("experience"),
        "avg_salary_min": role.get("avg_salary_min"),
        "avg_salary_max": role.get("avg_salary_max"),
        "growth_trend": role.get("growth_trend"),
        "description": role.get("description"),
        "required_skills": role.get("required_skills", []),
        "apply_links": apply_links,
        "is_bookmarked": is_bookmarked,
    }
    if user_analysis:
        insights = build_role_insights(user_analysis, role)
        payload["match_percent"] = insights["match_percent"]
        payload["gap_analysis"] = {
            "missing_keywords": insights["missing_keywords"],
            "matched_keywords": insights["matched_keywords"],
        }
        payload["learning_path"] = insights["learning_path"]
    return payload


@login_required
def api_careers(request):
    """
    Careers API endpoint with query filtering and sorting. Requires login.
    """
    q = (request.GET.get("q") or "").strip().lower()
    domain = (request.GET.get("domain") or "").strip()
    exp = (request.GET.get("experience") or "").strip()
    sort = (request.GET.get("sort") or "demand").strip().lower()

    roles = list_roles()
    user_analysis = _latest_user_analysis(request.user) if request.user.is_authenticated else None
    bookmarks = set(
        SavedJob.objects.filter(user=request.user).values_list("role_slug", flat=True)
    ) if request.user.is_authenticated else set()

    def role_matches(r):
        if domain and r.get("domain") != domain:
            return False
        if exp and r.get("experience") != exp:
            return False
        if q:
            title = (r.get("title") or "").lower()
            desc = (r.get("description") or "").lower()
            required = " ".join(r.get("required_skills") or []).lower()
            if q not in title and q not in desc and q not in required:
                return False
        return True

    roles = [r for r in roles if role_matches(r)]

    def sort_key(r):
        if sort in ("salary", "highest_salary"):
            return (r.get("avg_salary_max") or 0)
        return (r.get("growth_trend") or 0)

    roles.sort(key=sort_key, reverse=True)

    result = [
        _serialize_role(r, user_analysis=user_analysis, is_bookmarked=(r["slug"] in bookmarks))
        for r in roles
    ]
    return JsonResponse({
        "roles": result,
        "is_authenticated": request.user.is_authenticated,
        "has_resume_analysis": bool(user_analysis),
    })


@login_required
def api_toggle_bookmark(request, role_slug: str):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Invalid method"}, status=405)
    role_slug = (role_slug or "").strip()
    if not role_slug:
        return JsonResponse({"ok": False, "message": "Missing role_slug"}, status=400)
    role = get_role_by_slug(role_slug)
    if not role:
        return JsonResponse({"ok": False, "message": "Unknown role"}, status=404)

    obj, created = SavedJob.objects.get_or_create(user=request.user, role_slug=role_slug)
    if not created:
        obj.delete()
        return JsonResponse({"ok": True, "bookmarked": False})
    return JsonResponse({"ok": True, "bookmarked": True})


@login_required
def api_view_role(request, role_slug: str):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Invalid method"}, status=405)
    role_slug = (role_slug or "").strip()
    if not role_slug:
        return JsonResponse({"ok": False, "message": "Missing role_slug"}, status=400)
    role = get_role_by_slug(role_slug)
    if not role:
        return JsonResponse({"ok": False, "message": "Unknown role"}, status=404)
    ViewedRole.objects.create(user=request.user, role_slug=role_slug)
    return JsonResponse({"ok": True})


@login_required
def api_notifications(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"ok": True})
    notifications = list(
        Notification.objects.filter(user=request.user).order_by("-created_at")[:20]
    )
    unread = sum(1 for n in notifications if not n.is_read)
    return JsonResponse({
        "ok": True,
        "unread_count": unread,
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "created_at": n.created_at.isoformat(),
                "is_read": n.is_read,
            }
            for n in notifications
        ],
    })


@login_required
def history(request):
    """Full history of career guidance, resume uploads, and resume drafts."""
    guidance_list = CareerGuidance.objects.filter(user=request.user).order_by('-created_at')
    resume_list = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    drafts_list = ResumeDraft.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'history.html', {
        'guidance_list': guidance_list,
        'resume_list': resume_list,
        'drafts_list': drafts_list,
    })


def _dashboard_context(user, tab='guidance', guidance_form=None, analyzer_form=None, analysis=None, suggestions=None, skills_submitted=''):
    resume_qs = Resume.objects.filter(user=user).order_by('-uploaded_at')
    recent_resumes = list(resume_qs[:20])
    resume_history = []
    for r in recent_resumes:
        result = r.analysis_result or {}
        resume_history.append({
            'id': r.id,
            'name': os.path.basename(r.file.name) if r.file else 'resume',
            'uploaded_at': r.uploaded_at.isoformat(),
            'uploaded_display': r.uploaded_at.strftime('%b %d, %Y %H:%M'),
            'score': result.get('score', 0),
            'skills_count': len(result.get('found_skills', [])),
            'download_url': f'/resume/{r.id}/download/',
        })
    drafts = ResumeDraft.objects.filter(user=user).order_by('-updated_at')[:5]
    return {
        'tab': tab,
        'guidance_form': guidance_form or CareerGuidanceForm(),
        'analyzer_form': analyzer_form or ResumeUploadForm(),
        'analysis': analysis,
        'suggestions': suggestions,
        'skills_submitted': skills_submitted,
        'recent_guidance': CareerGuidance.objects.filter(user=user).order_by('-created_at')[:5],
        'recent_resumes': recent_resumes[:5],
        'resume_history': resume_history,
        'recent_drafts': drafts,
    }


@login_required
def dashboard(request):
    context = _dashboard_context(request.user, tab=request.GET.get('tab', 'guidance'))
    return render(request, 'dashboard.html', context)


@login_required
def career_guidance(request):
    if request.method == 'POST':
        form = CareerGuidanceForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['skills'].strip()
            if not skills:
                messages.warning(request, 'Please enter at least one skill or interest.')
                return render(request, 'dashboard.html', _dashboard_context(request.user, tab='guidance', guidance_form=form))
            suggestions = get_career_suggestions(skills)
            CareerGuidance.objects.create(
                user=request.user,
                skills=skills,
                suggested_careers=suggestions
            )
            return render(
                request,
                'dashboard.html',
                _dashboard_context(request.user, tab='guidance', suggestions=suggestions, skills_submitted=skills),
            )
        return render(request, 'dashboard.html', _dashboard_context(request.user, tab='guidance', guidance_form=form))
    return redirect(f"{reverse('dashboard')}?tab=guidance")


@login_required
def resume_analyzer(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            target_role = form.cleaned_data.get('target_role', '')

            try:
                analysis = analyze_resume(resume.file.path, target_role=target_role)
            except Exception as e:
                analysis = {'error': f'Analysis failed: {str(e)}'}

            # If analysis errored, delete the invalid file and record to prevent orphan file accumulation
            if 'error' in analysis:
                if resume.file and os.path.exists(resume.file.path):
                    try:
                        resume.file.delete(save=False)
                    except Exception:
                        pass
                resume.delete()
                messages.error(request, analysis['error'])
                return render(request, 'dashboard.html', _dashboard_context(request.user, tab='analyzer', analyzer_form=form))

            previous = Resume.objects.filter(user=request.user, analysis_result__isnull=False).exclude(id=resume.id).order_by('-uploaded_at').first()
            if previous and previous.analysis_result:
                old_score = float(previous.analysis_result.get('score', 0))
                delta = round(float(analysis.get('score', 0)) - old_score, 1)
                analysis['score_change'] = delta
                if delta > 0:
                    messages.success(request, f'Your resume score improved by {delta}% compared to the previous upload.')
                elif delta < 0:
                    messages.warning(request, f'Current score is {abs(delta)}% lower than your previous upload.')

            if analysis.get('ats_issues'):
                messages.info(request, f"Attention: {analysis['ats_issues'][0]}")

            # Save analysis to DB
            resume.analysis_result = analysis
            resume.save(update_fields=['analysis_result'])

            # Persist notification with deduplication
            if "score_change" in analysis and float(analysis.get("score_change") or 0) != 0:
                delta = analysis.get("score_change")
                direction = "improved" if delta > 0 else "dropped"
                msg = f"Your resume score {direction} by {abs(delta)}%."
                if not Notification.objects.filter(user=request.user, message=msg, is_read=False).exists():
                    Notification.objects.create(user=request.user, message=msg)

            # Create new job matches notifications with deduplication
            user_analysis = resume.analysis_result or {}
            roles = list_roles()
            scored = []
            for r in roles:
                insights = build_role_insights(user_analysis, r)
                scored.append((insights["match_percent"], r))
            scored.sort(key=lambda x: x[0], reverse=True)
            top = [r for score, r in scored[:3] if score >= 70]
            saved_slugs = set(
                SavedJob.objects.filter(user=request.user).values_list("role_slug", flat=True)
            )
            for r in top:
                if r["slug"] in saved_slugs:
                    continue
                match_val = build_role_insights(user_analysis, r)['match_percent']
                msg = f"You have a {match_val}% match for {r['title']}."
                if not Notification.objects.filter(user=request.user, message=msg, is_read=False).exists():
                    Notification.objects.create(user=request.user, message=msg)

            return render(request, 'dashboard.html', _dashboard_context(request.user, tab='analyzer', analysis=analysis, analyzer_form=ResumeUploadForm()))
        messages.error(request, 'Upload validation error. Please upload a valid PDF, TXT, DOCX, or image (max 5MB).')
        return render(request, 'dashboard.html', _dashboard_context(request.user, tab='analyzer', analyzer_form=form))
    return redirect(f"{reverse('dashboard')}?tab=analyzer")


@login_required
def delete_resume(request, resume_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Invalid request method'}, status=405)
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    if resume.file and os.path.exists(resume.file.path):
        try:
            resume.file.delete(save=False)
        except Exception:
            pass
    resume.delete()
    return JsonResponse({'ok': True, 'message': 'Resume deleted successfully.'})


@login_required
def download_resume(request, resume_id):
    """
    Secure authenticated resume download view.
    Enforces that only the resume owner (or staff) can access the physical file.
    """
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Access denied: You do not own this resume.")

    if not resume.file or not os.path.exists(resume.file.path):
        raise Http404("Resume file not found.")

    filename = os.path.basename(resume.file.name)
    return FileResponse(open(resume.file.path, 'rb'), as_attachment=True, filename=filename)


# ==============================================================================
# INTERACTIVE RESUME / CV BUILDER (FROM SCRATCH TO PRO)
# ==============================================================================

@login_required
def resume_builder(request, draft_id=None):
    """
    Interactive Resume / CV Builder studio. Requires login.
    """
    active_draft = None
    if draft_id and request.user.is_authenticated:
        active_draft = ResumeDraft.objects.filter(id=draft_id, user=request.user).first()

    user_drafts = []
    if request.user.is_authenticated:
        user_drafts = list(ResumeDraft.objects.filter(user=request.user).order_by('-updated_at')[:15])

    return render(request, 'resume_builder.html', {
        'active_draft': active_draft,
        'active_draft_json': json.dumps(active_draft.data) if active_draft and active_draft.data else '{}',
        'user_drafts': user_drafts,
        'draft_id': active_draft.id if active_draft else '',
        'draft_title': active_draft.title if active_draft else 'My Professional Resume',
        'draft_template': active_draft.template_name if active_draft else 'modern',
        'draft_theme': active_draft.theme_color if active_draft else '#2563eb',
        'draft_font': active_draft.font_family if active_draft else 'Inter',
    })


@login_required
@require_POST
def api_save_resume_draft(request):
    """Save or update a resume draft."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'message': 'Invalid JSON'}, status=400)

    draft_id = payload.get('id')
    title = (payload.get('title') or 'Untitled Resume').strip()[:200]
    template_name = payload.get('template_name') or 'modern'
    theme_color = payload.get('theme_color') or '#2563eb'
    font_family = payload.get('font_family') or 'Inter'
    data = payload.get('data') or {}

    if draft_id:
        draft = ResumeDraft.objects.filter(id=draft_id, user=request.user).first()
        if not draft:
            return JsonResponse({'ok': False, 'message': 'Draft not found'}, status=404)
        draft.title = title
        draft.template_name = template_name
        draft.theme_color = theme_color
        draft.font_family = font_family
        draft.data = data
        draft.save()
    else:
        draft = ResumeDraft.objects.create(
            user=request.user,
            title=title,
            template_name=template_name,
            theme_color=theme_color,
            font_family=font_family,
            data=data
        )

    return JsonResponse({
        'ok': True,
        'id': draft.id,
        'title': draft.title,
        'message': 'Resume draft saved successfully.',
        'updated_at': draft.updated_at.strftime('%b %d, %Y %H:%M')
    })


@login_required
def api_list_resume_drafts(request):
    """List all saved resume drafts for current user."""
    drafts = ResumeDraft.objects.filter(user=request.user).order_by('-updated_at')
    return JsonResponse({
        'ok': True,
        'drafts': [
            {
                'id': d.id,
                'title': d.title,
                'template_name': d.template_name,
                'theme_color': d.theme_color,
                'updated_at': d.updated_at.strftime('%b %d, %Y %H:%M'),
            }
            for d in drafts
        ]
    })


@login_required
def api_get_resume_draft(request, draft_id: int):
    """Fetch full data for a specific resume draft."""
    draft = get_object_or_404(ResumeDraft, id=draft_id, user=request.user)
    return JsonResponse({
        'ok': True,
        'id': draft.id,
        'title': draft.title,
        'template_name': draft.template_name,
        'theme_color': draft.theme_color,
        'font_family': draft.font_family,
        'data': draft.data,
        'updated_at': draft.updated_at.strftime('%b %d, %Y %H:%M'),
    })


@login_required
@require_POST
def api_delete_resume_draft(request, draft_id: int):
    """Delete a resume draft."""
    draft = get_object_or_404(ResumeDraft, id=draft_id, user=request.user)
    draft.delete()
    return JsonResponse({'ok': True, 'message': 'Resume draft deleted.'})


@require_POST
def api_analyze_draft_resume(request):
    """
    Directly analyze the textual content of a resume draft with the ATS engine.
    Allows instant feedback while building the resume, without file upload.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'message': 'Invalid JSON'}, status=400)

    text = payload.get('text', '')
    target_role = payload.get('target_role', '')

    res = analyze_resume_text(text, target_role=target_role)
    if 'error' in res:
        return JsonResponse({'ok': False, 'message': res['error']}, status=400)

    return JsonResponse({
        'ok': True,
        'analysis': res
    })

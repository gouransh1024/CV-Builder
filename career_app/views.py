from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, ResumeUploadForm, CareerGuidanceForm
from .models import Resume, CareerGuidance
from .ml_models.resume_analyzer import analyze_resume
from .ml_models.utils import get_career_suggestions, SKILL_CAREER_MAP


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Welcome back!')
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def explore_careers(request):
    """Public page: browse skills and suggested careers."""
    skills_careers = [{'skill': k, 'careers': v} for k, v in sorted(SKILL_CAREER_MAP.items())]
    return render(request, 'explore_careers.html', {'skills_careers': skills_careers})


@login_required
def history(request):
    """Full history of career guidance and resume uploads for the user."""
    guidance_list = CareerGuidance.objects.filter(user=request.user).order_by('-created_at')
    resume_list = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'history.html', {
        'guidance_list': guidance_list,
        'resume_list': resume_list,
    })


@login_required
def dashboard(request):
    context = {
        'tab': request.GET.get('tab', 'guidance'),
        'guidance_form': CareerGuidanceForm(),
        'analyzer_form': ResumeUploadForm(),
        'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5],
        'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required
def career_guidance(request):
    if request.method == 'POST':
        form = CareerGuidanceForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['skills'].strip()
            if not skills:
                messages.warning(request, 'Please enter at least one skill or interest.')
                return render(request, 'dashboard.html', {'tab': 'guidance', 'guidance_form': form, 'analyzer_form': ResumeUploadForm(), 'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5], 'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5]})
            suggestions = get_career_suggestions(skills)
            CareerGuidance.objects.create(
                user=request.user,
                skills=skills,
                suggested_careers=suggestions
            )
            return render(request, 'dashboard.html', {
                'tab': 'guidance',
                'guidance_form': CareerGuidanceForm(),
                'analyzer_form': ResumeUploadForm(),
                'suggestions': suggestions,
                'skills_submitted': skills,
                'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5],
                'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5],
            })
        return render(request, 'dashboard.html', {'tab': 'guidance', 'guidance_form': form, 'analyzer_form': ResumeUploadForm(), 'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5], 'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5]})
    return redirect('dashboard' + '?tab=guidance')


@login_required
def resume_analyzer(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            try:
                analysis = analyze_resume(resume.file.path)
            except Exception as e:
                analysis = {'error': f'Analysis failed: {str(e)}'}
            if 'error' in analysis:
                messages.error(request, analysis['error'])
                return render(request, 'dashboard.html', {
                    'tab': 'analyzer',
                    'guidance_form': CareerGuidanceForm(),
                    'analyzer_form': form,
                    'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5],
                    'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5],
                })
            # Save analysis to DB for history
            resume.analysis_result = analysis
            resume.save(update_fields=['analysis_result'])
            return render(request, 'dashboard.html', {
                'tab': 'analyzer',
                'guidance_form': CareerGuidanceForm(),
                'analyzer_form': ResumeUploadForm(),
                'analysis': analysis,
                'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5],
                'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5],
            })
        messages.error(request, 'Invalid file. Use PDF, TXT, DOCX, or image (JPG, PNG, GIF, WEBP).')
        return render(request, 'dashboard.html', {
            'tab': 'analyzer',
            'guidance_form': CareerGuidanceForm(),
            'analyzer_form': form,
            'recent_guidance': CareerGuidance.objects.filter(user=request.user).order_by('-created_at')[:5],
            'recent_resumes': Resume.objects.filter(user=request.user).order_by('-uploaded_at')[:5],
        })
    return redirect('dashboard' + '?tab=analyzer')

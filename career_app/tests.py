import json
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Resume, CareerGuidance, SavedJob, Notification, ResumeDraft
from .ml_models.utils import get_career_suggestions
from .ml_models.resume_analyzer import analyze_resume_text
from smart_career_guidance.middleware import _is_safe_local_origin


class CareerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_create_resume_draft(self):
        draft = ResumeDraft.objects.create(
            user=self.user,
            title='Software Engineer Resume',
            template_name='modern',
            theme_color='#2563eb',
            font_family='Inter',
            data={'summary': 'Experienced developer'}
        )
        self.assertEqual(str(draft), 'testuser - Software Engineer Resume (modern)')
        self.assertEqual(draft.user, self.user)
        self.assertEqual(draft.data['summary'], 'Experienced developer')

    def test_saved_job_and_notification(self):
        job = SavedJob.objects.create(user=self.user, role_slug='software-developer')
        notif = Notification.objects.create(user=self.user, message='Welcome to Smart Career')
        self.assertEqual(str(job), 'testuser: software-developer')
        self.assertIn('unread', str(notif))


class MachineLearningGuidanceTests(TestCase):
    def test_ml_model_prediction(self):
        suggestions = get_career_suggestions("python django postgresql docker backend api")
        self.assertTrue(len(suggestions) > 0)
        # Should include relevant engineering titles
        tech_matches = [s for s in suggestions if any(k in s for k in ['Backend', 'Software', 'Engineer', 'Developer'])]
        self.assertTrue(len(tech_matches) > 0, f"Expected tech roles in {suggestions}")

    def test_stopword_bug_fixed_no_false_positives(self):
        # Previously 'in' caused 'interested in art' to falsely suggest 'Marketing' and 'Finance'
        suggestions = get_career_suggestions("interested in art")
        self.assertNotIn("Marketing Specialist", suggestions)
        self.assertNotIn("Financial Analyst", suggestions)

    def test_empty_input_fallback(self):
        suggestions = get_career_suggestions("")
        self.assertEqual(suggestions, ['General Professional', 'Career Coach recommended'])


class ResumeAnalyzerTests(TestCase):
    def test_analyze_resume_text_success(self):
        text = """
        Alex Morgan - Senior Software Engineer
        Experience: 4 years backend development with Python, Django, SQL, and Docker.
        Projects: Built scalable microservices architecture.
        Education: Bachelor of Science in Computer Science.
        Skills: Python, SQL, Docker, Git, Agile, React.
        """
        analysis = analyze_resume_text(text, target_role="software_developer")
        self.assertNotIn('error', analysis)
        self.assertTrue(analysis['score'] > 0)
        self.assertIn('python', analysis['found_skills'])
        self.assertTrue(analysis['sections_detected']['experience'])
        self.assertTrue(analysis['sections_detected']['projects'])
        self.assertTrue(analysis['sections_detected']['education'])

    def test_analyze_resume_text_too_short(self):
        analysis = analyze_resume_text("hello")
        self.assertIn('error', analysis)


class SecurityAndAccessTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password123')
        self.client = Client()

    def test_safe_local_origin_filter(self):
        # Valid origins
        self.assertTrue(_is_safe_local_origin('http://localhost:8000'))
        self.assertTrue(_is_safe_local_origin('http://127.0.0.1:8000'))
        self.assertTrue(_is_safe_local_origin('http://192.168.1.50:8000'))
        self.assertTrue(_is_safe_local_origin('http://10.0.0.12:8000'))

        # Attacker origins (substring tricks) MUST be rejected
        self.assertFalse(_is_safe_local_origin('http://localhost.evil.com'))
        self.assertFalse(_is_safe_local_origin('http://10.attacker.com'))
        self.assertFalse(_is_safe_local_origin('http://192.168.attacker.com'))
        self.assertFalse(_is_safe_local_origin('http://evil.com'))

    def test_cannot_download_other_user_resume(self):
        # Create a resume belonging to alice
        resume = Resume.objects.create(user=self.user1, file='resumes/alice_secret.pdf')
        # Login as bob
        self.client.force_login(self.user2)
        response = self.client.get(f'/resume/{resume.id}/download/')
        self.assertEqual(response.status_code, 403)

    def test_login_redirects_to_next(self):
        response = self.client.post('/login/?next=/explore/', {
            'username': 'alice',
            'password': 'password123'
        })
        self.assertRedirects(response, '/explore/')


class PublicExploreAndBuilderAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='charlie', password='password123')
        self.client = Client()

    def test_guest_redirected_to_login_for_explore(self):
        response = self.client.get('/explore/')
        self.assertRedirects(response, '/login/?next=/explore/')

        # Once logged in, user can access explore page and careers API
        self.client.force_login(self.user)
        response_auth = self.client.get('/explore/')
        self.assertEqual(response_auth.status_code, 200)

        response_api = self.client.get('/api/careers/')
        self.assertEqual(response_api.status_code, 200)
        data = response_api.json()
        self.assertTrue(len(data.get('roles', [])) > 0)
        self.assertTrue(data.get('is_authenticated'))

    def test_resume_builder_api_save_and_retrieve(self):
        self.client.force_login(self.user)
        # Save draft
        payload = {
            'title': 'Frontend Developer Resume',
            'template_name': 'creative',
            'theme_color': '#0f766e',
            'font_family': 'Outfit',
            'data': {
                'personal': {'name': 'Charlie Developer'},
                'skills': {'technical': 'React, TypeScript'}
            }
        }
        res = self.client.post(
            '/api/builder/save/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        draft_id = res.json().get('id')
        self.assertIsNotNone(draft_id)

        # Retrieve draft
        get_res = self.client.get(f'/api/builder/{draft_id}/')
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['title'], 'Frontend Developer Resume')

    def test_resume_builder_api_analyze(self):
        payload = {
            'text': 'Experienced Python Engineer with PostgreSQL and Docker. Built REST APIs. Bachelor in Science.',
            'target_role': 'software_developer'
        }
        res = self.client.post(
            '/api/builder/analyze/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])
        self.assertIn('score', res.json()['analysis'])

    def test_guest_redirected_to_login_for_builder(self):
        response = self.client.get('/builder/')
        self.assertRedirects(response, '/login/?next=/builder/')

    def test_login_page_renders_next_and_signup_link_preserves_next(self):
        response = self.client.get('/login/?next=/builder/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please sign in to access this feature')
        self.assertContains(response, '/signup/?next=/builder/')
        self.assertContains(response, '<input type="hidden" name="next" value="/builder/">')

    def test_signup_redirects_to_next(self):
        response = self.client.post('/signup/?next=/explore/', {
            'username': 'newexplorer',
            'email': 'new@example.com',
            'password1': 'ComplexPassword!123',
            'password2': 'ComplexPassword!123',
            'next': '/explore/'
        })
        self.assertRedirects(response, '/explore/')
        self.assertTrue(User.objects.filter(username='newexplorer').exists())

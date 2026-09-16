"""
Vercel Serverless Function entrypoint.
"""
import os
import sys

# Ensure workspace root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_career_guidance.settings')

from smart_career_guidance.wsgi import app, application

__all__ = ['app', 'application']

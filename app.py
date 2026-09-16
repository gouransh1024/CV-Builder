"""
Root app entrypoint for Vercel Python runtime.
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_career_guidance.settings')

from smart_career_guidance.wsgi import app, application

__all__ = ['app', 'application']

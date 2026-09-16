"""
Root WSGI entrypoint for Vercel and production deployment.
"""
import os
import sys

# Ensure workspace root is at the head of Python sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_career_guidance.settings')

from smart_career_guidance.wsgi import application, app

# Export both standard WSGI callable names
__all__ = ['application', 'app']

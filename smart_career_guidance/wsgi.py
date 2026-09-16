"""
WSGI config for smart_career_guidance project.

It exposes the WSGI callable as a module-level variable named ``application``.
For Vercel serverless deployments, it also exposes ``app``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_career_guidance.settings')

application = get_wsgi_application()
app = application

# On Vercel serverless, ensure database tables and seed users exist in /tmp
if os.environ.get('VERCEL'):
    from django.core.management import call_command
    try:
        call_command('migrate', interactive=False)
    except Exception as e:
        print('Vercel startup migration notice:', e)

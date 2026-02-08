@echo off
cd /d "%~dp0"
echo Starting Smart Career Guidance at http://127.0.0.1:8000/
python manage.py runserver

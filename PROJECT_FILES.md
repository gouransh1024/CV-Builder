# Project Files & Libraries

Quick reference for where each library is used and how to run the project.

## Install & Run

| Action | Command / File |
|--------|----------------|
| Install all libraries | `pip install -r requirements.txt` or run `install.bat` |
| Run migrations | `python manage.py migrate` |
| Start server | `python manage.py runserver` or run `run.bat` |
| Create admin user | `python manage.py createsuperuser` |

## Requirements (requirements.txt)

| Library | Purpose |
|---------|---------|
| Django | Web framework |
| scikit-learn | Optional ML model (career_guidance_model.pkl) |
| nltk | Resume text tokenization, stopwords |
| joblib | Load/save ML model in utils.py |
| PyPDF2 | PDF resume parsing in resume_analyzer.py |

## Where libraries are used

| File | Libraries / deps |
|------|------------------|
| `career_app/ml_models/resume_analyzer.py` | PyPDF2, nltk (word_tokenize, stopwords) |
| `career_app/ml_models/utils.py` | joblib, django.conf.settings |
| `career_app/views.py` | Django (shortcuts, auth, messages), app forms/models/ml_models |
| `career_app/forms.py` | Django forms, User, Resume |
| `career_app/models.py` | Django db, User |
| `career_app/admin.py` | Django admin, Resume, CareerGuidance |
| `smart_career_guidance/settings.py` | pathlib.Path |

## Main URLs

- `/` — Home
- `/explore/` — Explore careers (public)
- `/signup/`, `/login/`, `/logout/` — Auth
- `/dashboard/` — User dashboard (Career Guidance + Resume Analyzer)
- `/guidance/` — POST career guidance form
- `/analyzer/` — POST resume upload
- `/admin/` — Django admin

## Static assets

- `career_app/static/css/style.css` — Custom styles
- `career_app/static/js/scripts.js` — Tab and alert behavior
- Bootstrap 5 & Font Awesome loaded from CDN in `base.html`

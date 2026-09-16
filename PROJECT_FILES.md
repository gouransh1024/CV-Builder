# Project Files & Architecture Reference

Comprehensive reference for the Smart Career Guidance platform architecture, machine learning models, resume builder, and security endpoints.

## Quick Start & Run Commands

| Action | Command / File |
|--------|----------------|
| Install dependencies | `pip install -r requirements.txt` or run `install.bat` |
| Train/Retrain ML Model | `python career_app/ml_models/train.py` |
| Run migrations | `python manage.py migrate` |
| Run automated test suite | `python manage.py test` |
| Start development server | `python manage.py runserver` or run `run.bat` |
| Start network/mobile server | `run_network.bat` |
| Create admin user | `python manage.py createsuperuser` |

## Requirements (`requirements.txt`)

| Library | Purpose |
|---------|---------|
| Django (4.2.x) | Core web framework, ORM, authentication, CSRF security |
| scikit-learn (>=1.3) | TF-IDF vectorization & LogisticRegression career guidance ML pipeline |
| nltk (>=3.8) | Text tokenization, stopword removal, and keyword analysis |
| joblib (>=1.3) | High-performance serialization and caching of the trained ML model |
| PyPDF2 (>=3.0) | PDF resume document parsing |
| python-docx (>=1.0) | DOCX resume document parsing |
| Pillow (>=10.0) | Image processing support |

## Key Components

| Component | File Path | Description |
|-----------|-----------|-------------|
| **ML Training Pipeline** | `career_app/ml_models/train.py` | Trains TF-IDF + LogisticRegression NLP model on 80+ profiles across 37 careers |
| **ML Inference & Utils** | `career_app/ml_models/utils.py` | Cached model inference with fallback token-exact heuristics |
| **ATS Resume Analyzer** | `career_app/ml_models/resume_analyzer.py` | Multi-format parsing (PDF, DOCX, TXT), section detection, ATS scoring & keyword gap analysis |
| **Resume / CV Builder** | `career_app/templates/resume_builder.html`<br>`career_app/static/js/resume_builder.js`<br>`career_app/static/css/resume_templates.css` | Real-time reactive resume builder with 4 trending templates (Modern Tech, Executive, Minimal, Creative Split), color picker, PDF export, and direct ATS scanning |
| **Career Domain Services** | `career_app/career_services.py`<br>`career_app/job_roles.py` | Skill overlap calculation, gap analysis, dynamic learning path recommendations, and external job boards |
| **Security & Middleware** | `smart_career_guidance/middleware.py`<br>`smart_career_guidance/settings.py` | Strict IP-based dynamic CSRF trusted origin validator and secured media download access |
| **Test Suite** | `career_app/tests.py` | Automated tests for auth, guidance, analyzer, security, and builder |

## Main URLs

- `/` — Modern landing page
- `/explore/` — Explore careers (publicly accessible; personalized for authenticated users)
- `/builder/` — Interactive Resume & CV Builder studio
- `/builder/<id>/` — Edit existing saved resume draft
- `/dashboard/` — User dashboard (Career Guidance + ATS Resume Analyzer)
- `/history/` — User history (Career guidance sessions, uploaded resumes, and created CV drafts)
- `/guidance/` — POST career guidance form
- `/analyzer/` — POST resume file upload for ATS analysis
- `/resume/<id>/download/` — Authenticated, ownership-verified resume file download
- `/api/careers/` — Public & personalized careers JSON API
- `/api/builder/save/` — Save or update resume draft
- `/api/builder/analyze/` — Direct live ATS analysis of resume draft text
- `/admin/` — Django administrative portal

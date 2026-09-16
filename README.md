# Smart Career Guidance & CV Builder

An advanced, AI-powered web application for career path prediction, interactive ATS-ready CV/Resume building with modern industry templates, resume analysis, and tech career exploration.

## Key Features

- **Interactive CV / Resume Builder** – Build professional resumes from scratch with real-time preview, live ATS keyword scoring, instant PDF generation, and auto-saving drafts.
- **4 Trending Industry Templates** – Switch seamlessly between Modern Tech, Executive Leader, Tech Minimalist, and Creative Designer layouts.
- **AI Career Path Prediction** – Machine learning model (scikit-learn) recommending roles based on academic interests, skills, and work preferences.
- **ATS Resume Analyzer** – Multi-format parser (PDF, TXT, DOCX, Images) with skill gap analysis, ATS score, and tailored advice.
- **Explore 37+ Tech Careers** – Interactive career guide with skill tags, salary insights, growth outlook, and step-by-step roadmaps.
- **Automatic Theme Detection** – Synchronously detects browser/system dark or light theme (zero flash of unstyled content) with synchronized manual toggle.
- **Protected User Workflow** – Seamless login gating with automatic post-authentication redirects to chosen tools.

## Quick start (Windows)

1. **Install libraries and run migrations:**
   - Double-click `install.bat` (or run in terminal: `install.bat`)
   - This installs all dependencies from `requirements.txt` and runs migrations.

2. **Start the server:**
   - **Local only:** Double-click `run.bat` → Open http://127.0.0.1:8000/
   - **Network (phone access):** Double-click `run_network.bat` → Use the IP shown to access from other devices.

## Setup (manual)

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
   Enter username, email, and password. Use this to log in at **http://127.0.0.1:8000/admin/**.

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

6. Open **http://127.0.0.1:8000/** in your browser.

## Project structure

- `career_app/` – Main Django app
  - `views.py` – Home, signup, login, dashboard, career guidance, resume analyzer, explore careers
  - `models.py` – Resume, CareerGuidance
  - `forms.py` – SignUp, ResumeUpload, CareerGuidance
  - `ml_models/` – `resume_analyzer.py` (PDF/TXT parsing, NLTK), `utils.py` (career suggestions)
  - `templates/` – base, home, login, signup, dashboard, explore_careers
  - `static/` – CSS and JS
- `smart_career_guidance/` – Django project settings and URLs

## Requirements

- Python 3.8+
- Django 4.2
- NLTK, PyPDF2, scikit-learn, joblib (see `requirements.txt`)

## Admin

- **URL:** http://127.0.0.1:8000/admin/
- **Access:** Log in with a superuser account (create one with `python manage.py createsuperuser`).
- **Managed models:** Resume (user, file, uploaded_at), Career Guidance (user, skills, suggested careers, created_at). You can view, search, and filter all user uploads and guidance entries.

## Access from Other Devices (Phone, Tablet, etc.)

To use the app on your phone or other devices on the same Wi-Fi network:

1. **Find your computer's local IP address:**
   - Windows: Open Command Prompt and run `ipconfig`. Look for "IPv4 Address" (e.g., `192.168.1.100`).

2. **Start the server on all interfaces:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Or use `run_network.bat` (see below).

3. **On your phone/tablet:**
   - Connect to the same Wi-Fi network.
   - Open browser and go to: `http://YOUR_IP:8000` (e.g., `http://192.168.1.100:8000`).

4. **Install as app (PWA):**
   - On Android Chrome: Tap the menu (⋮) → "Add to Home screen".
   - On iOS Safari: Tap Share → "Add to Home Screen".

## Mobile & Cross-Device Features

- **Responsive design** – Works on phones (portrait/landscape), tablets, desktops.
- **Touch-friendly** – Large tap targets, no accidental zooms.
- **PWA support** – Install as an app on Android/iOS for quick access.
- **Dark mode** – Follows your device's system theme.
- **Safe areas** – Supports notched phones (iPhone X+, Android with notch).

## Notes

- Resume analyzer supports **PDF**, **TXT**, **DOCX**, and images (JPG, PNG, GIF, WEBP).
- Career suggestions use keyword-based logic; a pre-trained model can be added via `career_app/ml_models/` and `ML_MODEL_PATH` in settings.
- Media files (uploaded resumes) are stored under `media/resumes/`.

"""Resume analyzer: extract text and return ATS-focused resume insights."""
import os
import re
from collections import Counter

import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Optional: DOCX
try:
    from docx import Document as DocxDocument
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False

# Optional: Images (Pillow + pytesseract for OCR)
try:
    from PIL import Image
    import pytesseract
    _IMAGE_OCR_AVAILABLE = True
except ImportError:
    _IMAGE_OCR_AVAILABLE = False

def _ensure_nltk_data():
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab/english", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]
    for resource_path, package_name in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package_name, quiet=True)


_ensure_nltk_data()

KEY_SKILLS = [
    'python', 'java', 'javascript', 'marketing', 'leadership', 'data', 'analysis',
    'design', 'writing', 'sales', 'finance', 'teaching', 'communication', 'management',
    'creative', 'development', 'project', 'team', 'customer', 'research',
    'cloud', 'security', 'database', 'testing', 'networking', 'hr', 'legal',
    'healthcare', 'logistics', 'support', 'product', 'agile', 'excel', 'sql',
    'react', 'node',
]

SKILL_CATEGORIES = {
    "frontend": {"react", "javascript", "html", "css", "typescript", "redux", "next", "vue", "angular"},
    "backend": {"python", "java", "node", "django", "flask", "express", "api", "fastapi"},
    "database": {"sql", "mysql", "postgresql", "mongodb", "redis", "database"},
    "tools": {"git", "docker", "kubernetes", "jenkins", "aws", "azure", "excel", "agile"},
}

ROLE_KEYWORDS = {
    "software_developer": {"python", "java", "sql", "git", "api", "testing", "database"},
    "frontend_developer": {"react", "javascript", "html", "css", "typescript", "redux"},
    "backend_developer": {"python", "java", "node", "django", "flask", "api", "sql", "docker"},
    "data_analyst": {"python", "sql", "excel", "analysis", "statistics", "powerbi", "tableau"},
    "devops_engineer": {"docker", "kubernetes", "aws", "azure", "jenkins", "linux", "ci", "cd"},
    "product_manager": {"communication", "leadership", "agile", "roadmap", "analytics", "customer"},
}

SECTION_PATTERNS = {
    "projects": re.compile(r"\b(projects?|portfolio)\b", re.I),
    "education": re.compile(r"\b(education|bachelor|master|university|college|degree)\b", re.I),
    "experience": re.compile(r"\b(experience|employment|work history|internship)\b", re.I),
}

# Supported extensions for text extraction
TEXT_EXTENSIONS = ('.pdf', '.txt', '.docx', '.doc')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


def _extract_text_pdf(file_path):
    """Extract text from a PDF file."""
    text_parts = []
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            try:
                content = page.extract_text()
                if content:
                    text_parts.append(content)
            except Exception:
                pass
    return "\n".join(text_parts)


def _extract_text_txt(file_path):
    """Extract text from a plain text file."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def _extract_text_docx(file_path):
    """Extract text from a DOCX file."""
    if not _DOCX_AVAILABLE:
        return ""
    doc = DocxDocument(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text)


def _extract_text_image(file_path):
    """Extract text from an image using OCR (if available)."""
    if not _IMAGE_OCR_AVAILABLE:
        return None
    try:
        img = Image.open(file_path)
        if img.mode not in ('L', 'RGB', 'RGBA'):
            img = img.convert('RGB')
        return pytesseract.image_to_string(img)
    except Exception:
        return None


def _extract_tokens(text):
    normalized = text.lower()
    try:
        tokens = word_tokenize(normalized)
    except LookupError:
        tokens = re.findall(r"[a-z0-9]+", normalized)
    except Exception:
        raise
    return [t for t in tokens if t and t.isalnum()]


def _extract_resume_sections(text):
    lower = (text or "").lower()
    return {
        section: bool(pattern.search(lower))
        for section, pattern in SECTION_PATTERNS.items()
    }


def _categorize_skills(skills):
    grouped = {name: [] for name in SKILL_CATEGORIES.keys()}
    grouped["others"] = []
    for skill in skills:
        matched = False
        for category, bucket in SKILL_CATEGORIES.items():
            if skill in bucket:
                grouped[category].append(skill)
                matched = True
                break
        if not matched:
            grouped["others"].append(skill)
    return {k: sorted(list(dict.fromkeys(v))) for k, v in grouped.items()}


def _build_keyword_gap(found_skills, role_key):
    target = ROLE_KEYWORDS.get(role_key or "", set())
    if not target:
        return {"role": "", "match_percent": 0, "missing": [], "recommended": []}
    found_set = set(found_skills)
    matched = sorted(found_set.intersection(target))
    missing = sorted(target.difference(found_set))
    match_percent = round((len(matched) / max(1, len(target))) * 100, 1)
    return {
        "role": role_key,
        "match_percent": match_percent,
        "matched": matched,
        "missing": missing,
        "recommended": missing[:10],
    }


def _compute_score(found_skills, keywords, sections, role_gap):
    skill_relevance = (len(found_skills) / max(1, len(KEY_SKILLS))) * 45
    keyword_density = min(20, len(keywords) / 2.5)
    section_score = sum(10 for is_present in sections.values() if is_present)
    role_score = (role_gap.get("match_percent", 0) / 100) * 25 if role_gap.get("role") else 10
    total = round(min(100.0, skill_relevance + keyword_density + section_score + role_score), 1)
    return total


def _analyze_text(text, target_role=""):
    """Run keyword and ATS analysis on extracted text. Returns dict or None."""
    text = (text or "").strip()
    if not text:
        return None
    tokens = _extract_tokens(text)
    try:
        stop_words = set(stopwords.words('english'))
    except LookupError:
        stop_words = set()
    keywords = [
        w for w in tokens
        if w.isalnum() and w not in stop_words and len(w) > 2
    ]
    keywords_unique = list(dict.fromkeys(keywords))[:30]
    keyword_freq = Counter(keywords).most_common(12)
    found_skills = sorted([s for s in KEY_SKILLS if s in keywords])
    missing_skills = sorted([s for s in KEY_SKILLS if s not in found_skills])[:20]
    sections = _extract_resume_sections(text)
    categorized_skills = _categorize_skills(found_skills)
    role_gap = _build_keyword_gap(found_skills, target_role)
    score = _compute_score(found_skills, keywords, sections, role_gap)

    ats_issues = []
    if len(found_skills) < 6:
        ats_issues.append("Low role-specific skill coverage.")
    if len(keywords) < 35:
        ats_issues.append("Low keyword density for ATS scanners.")
    if not sections.get("experience"):
        ats_issues.append("Experience section looks missing or weak.")
    if not sections.get("projects"):
        ats_issues.append("Projects section not clearly detected.")

    suggestions = []
    if score < 40:
        suggestions.append("Add more role-aligned keywords across summary, skills, and experience.")
    if len(keywords) < 35:
        suggestions.append("Include more quantifiable achievements and action verbs.")
    if role_gap.get("missing"):
        suggestions.append(f"Add missing keywords for selected role: {', '.join(role_gap['missing'][:6])}.")
    if not sections.get("projects"):
        suggestions.append("Add a projects section with measurable outcomes.")
    suggestions.append("Tailor your resume to each job description for better results.")
    return {
        'keywords': keywords_unique,
        'keyword_frequency': [{"keyword": k, "count": c} for k, c in keyword_freq],
        'found_skills': found_skills,
        'missing_skills': missing_skills,
        'skill_categories': categorized_skills,
        'sections_detected': sections,
        'ats_issues': ats_issues,
        'role_analysis': role_gap,
        'score': score,
        'suggestions': " ".join(suggestions),
        'suggestions_list': suggestions,
    }


def analyze_resume(file_path, target_role=""):
    """
    Analyze a resume file (PDF, TXT, DOCX, or image). Returns a dict with:
    - keywords, found_skills, score, suggestions
    Or returns {'error': 'message'} on failure.
    For unsupported image formats without OCR, returns a saved message and score 0.
    """
    file_path = os.path.abspath(str(file_path))
    if not os.path.isfile(file_path):
        return {'error': 'File not found.'}

    path_lower = file_path.lower()
    text = ""

    if path_lower.endswith('.pdf'):
        try:
            text = _extract_text_pdf(file_path)
        except Exception as e:
            return {'error': f'Could not read PDF: {e}'}
    elif path_lower.endswith('.txt'):
        try:
            text = _extract_text_txt(file_path)
        except Exception as e:
            return {'error': f'Could not read file: {e}'}
    elif path_lower.endswith('.doc'):
        return {'error': 'Legacy .doc format is not supported. Please re-save or export your resume as .pdf or .docx.'}
    elif path_lower.endswith('.docx'):
        if not _DOCX_AVAILABLE:
            return {'error': 'DOCX support requires python-docx. Install: pip install python-docx'}
        try:
            text = _extract_text_docx(file_path)
        except Exception as e:
            return {'error': f'Could not read DOCX: {e}'}
    elif any(path_lower.endswith(ext) for ext in IMAGE_EXTENSIONS):
        text = _extract_text_image(file_path)
        if text is None or not text.strip():
            return {
                'keywords': [],
                'found_skills': [],
                'score': 0,
                'suggestions': 'File saved. For detailed text analysis, upload a PDF or DOCX resume.',
            }
        text = text.strip()
    else:
        return {'error': 'Unsupported file type. Use PDF, TXT, DOCX, or image (JPG, PNG, GIF, WEBP).'}

    result = _analyze_text(text, target_role=target_role)
    if result is None:
        return {'error': 'No text could be extracted from the file.'}
    return result


def analyze_resume_text(text: str, target_role: str = "") -> dict:
    """
    Directly analyze resume text content without requiring a physical file upload.
    Used by the Interactive Resume/CV Builder for instantaneous ATS scoring.
    """
    clean_text = (text or "").strip()
    if not clean_text or len(clean_text) < 20:
        return {
            'error': 'Please enter more content (at least summary, skills, or experience) to analyze your resume.'
        }
    res = _analyze_text(clean_text, target_role=target_role)
    if not res:
        return {'error': 'Could not extract sufficient keywords for analysis.'}
    return res

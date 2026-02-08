"""Resume analyzer: extract text from PDF, TXT, DOCX, and images; analyze keywords/skills."""
import os

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

# Ensure NLTK data is available (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

KEY_SKILLS = [
    'python', 'java', 'javascript', 'marketing', 'leadership', 'data', 'analysis',
    'design', 'writing', 'sales', 'finance', 'teaching', 'communication', 'management',
    'creative', 'development', 'project', 'team', 'customer', 'research',
    'cloud', 'security', 'database', 'testing', 'networking', 'hr', 'legal',
    'healthcare', 'logistics', 'support', 'product', 'agile', 'excel', 'sql',
    'react', 'node',
]

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


def _analyze_text(text):
    """Run keyword/skill analysis on extracted text. Returns dict or None."""
    text = (text or "").strip()
    if not text:
        return None
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [
        w for w in tokens
        if w.isalnum() and w not in stop_words and len(w) > 2
    ]
    keywords_unique = list(dict.fromkeys(keywords))[:25]
    found_skills = [s for s in KEY_SKILLS if s in keywords]
    score = 0.0
    if KEY_SKILLS:
        score = (len(found_skills) / len(KEY_SKILLS)) * 100
    score = score + min(20, len(keywords) / 5)
    score = round(min(100.0, score), 1)
    suggestions = []
    if score < 40:
        suggestions.append("Add more relevant skills and keywords to improve ATS compatibility.")
    if len(keywords) < 30:
        suggestions.append("Include more quantifiable achievements and action verbs.")
    suggestions.append("Tailor your resume to each job description for better results.")
    return {
        'keywords': keywords_unique,
        'found_skills': found_skills,
        'score': score,
        'suggestions': " ".join(suggestions),
    }


def analyze_resume(file_path):
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
    elif path_lower.endswith('.docx') or path_lower.endswith('.doc'):
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

    result = _analyze_text(text)
    if result is None:
        return {'error': 'No text could be extracted from the file.'}
    return result

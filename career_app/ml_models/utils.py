import re
from pathlib import Path
from typing import Any, List, Optional
import joblib

try:
    from django.conf import settings
except ImportError:
    settings = None

# Extended skill-to-career mapping for rich suggestions
SKILL_CAREER_MAP = {
    'python': ['Software Developer', 'Data Scientist', 'Backend Engineer', 'DevOps Engineer', 'ML Engineer'],
    'java': ['Software Engineer', 'Android Developer', 'Enterprise Developer', 'Backend Developer'],
    'javascript': ['Frontend Developer', 'Full Stack Developer', 'Web Developer', 'Node.js Developer'],
    'marketing': ['Marketing Specialist', 'Digital Marketing Manager', 'Content Strategist', 'SEO Specialist', 'Growth Hacker'],
    'leadership': ['Project Manager', 'Team Lead', 'Operations Manager', 'Program Manager', 'Scrum Master'],
    'data': ['Data Analyst', 'Data Scientist', 'Business Intelligence Analyst', 'Data Engineer', 'Analytics Manager'],
    'analysis': ['Business Analyst', 'Data Analyst', 'Research Analyst', 'Financial Analyst', 'Product Analyst'],
    'design': ['UI/UX Designer', 'Graphic Designer', 'Product Designer', 'Visual Designer', 'Interaction Designer'],
    'writing': ['Content Writer', 'Technical Writer', 'Copywriter', 'Editor', 'Content Strategist'],
    'sales': ['Sales Representative', 'Account Manager', 'Business Development', 'Sales Engineer', 'Channel Manager'],
    'finance': ['Financial Analyst', 'Accountant', 'Investment Analyst', 'Controller', 'Treasury Analyst'],
    'teaching': ['Educator', 'Corporate Trainer', 'Curriculum Developer', 'Instructional Designer', 'E-Learning Specialist'],
    'communication': ['Public Relations', 'Communications Manager', 'Community Manager', 'Internal Communications', 'Media Relations'],
    'management': ['Project Manager', 'Product Manager', 'Operations Manager', 'General Manager', 'Department Head'],
    'creative': ['Creative Director', 'Brand Manager', 'Marketing Manager', 'Art Director', 'Campaign Manager'],
    'development': ['Software Developer', 'Application Developer', 'Systems Developer', 'Integration Developer'],
    'project': ['Project Manager', 'Project Coordinator', 'Program Manager', 'Delivery Manager'],
    'team': ['Team Lead', 'Team Manager', 'Department Head', 'People Manager'],
    'customer': ['Customer Success Manager', 'Account Manager', 'Support Lead', 'Client Relations'],
    'research': ['Research Analyst', 'Market Researcher', 'UX Researcher', 'Data Scientist', 'Research Scientist'],
    'cloud': ['Cloud Architect', 'DevOps Engineer', 'Solutions Architect', 'Cloud Developer'],
    'security': ['Security Analyst', 'Cybersecurity Specialist', 'InfoSec Engineer', 'Penetration Tester'],
    'database': ['Database Administrator', 'Data Engineer', 'DBA', 'Analytics Engineer'],
    'testing': ['QA Engineer', 'Test Engineer', 'Automation Engineer', 'SDET'],
    'networking': ['Network Engineer', 'Systems Administrator', 'Infrastructure Engineer'],
    'hr': ['HR Manager', 'Recruiter', 'Talent Acquisition', 'HR Business Partner', 'People Operations'],
    'legal': ['Legal Counsel', 'Compliance Officer', 'Contract Manager', 'Paralegal'],
    'healthcare': ['Healthcare Administrator', 'Clinical Manager', 'Health Informatics', 'Medical Writer'],
    'logistics': ['Supply Chain Manager', 'Logistics Coordinator', 'Procurement Specialist', 'Operations Analyst'],
    'support': ['Technical Support', 'Customer Support Lead', 'Help Desk Manager', 'Support Engineer'],
    'product': ['Product Manager', 'Product Owner', 'Product Designer', 'Product Analyst'],
    'agile': ['Scrum Master', 'Agile Coach', 'Product Owner', 'Release Manager'],
    'excel': ['Business Analyst', 'Financial Analyst', 'Data Analyst', 'Operations Analyst'],
    'sql': ['Data Analyst', 'Data Engineer', 'Business Intelligence Analyst', 'Database Developer'],
    'react': ['Frontend Developer', 'React Developer', 'Full Stack Developer', 'UI Developer'],
    'node': ['Backend Developer', 'Full Stack Developer', 'Node.js Developer', 'API Developer'],
}

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
    'want', 'like', 'interested', 'good', 'skills', 'experience'
}

_CACHED_MODEL: Any = None


def _get_model() -> Any:
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    model_path = None
    try:
        if settings is not None and settings.configured:
            model_path = getattr(settings, 'ML_MODEL_PATH', None)
    except Exception:
        model_path = None
    if not model_path:
        base_dir = Path(__file__).resolve().parent
        model_path = base_dir / 'career_guidance_model.pkl'

    if model_path and Path(model_path).exists() and Path(model_path).stat().st_size > 0:
        try:
            _CACHED_MODEL = joblib.load(model_path)
            return _CACHED_MODEL
        except Exception:
            return None
    return None


def get_career_suggestions(skills_text: Optional[str] = None) -> List[str]:
    """
    Return a list of career suggestions based on skills/interests text.
    Combines authentic ML model classification with safe keyword heuristics.
    """
    clean_text = (skills_text or '').strip()
    if not clean_text:
        return ['General Professional', 'Career Coach recommended']

    seen = set()
    results = []

    # 1. Authentic ML model predictions
    model = _get_model()
    if model is not None:
        try:
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba([clean_text.lower()])[0]
                top_indices = probas.argsort()[-5:][::-1]
                for idx in top_indices:
                    career = str(model.classes_[idx])
                    if probas[idx] > 0.03 and career not in seen:
                        seen.add(career)
                        results.append(career)
            else:
                pred = model.predict([clean_text.lower()])
                for p in (pred if hasattr(pred, '__iter__') and not isinstance(pred, str) else [str(pred)]):
                    p_str = str(p)
                    if p_str not in seen:
                        seen.add(p_str)
                        results.append(p_str)
        except Exception:
            pass

    # 2. Heuristic skill matching with tokenization & stopword elimination
    tokens = [
        t for t in re.findall(r'[a-zA-Z0-9+#.]+', clean_text.lower())
        if len(t) > 1 and t not in STOPWORDS
    ]

    for token in tokens:
        for skill_key, careers in SKILL_CAREER_MAP.items():
            # Exact token match or token contains full skill key (e.g. "python3" contains "python")
            if token == skill_key or (len(token) > len(skill_key) and skill_key in token):
                for c in careers:
                    if c not in seen:
                        seen.add(c)
                        results.append(c)

    # 3. Multi-word phrase check (e.g. "machine learning", "data science")
    clean_lower = f" {clean_text.lower()} "
    for skill_key, careers in SKILL_CAREER_MAP.items():
        if f" {skill_key} " in clean_lower:
            for c in careers:
                if c not in seen:
                    seen.add(c)
                    results.append(c)

    if not results:
        results = ['General Professional', 'Consider exploring roles that match your interests']

    return results[:10]

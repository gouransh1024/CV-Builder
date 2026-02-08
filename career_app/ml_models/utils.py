import joblib
from django.conf import settings

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


def get_career_suggestions(skills_text):
    """Return a list of career suggestions based on skills/interests text."""
    model_path = getattr(settings, 'ML_MODEL_PATH', None)
    if model_path and getattr(model_path, 'exists', lambda: False)():
        try:
            model = joblib.load(model_path)
            pred = model.predict([skills_text.lower()])
            return list(pred) if hasattr(pred, '__iter__') and not isinstance(pred, str) else [str(pred)]
        except Exception:
            pass
    # Fallback: keyword-based suggestions
    skills_lower = skills_text.lower().strip()
    if not skills_lower:
        return ['General Professional', 'Career Coach recommended']
    words = set(skills_lower.replace(',', ' ').split())
    seen = set()
    result = []
    for word in words:
        if len(word) < 2:
            continue
        for skill_key, careers in SKILL_CAREER_MAP.items():
            if skill_key in word or word in skill_key:
                for c in careers:
                    if c not in seen:
                        seen.add(c)
                        result.append(c)
    if not result:
        result = ['General Professional', 'Consider exploring roles that match your interests']
    return result[:12]

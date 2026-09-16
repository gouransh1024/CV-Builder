"""
Job role metadata used by the interactive Explore Careers experience.

This is intentionally data-driven so you can extend it without touching UI code.
"""

ROLE_DEFINITIONS = [
    {
        "slug": "software-developer",
        "title": "Software Developer",
        "domain": "Tech",
        "experience": "Entry-Mid",
        "avg_salary_min": 70000,
        "avg_salary_max": 125000,
        "growth_trend": 9.5,
        "description": "Build and ship production software across the full lifecycle: design, implementation, testing, and maintenance.",
        "required_skills": ["python", "java", "sql", "git", "api", "testing", "database"],
        "apply_keywords": "Software Developer",
    },
    {
        "slug": "frontend-developer",
        "title": "Frontend Developer",
        "domain": "Tech",
        "experience": "Entry-Mid",
        "avg_salary_min": 75000,
        "avg_salary_max": 135000,
        "growth_trend": 10.2,
        "description": "Design and implement responsive user interfaces, accessibility improvements, and performance optimizations.",
        "required_skills": ["react", "javascript", "html", "css", "typescript", "redux", "api"],
        "apply_keywords": "Frontend Developer React",
    },
    {
        "slug": "backend-developer",
        "title": "Backend Developer",
        "domain": "Tech",
        "experience": "Entry-Mid-Senior",
        "avg_salary_min": 80000,
        "avg_salary_max": 145000,
        "growth_trend": 8.8,
        "description": "Create robust APIs, data models, and backend services powering web and mobile applications.",
        "required_skills": ["python", "java", "node", "django", "api", "sql", "docker"],
        "apply_keywords": "Backend Developer API Node Python",
    },
    {
        "slug": "data-analyst",
        "title": "Data Analyst",
        "domain": "Tech",
        "experience": "Entry-Mid",
        "avg_salary_min": 65000,
        "avg_salary_max": 120000,
        "growth_trend": 12.0,
        "description": "Analyze data to derive insights, build dashboards/reports, and support business decisions with evidence.",
        "required_skills": ["python", "sql", "analysis", "excel", "statistics", "database"],
        "apply_keywords": "Data Analyst SQL Python Analytics",
    },
    {
        "slug": "devops-engineer",
        "title": "DevOps Engineer",
        "domain": "Tech",
        "experience": "Mid-Senior",
        "avg_salary_min": 90000,
        "avg_salary_max": 155000,
        "growth_trend": 11.1,
        "description": "Own CI/CD, infrastructure automation, reliability improvements, and cloud deployment pipelines.",
        "required_skills": ["docker", "kubernetes", "aws", "azure", "ci", "cd", "linux", "git"],
        "apply_keywords": "DevOps Engineer CI CD Docker Kubernetes",
    },
    {
        "slug": "product-manager",
        "title": "Product Manager",
        "domain": "Tech",
        "experience": "Mid-Senior",
        "avg_salary_min": 95000,
        "avg_salary_max": 170000,
        "growth_trend": 6.6,
        "description": "Drive product strategy and execution: define roadmap, align stakeholders, measure outcomes, and iterate.",
        "required_skills": ["communication", "leadership", "agile", "roadmap", "analytics", "customer"],
        "apply_keywords": "Product Manager Roadmap Analytics",
    },
    {
        "slug": "marketing-specialist",
        "title": "Marketing Specialist",
        "domain": "Marketing",
        "experience": "Entry-Mid",
        "avg_salary_min": 55000,
        "avg_salary_max": 95000,
        "growth_trend": 7.7,
        "description": "Plan, execute, and optimize marketing programs across channels using performance data and experimentation.",
        "required_skills": ["marketing", "analysis", "writing", "communication", "excel", "seo"],
        "apply_keywords": "Marketing Specialist SEO Content Growth",
    },
    {
        "slug": "financial-analyst",
        "title": "Financial Analyst",
        "domain": "Finance",
        "experience": "Entry-Mid",
        "avg_salary_min": 65000,
        "avg_salary_max": 115000,
        "growth_trend": 5.2,
        "description": "Perform financial analysis, forecasting, and reporting to support strategy and investment decisions.",
        "required_skills": ["finance", "analysis", "excel", "sql", "communication"],
        "apply_keywords": "Financial Analyst Excel SQL Forecasting",
    },
]


ROLE_BY_SLUG = {r["slug"]: r for r in ROLE_DEFINITIONS}


def get_role_by_slug(slug: str):
    if not slug:
        return None
    return ROLE_BY_SLUG.get(slug)


def list_roles():
    return ROLE_DEFINITIONS[:]


def get_apply_links(role):
    """
    Generate external job platform links using a role's keywords.
    """
    keywords = role.get("apply_keywords") or role.get("title") or ""
    q = (keywords or "").strip()
    # LinkedIn expects keywords=... in query string
    linkedin = f"https://www.linkedin.com/jobs/search/?keywords={encodeURIComponent_safe(q)}"
    # Indeed commonly uses 'q' parameter
    indeed = f"https://www.indeed.com/jobs?q={encodeURIComponent_safe(q)}"
    # Glassdoor uses 'keyword' parameter
    glassdoor = f"https://www.glassdoor.com/Job/jobs.htm?keyword={encodeURIComponent_safe(q)}"
    return {
        "linkedin": linkedin,
        "indeed": indeed,
        "glassdoor": glassdoor,
    }


def encodeURIComponent_safe(s: str) -> str:
    # Minimal encoder to avoid adding dependencies.
    # Django templates & requests will handle safe characters.
    import urllib.parse

    return urllib.parse.quote(s)


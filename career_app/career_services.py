"""
Pure helper functions powering interactive career insights.

We keep this framework-agnostic so it can be reused by APIs, templates, and future AI modules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _normalize_skill(s: str) -> str:
    return (s or "").strip().lower().replace(".", "")


def compute_skill_overlap(found_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Returns (match_percent, matched_skills, missing_skills).
    """
    found_norm = {_normalize_skill(x) for x in (found_skills or [])}
    required_norm = {_normalize_skill(x) for x in (required_skills or [])}
    if not required_norm:
        return 0.0, [], []

    matched = sorted(list(required_norm.intersection(found_norm)))
    missing = sorted(list(required_norm.difference(found_norm)))
    match_percent = round((len(matched) / max(1, len(required_norm))) * 100, 1)
    return match_percent, matched, missing


LEARNING_PATHS = {
    "react": ["Build 2-3 React projects (forms, charts, dashboards)", "Study component architecture and hooks", "Practice accessibility and performance"],
    "javascript": ["Brush up on modern JS (async/await, modules)", "Practice state management patterns", "Learn testing basics (Jest/React Testing Library)"],
    "node": ["Build REST APIs with auth + pagination", "Learn async patterns and error handling", "Practice deployment with Docker"],
    "python": ["Practice data structures + scripting", "Build a mini backend service", "Work through one NLP/analysis project"],
    "sql": ["Learn indexing and query optimization", "Practice joins, CTEs, and window functions", "Build analytics queries for dashboards"],
    "docker": ["Create local dev environments using Docker Compose", "Learn container networking basics", "Practice CI pipelines with containers"],
}


def recommend_learning_path(missing_skills: List[str]) -> List[str]:
    """
    Rule-based learning path generation (cheap, deterministic).
    Can later be upgraded to an embedding/LLM-based recommender.
    """
    tips: List[str] = []
    for s in (missing_skills or []):
        key = _normalize_skill(s)
        if key in LEARNING_PATHS:
            tips.extend(LEARNING_PATHS[key][:2])
    if not tips:
        tips = ["Add missing keywords in a Skills/Experience section", "Add 1-2 projects that demonstrate those skills", "Use metrics (impact) to improve ATS matching"]
    # Deduplicate while preserving order
    seen = set()
    out = []
    for t in tips:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:6]


def build_role_insights(user_analysis: Dict[str, Any], role: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses the latest resume analysis to compute:
    - match_percent
    - gap analysis (missing_keywords)
    - learning path recommendations
    """
    found_skills = user_analysis.get("found_skills") or []
    required_skills = role.get("required_skills") or []
    match_percent, matched, missing = compute_skill_overlap(found_skills, required_skills)
    learning_path = recommend_learning_path(missing)

    return {
        "match_percent": match_percent,
        "matched_keywords": matched,
        "missing_keywords": missing[:12],
        "learning_path": learning_path,
    }


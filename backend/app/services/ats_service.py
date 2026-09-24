import re
from typing import Dict, Any, List, Optional

STRONG_ACTION_VERBS = [
    "architected", "engineered", "optimized", "automated", "streamlined",
    "spearheaded", "designed", "scaled", "implemented", "refactored",
    "reduced", "accelerated", "deployed", "built", "developed",
    "orchestrated", "migrated", "configured", "published", "led",
    "mentored", "authored", "integrated", "benchmarked", "executed"
]

METRIC_PATTERNS = [
    r'\b\d+(?:\.\d+)?%\b',                                  # Percentages: 25%, 3.2%
    r'\b\d+(?:\.\d+)?x\b',                                  # Multipliers: 3.2x, 10x
    r'\b\d+\s*(?:k|m|b|million|billion|thousand)\b',        # Scale: 10M, 50k
    r'\$\d+(?:,\d+)*(?:\.\d+)?\b',                         # Currency: $10,000
    r'\b\d+\s*(?:ms|seconds|users|clients|events|requests|queries|nodes|clusters|qps|rps)\b', # Metrics
    r'\b(?:gpa|cgpa)\s*[:=]?\s*\d+(?:\.\d+)?\b'             # GPA: 9.1 / 10.0
]


def evaluate_ats_health(raw_text: str, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate resume ATS compatibility, impact metrics, action verb strength, and structural completeness.
    """
    text = (raw_text or "").strip()
    text_lower = text.lower()
    
    # 1. Quantifiable Impact Metrics (Weight 30%)
    metrics_found = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, text_lower)
        metrics_found.extend(matches)
    
    metric_count = len(metrics_found)
    if metric_count >= 5:
        metric_score = 30.0
    elif metric_count >= 3:
        metric_score = 24.0
    elif metric_count >= 1:
        metric_score = 16.0
    else:
        metric_score = 5.0

    # 2. Action Verb Strength (Weight 25%)
    verbs_found = set()
    for verb in STRONG_ACTION_VERBS:
        if re.search(r'\b' + re.escape(verb) + r'\b', text_lower):
            verbs_found.add(verb.title())
    
    verb_count = len(verbs_found)
    if verb_count >= 6:
        verb_score = 25.0
    elif verb_count >= 4:
        verb_score = 20.0
    elif verb_count >= 2:
        verb_score = 14.0
    else:
        verb_score = 6.0

    # 3. Structural Completeness (Weight 25%)
    structure_checks = {
        "Contact Information": bool(parsed_resume.get("email") or parsed_resume.get("phone")),
        "Technical Skills": bool(parsed_resume.get("technical_skills") or parsed_resume.get("skills")),
        "Work Experience": bool(parsed_resume.get("experience") or "experience" in text_lower or "intern" in text_lower),
        "Projects Section": bool(parsed_resume.get("projects")),
        "Education Section": bool(parsed_resume.get("education") or "education" in text_lower or "university" in text_lower or "degree" in text_lower),
        "Developer Profiles": bool(parsed_resume.get("github_username") or parsed_resume.get("leetcode_username")),

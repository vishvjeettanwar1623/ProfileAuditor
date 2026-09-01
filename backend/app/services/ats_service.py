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
    }
    
    passed_sections = sum(1 for v in structure_checks.values() if v)
    structure_score = round((passed_sections / len(structure_checks)) * 25.0, 1)

    # 4. Length & Formatting Health (Weight 20%)
    word_count = len(text.split())
    if 300 <= word_count <= 950:
        length_score = 20.0
    elif 200 <= word_count < 300 or 950 < word_count <= 1300:
        length_score = 14.0
    else:
        length_score = 8.0

    total_ats_score = min(100.0, round(metric_score + verb_score + structure_score + length_score, 1))

    # Passed checks & Improvement tips
    passed_checks = []
    improvement_tips = []

    if metric_count >= 3:
        passed_checks.append(f"Includes strong quantifiable impact metrics ({metric_count} measurable achievements detected)")
    else:
        improvement_tips.append("Add more measurable impact metrics (%, scale, latency reduction, user growth) to experience bullet points")

    if verb_count >= 4:
        passed_checks.append(f"Uses strong technical action verbs ({len(verbs_found)} distinct verbs: {', '.join(list(verbs_found)[:4])})")
    else:
        improvement_tips.append("Begin bullet points with active engineering verbs (e.g. 'Architected', 'Optimized', 'Automated')")

    if passed_sections == len(structure_checks):
        passed_checks.append("All standard ATS sections present and structured cleanly")
    else:
        missing_secs = [k for k, v in structure_checks.items() if not v]
        improvement_tips.append(f"Ensure explicit section headers for: {', '.join(missing_secs)}")

    if 300 <= word_count <= 950:
        passed_checks.append(f"Optimal resume length ({word_count} words — ideal for single/two-page ATS parsing)")
    else:
        improvement_tips.append(f"Resume length is {word_count} words. Aim for 350–850 words for optimal recruiter readability")

    if parsed_resume.get("github_username") or parsed_resume.get("leetcode_username"):
        passed_checks.append("Includes discoverable public engineering footprints (GitHub/LeetCode)")

    # Rating label
    if total_ats_score >= 80:
        health_label = "Optimal ATS Health"
    elif total_ats_score >= 60:
        health_label = "Good ATS Health"
    else:
        health_label = "Needs Optimization"

    return {
        "ats_score": total_ats_score,
        "health_label": health_label,
        "word_count": word_count,
        "metric_count": metric_count,
        "action_verbs_count": verb_count,
        "action_verbs": sorted(list(verbs_found)),
        "sub_scores": {
            "impact_metrics": round((metric_score / 30.0) * 100, 1),
            "action_verbs": round((verb_score / 25.0) * 100, 1),
            "structure_completeness": round((structure_score / 25.0) * 100, 1),
            "formatting_health": round((length_score / 20.0) * 100, 1),
        },
        "passed_checks": passed_checks,
        "improvement_tips": improvement_tips
    }

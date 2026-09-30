import os
import re
import json
import requests
from typing import Dict, Any, List, Optional

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def extract_jd_requirements(job_description: str) -> Dict[str, Any]:
    """
    Extract structured requirements from a job description text using LLM or rule-based fallback.
    """
    if not job_description or not job_description.strip():
        return {
            "role_title": "General Software Engineer",
            "required_skills": [],
            "preferred_skills": [],
            "domain_focus": "General Engineering"
        }

    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        prompt = (
            "You are an expert technical recruiter. Extract structured hiring requirements from the following Job Description.\n"
            "Return a strictly valid JSON object with these exact keys:\n"
            "{\n"
            '  "role_title": "e.g. Senior Backend Engineer",\n'
            '  "required_skills": ["e.g. Go", "Docker", "PostgreSQL", "Kubernetes"],\n'
            '  "preferred_skills": ["e.g. Redis", "AWS", "gRPC"],\n'
            '  "domain_focus": "e.g. Distributed Systems & Cloud Infrastructure"\n'
            "}\n"
            "Do NOT include markdown fences, backticks, or any additional text. Return ONLY the raw JSON object.\n\n"
            f"JOB DESCRIPTION:\n{job_description}"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "ProfileAuditor",
        }

        body = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You extract structured hiring requirements into clean JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        }

        try:
            url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
            resp = requests.post(url, headers=headers, json=body, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
                content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "required_skills" in parsed:
                    return parsed
        except Exception as e:
            print(f"LLM JD extraction fallback: {e}")

    # Rule-based fallback extraction
    return _rule_based_jd_extraction(job_description)


def _rule_based_jd_extraction(job_description: str) -> Dict[str, Any]:
    """Fallback rule-based JD requirement extractor."""
    known_skills = [
        "python", "javascript", "typescript", "react", "node.js", "next.js", "vue", "angular",
        "java", "spring boot", "c++", "c#", ".net", "go", "golang", "rust", "php", "ruby", "rails",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
        "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci/cd", "git", "github",
        "graphql", "rest", "grpc", "microservices", "kafka", "rabbitmq", "linux", "html", "css",
        "pytorch", "tensorflow", "opencv", "scikit-learn", "fastapi"
    ]

    jd_lower = job_description.lower()
    found_skills = []

    for s in known_skills:
        pattern = r'\b' + re.escape(s) + r'\b'
        if re.search(pattern, jd_lower):
            found_skills.append(s.title() if len(s) > 2 else s.upper())

    # Detect role title
    title = "Target Software Role"
    first_line = job_description.strip().split('\n')[0][:60]
    if any(k in first_line.lower() for k in ["engineer", "developer", "architect", "lead", "intern"]):
        title = first_line

    required = found_skills[:6] if len(found_skills) > 6 else found_skills
    preferred = found_skills[6:10] if len(found_skills) > 6 else []

    return {
        "role_title": title,
        "required_skills": required,
        "preferred_skills": preferred,
        "domain_focus": "Software Engineering"
    }


def _skill_matches(target_skill: str, candidate_skills: List[str]) -> bool:
    """Case-insensitive fuzzy match for skills."""
    t_clean = re.sub(r'[^a-z0-9]', '', target_skill.lower())
    for s in candidate_skills:
        s_clean = re.sub(r'[^a-z0-9]', '', s.lower())
        if t_clean == s_clean or t_clean in s_clean or s_clean in t_clean:
            return True
    return False


def evaluate_role_fit(
    job_description: str,
    verified_skills: List[str],
    unverified_skills: List[str],
    verified_projects: List[str],
    github_results: Dict[str, Any],
    leetcode_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate candidate's verified public footprint against target job description requirements.
    """
    if not job_description or not job_description.strip():
        return None

    requirements = extract_jd_requirements(job_description)
    req_skills = requirements.get("required_skills", [])
    pref_skills = requirements.get("preferred_skills", [])

    verified_req = []
    claimed_unverified_req = []
    missing_req = []

    for skill in req_skills:
        if _skill_matches(skill, verified_skills):
            verified_req.append(skill)
        elif _skill_matches(skill, unverified_skills):
            claimed_unverified_req.append(skill)
        else:
            missing_req.append(skill)

    verified_pref = []
    missing_pref = []

    for skill in pref_skills:
        if _skill_matches(skill, verified_skills) or _skill_matches(skill, unverified_skills):
            verified_pref.append(skill)
        else:
            missing_pref.append(skill)

    # Score calculation (0 - 100)
    # Required skills with verified code proof: 1.0 weight
    # Required skills claimed but unverified: 0.4 weight
    # Preferred skills bonus: up to 15 points
    total_req_count = len(req_skills)
    if total_req_count > 0:
        req_points = (len(verified_req) * 1.0 + len(claimed_unverified_req) * 0.4) / total_req_count * 85
    else:
        req_points = 85.0

    total_pref_count = len(pref_skills)
    pref_points = (len(verified_pref) / total_pref_count * 15) if total_pref_count > 0 else 10.0

    role_fit_score = min(100.0, round(req_points + pref_points, 1))

    # Hiring recommendation verdict
    if role_fit_score >= 80:
        verdict = "Strong Match - High Code Proof"
        verdict_summary = f"Candidate has verified code evidence for {len(verified_req)} of {total_req_count} core requirements. Recommended for technical interview."
    elif role_fit_score >= 55:
        verdict = "Moderate Match - Verification Gaps"
        verdict_summary = f"Candidate matches core requirements, but {len(claimed_unverified_req)} required skills lack public repository proof. Conduct focused technical screen."
    else:
        verdict = "Low Alignment with Role"
        verdict_summary = f"Significant requirement gap: {len(missing_req)} of {total_req_count} core requirements were not found in candidate claims or codebases."

    return {
        "role_title": requirements.get("role_title", "Target Role"),
        "domain_focus": requirements.get("domain_focus", "General Engineering"),
        "role_fit_score": role_fit_score,
        "verdict": verdict,
        "verdict_summary": verdict_summary,
        "verified_requirements": verified_req,
        "claimed_unverified_requirements": claimed_unverified_req,
        "missing_requirements": missing_req,
        "verified_preferred": verified_pref,
        "missing_preferred": missing_pref,
        "total_required_count": total_req_count,
        "total_preferred_count": total_pref_count
    }

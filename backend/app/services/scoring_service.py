import os
import re
import json
import requests
from typing import Dict, Any, List, Tuple, Optional

# Optional Gemini SDK fallback
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def _call_openrouter_for_score(payload: Dict[str, Any]) -> Optional[float]:
    """Call OpenRouter model to obtain an AI-evaluated Reality Score (0-100)."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY not set; falling back to Gemini SDK or rule-based scoring")
        return _call_gemini_for_score(payload)

    system_prompt = (
        "You are an expert technical recruiter and developer profile auditor. Assign a single overall Reality Score from 0 to 100.\n"
        "Evaluation Principles:\n"
        "- Reward verifiable technical evidence from GitHub code repositories and LeetCode problem solving.\n"
        "- Penalize unverified technical claims and missing public code proof.\n"
        "- Consider the provided sub-scores as guidance.\n"
        "- Output ONLY the final integer number (0-100) with no additional text or formatting."
    )

    context = {
        "breakdown": payload.get("breakdown", {}),
        "counts": {
            "verified_skills": len(payload.get("verified_skills", [])),
            "unverified_skills": len(payload.get("unverified_skills", [])),
            "verified_projects": len(payload.get("verified_projects", [])),
            "unverified_projects": len(payload.get("unverified_projects", [])),
        },
        "github_audit": {
            "has_github": bool(payload.get("github_results")),
            "original_repos": len(payload.get("github_results", {}).get("original_repos", [])),
            "forked_repos": len(payload.get("github_results", {}).get("forked_repos", [])),
            "total_stars": payload.get("github_results", {}).get("total_stars", 0),
            "languages": payload.get("github_results", {}).get("languages", []),
        },
        "leetcode_audit": {
            "has_leetcode": bool(payload.get("leetcode_results", {}).get("verified")),
            "total_solved": payload.get("leetcode_results", {}).get("total_solved", 0),
            "ranking": payload.get("leetcode_results", {}).get("global_ranking"),
        },
        "rule_based_final": payload.get("rule_based_final")
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "ProfileAuditor",
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"AUDIT DATA:\n{json.dumps(context)}"}
        ],
        "temperature": 0.2,
        "max_tokens": 10,
    }

    try:
        url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        print(f"Calling OpenRouter model '{OPENROUTER_MODEL}' for reality score...")
        resp = requests.post(url, headers=headers, json=body, timeout=20)
        if resp.status_code != 200:
            print(f"OpenRouter returned status {resp.status_code}: {resp.text}")
            return _call_gemini_for_score(payload)

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            return _call_gemini_for_score(payload)

        content = choices[0].get("message", {}).get("content", "").strip()
        m = re.search(r"\b(100|\d{1,2})\b", content)
        if not m:
            return _call_gemini_for_score(payload)

        score = float(m.group(1))
        return max(0.0, min(100.0, score))
    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        return _call_gemini_for_score(payload)


def _call_gemini_for_score(payload: Dict[str, Any]) -> Optional[float]:
    """Call Gemini as fallback to get an AI-driven score (0-100)."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        prompt = (
            "You are an expert resume auditor. Assign a single overall Reality Score from 0 to 100 based on verified code evidence.\n"
            "Output ONLY a single integer (0-100)."
        )

        response = model.generate_content([prompt, f"DATA:\n{payload}"])
        text = (response.text or "").strip()
        m = re.search(r"\b(100|\d{1,2})\b", text)
        if not m:
            return None
        return float(max(0, min(100, int(m.group(1)))))
    except Exception:
        return None


def calculate_reality_score(
    github_results: Dict[str, Any],
    leetcode_results: Dict[str, Any],
    verified_skills: List[str],
    unverified_skills: List[str],
    verified_projects: List[str],
    unverified_projects: List[str]
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate reality score based on ground-truth verification results:
    - GitHub Code Authenticity
    - LeetCode Problem Solving
    - Technical Skills Verification
    - Projects Verification
    """
    # 1. Calculate component sub-scores (0 - 100)
    github_score = calculate_github_score(github_results)
    leetcode_score = calculate_leetcode_score(leetcode_results)
    skills_score = calculate_skills_score(verified_skills, unverified_skills)
    projects_score = calculate_projects_score(verified_projects, unverified_projects)

    # 2. Rule-based composite calculation
    has_leetcode = bool(leetcode_results and leetcode_results.get("verified"))

    if has_leetcode:
        # Standard balanced weights when both GitHub and LeetCode exist
        rule_based_final = (
            (github_score * 0.35) +
            (skills_score * 0.30) +
            (projects_score * 0.20) +
            (leetcode_score * 0.15)
        )
    else:
        # Dynamically normalized weights when candidate does not use LeetCode
        rule_based_final = (
            (github_score * 0.45) +
            (skills_score * 0.35) +
            (projects_score * 0.20)
        )

    rule_based_final = round(max(0.0, min(100.0, rule_based_final)), 1)

    breakdown = {
        "github_score": round(github_score, 1),
        "leetcode_score": round(leetcode_score, 1),
        "skills_score": round(skills_score, 1),
        "projects_score": round(projects_score, 1)
    }

    # 3. AI Reality Evaluation
    ai_payload = {
        "breakdown": breakdown,
        "verified_skills": verified_skills,
        "unverified_skills": unverified_skills,
        "verified_projects": verified_projects,
        "unverified_projects": unverified_projects,
        "github_results": github_results,
        "leetcode_results": leetcode_results,
        "rule_based_final": rule_based_final,
    }

    ai_score = _call_openrouter_for_score(ai_payload)
    if ai_score is not None:
        final_score = round(ai_score, 1)
    else:
        final_score = rule_based_final

    print(f"Final Reality Score: {final_score}/100 (Breakdown: {breakdown})")
    return final_score, breakdown


def calculate_github_score(github_results: Dict[str, Any]) -> float:
    """Calculate GitHub authenticity score from audit results."""
    if not github_results:
        return 0.0

    # If score already precomputed in deep audit
    if "score" in github_results and github_results["score"] > 0:
        return float(github_results["score"])

    original_repos = github_results.get("original_repos", [])
    languages = github_results.get("languages", [])
    total_stars = github_results.get("total_stars", 0)
    recent_active = github_results.get("recent_active_repos", [])

    repo_points = min(35, len(original_repos) * 6)
    lang_points = min(25, len(languages) * 6)
    recent_points = min(20, len(recent_active) * 6)
    star_points = min(20, total_stars * 3)

    return float(min(100, repo_points + lang_points + recent_points + star_points))


def calculate_leetcode_score(leetcode_results: Dict[str, Any]) -> float:
    """Calculate LeetCode problem-solving score."""
    if not leetcode_results or not leetcode_results.get("verified"):
        return 0.0

    if "score" in leetcode_results:
        return float(leetcode_results["score"])

    total = leetcode_results.get("total_solved", 0)
    mediums = leetcode_results.get("medium_solved", 0)
    hards = leetcode_results.get("hard_solved", 0)

    score = (total * 0.15) + (mediums * 0.35) + (hards * 1.0)
    return float(min(100, score))


def calculate_skills_score(verified_skills: List[str], unverified_skills: List[str]) -> float:
    """Calculate technical skills verification percentage."""
    total_skills = len(verified_skills) + len(unverified_skills)
    if total_skills == 0:
        return 0.0
    return float((len(verified_skills) / total_skills) * 100)


def calculate_projects_score(verified_projects: List[str], unverified_projects: List[str]) -> float:
    """Calculate projects verification percentage."""
    total_projects = len(verified_projects) + len(unverified_projects)
    if total_projects == 0:
        return 0.0
    return float((len(verified_projects) / total_projects) * 100)
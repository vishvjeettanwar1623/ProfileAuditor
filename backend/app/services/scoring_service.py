from typing import Dict, Any, List, Tuple
import os
import re

# Try to import Gemini SDK lazily; keep optional to avoid hard failures at import time
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # Fallback handled at runtime

# Default Gemini API Key per requirement (can be overridden by environment)
DEFAULT_GEMINI_API_KEY = "AIzaSyCfaVChVIoeE9se5xULvafD0YazbIuT6ck"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


from typing import Optional

def _call_gemini_for_score(payload: Dict[str, Any]) -> Optional[float]:
    """Call Gemini to get an AI-driven score (0-100) with medium difficulty.
    Returns None if the call cannot be completed; caller should fallback.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY", DEFAULT_GEMINI_API_KEY)
        if not api_key or genai is None:
            return None
        # Configure client (idempotent)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Build concise prompt; ask for a single integer 0-100 only
        prompt = (
            "You are an expert resume auditor. Assign a single overall Reality Score from 0 to 100.\n"
            "Be medium difficult (moderately strict):\n"
            "- Reward verified evidence across GitHub/Twitter/LinkedIn.\n"
            "- Penalize unverified claims.\n"
            "- Consider the provided rule-based sub-scores as guidance, but you may adjust.\n"
            "- Output ONLY the number (integer 0-100) with no extra text.\n"
        )

        # Keep payload compact; include breakdown and counts
        context = {
            "breakdown": payload.get("breakdown", {}),
            "counts": {
                "verified_skills": len(payload.get("verified_skills", [])),
                "unverified_skills": len(payload.get("unverified_skills", [])),
                "verified_projects": len(payload.get("verified_projects", [])),
                "unverified_projects": len(payload.get("unverified_projects", [])),
            },
            "sources": {
                "has_github": bool(payload.get("github_results")),
                "has_twitter": bool(payload.get("twitter_results")),
                "has_linkedin": bool(payload.get("linkedin_results")),
            },
        }

        # Temperature: relatively low to keep consistency; medium strictness is in instructions
        response = model.generate_content([
            prompt,
            f"DATA:\n{context}"
        ])
        text = (response.text or "").strip()
        # Extract first number 0-100
        m = re.search(r"\b(100|\d{1,2})\b", text)
        if not m:
            return None
        score = int(m.group(1))
        # Clamp to [0, 100]
        score = max(0, min(100, score))
        return float(score)
    except Exception:
        return None


def calculate_reality_score(
    github_results: Dict[str, Any],
    twitter_results: Dict[str, Any],
    linkedin_results: Dict[str, Any],
    verified_skills: List[str],
    unverified_skills: List[str],
    verified_projects: List[str],
    unverified_projects: List[str]
) -> Tuple[float, Dict[str, float]]:
    """Calculate reality score based on verification results.
    Uses Gemini to produce the final score with medium difficulty when available; otherwise falls back to rule-based.
    """
    # Define weights for different sources (used for rule-based guidance and breakdown)
    weights = {
        "github": 0.5,  # GitHub has highest weight
        "twitter": 0.3,  # Twitter has medium weight
        "linkedin": 0.2,  # LinkedIn has lowest weight (mock data)
        "skills": 0.6,  # Skills have higher weight than projects
        "projects": 0.4  # Projects have lower weight than skills
    }
    
    # Calculate sub-scores (rule-based)
    github_score = calculate_github_score(github_results)
    twitter_score = calculate_twitter_score(twitter_results)
    linkedin_score = calculate_linkedin_score(linkedin_results)
    skills_score = calculate_skills_score(verified_skills, unverified_skills)
    projects_score = calculate_projects_score(verified_projects, unverified_projects)
    
    # Weighted composites
    source_score = (
        github_score * weights["github"] +
        twitter_score * weights["twitter"] +
        linkedin_score * weights["linkedin"]
    )
    content_score = (
        skills_score * weights["skills"] +
        projects_score * weights["projects"]
    )
    rule_based_final = (source_score + content_score) / 2
    rule_based_final = max(0, min(100, rule_based_final))

    # Prepare payload for AI
    breakdown = {
        "github_score": github_score,
        "twitter_score": twitter_score,
        "linkedin_score": linkedin_score,
        "skills_score": skills_score,
        "projects_score": projects_score
    }
    ai_payload = {
        "breakdown": breakdown,
        "verified_skills": verified_skills,
        "unverified_skills": unverified_skills,
        "verified_projects": verified_projects,
        "unverified_projects": unverified_projects,
        "github_results": github_results,
        "twitter_results": twitter_results,
        "linkedin_results": linkedin_results,
        "rule_based_final": rule_based_final,
    }

    ai_score = _call_gemini_for_score(ai_payload)
    final_score = ai_score if ai_score is not None else rule_based_final

    return final_score, breakdown

def calculate_github_score(github_results: Dict[str, Any]) -> float:
    """Calculate GitHub score"""
    print(f"=== CALCULATING GITHUB SCORE ===")
    print(f"GitHub results: {github_results}")
    
    # If there's an error or no GitHub username, return 0
    if "error" in github_results:
        print(f"GitHub has error: {github_results.get('error')}")
        return 0
    
    if not github_results:
        print(f"GitHub results is empty")
        return 0
    
    # Calculate score based on repositories, languages, and contributions
    repositories = github_results.get("repositories", [])
    languages = github_results.get("languages", [])
    contributions = github_results.get("contributions", 0)
    verified_skills = github_results.get("verified_skills", [])
    verified_projects = github_results.get("verified_projects", [])
    
    print(f"Repositories: {len(repositories)} - {repositories}")
    print(f"Languages: {len(languages)} - {languages}")
    print(f"Contributions: {contributions}")
    print(f"Verified skills: {len(verified_skills)} - {verified_skills}")
    print(f"Verified projects: {len(verified_projects)} - {verified_projects}")
    
    # Repository score (max 25 points)
    repo_score = min(25, len(repositories) * 5)
    print(f"Repository score: {repo_score}")
    
    # Language score (max 25 points)
    language_score = min(25, len(languages) * 5)
    print(f"Language score: {language_score}")
    
    # Contributions score (max 20 points)
    contribution_score = min(20, contributions / 25)
    print(f"Contribution score: {contribution_score}")
    
    # Verification score (max 30 points)
    verification_score = min(30, (len(verified_skills) + len(verified_projects)) * 3)
    print(f"Verification score: {verification_score}")
    
    # Total GitHub score (max 100 points)
    total_score = repo_score + language_score + contribution_score + verification_score
    print(f"Total GitHub score: {total_score}")
    
    return total_score

def calculate_twitter_score(twitter_results: Dict[str, Any]) -> float:
    """Calculate Twitter score"""
    # If there's an error or no Twitter username, return 0
    if "error" in twitter_results or not twitter_results:
        return 0
    
    # Calculate score based on tweets and verifications
    tweets = twitter_results.get("tweets", [])
    verified_skills = twitter_results.get("verified_skills", [])
    verified_projects = twitter_results.get("verified_projects", [])
    
    # Tweet score (max 40 points)
    tweet_score = min(40, len(tweets) * 8)
    
    # Verification score (max 60 points)
    verification_score = min(60, (len(verified_skills) + len(verified_projects)) * 6)
    
    # Total Twitter score (max 100 points)
    total_score = tweet_score + verification_score
    
    return total_score

def calculate_linkedin_score(linkedin_results: Dict[str, Any]) -> float:
    """Calculate LinkedIn score"""
    print(f"=== CALCULATING LINKEDIN SCORE ===")
    print(f"LinkedIn results: {linkedin_results}")
    
    # If there's an error or no LinkedIn username, return 0
    if "error" in linkedin_results:
        print(f"LinkedIn has error: {linkedin_results.get('error')}")
        return 0
    
    if not linkedin_results:
        print(f"LinkedIn results is empty")
        return 0
    
    # Calculate score based on profile completeness and verifications
    profile = linkedin_results.get("profile", {})
    verified_skills = linkedin_results.get("verified_skills", [])
    verified_projects = linkedin_results.get("verified_projects", [])
    
    print(f"Profile: {profile}")
    print(f"Verified skills: {len(verified_skills)} - {verified_skills}")
    print(f"Verified projects: {len(verified_projects)} - {verified_projects}")
    
    # Profile completeness score (max 40 points)
    profile_score = 0
    if profile.get("name"):
        profile_score += 10
    if profile.get("headline"):
        profile_score += 10
    if profile.get("skills"):
        profile_score += 20
    
    print(f"Profile completeness score: {profile_score}")
    
    # Verification score (max 60 points)
    verification_score = min(60, (len(verified_skills) + len(verified_projects)) * 6)
    print(f"Verification score: {verification_score}")
    
    # Total LinkedIn score (max 100 points)
    total_score = profile_score + verification_score
    print(f"Total LinkedIn score: {total_score}")
    
    return total_score
    verified_projects = linkedin_results.get("verified_projects", [])
    
    # Profile score (max 40 points)
    profile_score = 0
    if profile.get("skills"):
        profile_score += min(20, len(profile.get("skills", [])) * 2)
    if profile.get("experience"):
        profile_score += min(20, len(profile.get("experience", [])) * 7)
    
    # Verification score (max 60 points)
    verification_score = min(60, (len(verified_skills) + len(verified_projects)) * 6)
    
    # Total LinkedIn score (max 100 points)
    total_score = profile_score + verification_score
    
    return total_score

def calculate_skills_score(verified_skills: List[str], unverified_skills: List[str]) -> float:
    """Calculate skills score"""
    # If no skills, return 0
    total_skills = len(verified_skills) + len(unverified_skills)
    if total_skills == 0:
        return 0
    
    # Calculate percentage of verified skills
    verification_percentage = len(verified_skills) / total_skills if total_skills > 0 else 0
    
    # Convert to score out of 100
    score = verification_percentage * 100
    
    return score

def calculate_projects_score(verified_projects: List[str], unverified_projects: List[str]) -> float:
    """Calculate projects score"""
    # If no projects, return 0
    total_projects = len(verified_projects) + len(unverified_projects)
    if total_projects == 0:
        return 0
    
    # Calculate percentage of verified projects
    verification_percentage = len(verified_projects) / total_projects if total_projects > 0 else 0
    
    # Convert to score out of 100
    score = verification_percentage * 100
    
    return score
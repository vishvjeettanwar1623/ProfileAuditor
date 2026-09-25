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

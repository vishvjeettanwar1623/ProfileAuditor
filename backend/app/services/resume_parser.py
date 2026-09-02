import os
import sys
import re
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
import PyPDF2
import docx

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# PDF parsing libraries with fallbacks
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
    print("pdfplumber library loaded successfully")
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("pdfplumber not available")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("PyMuPDF library loaded successfully")
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("PyMuPDF not available")

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    PDFMINER_AVAILABLE = True
    print("pdfminer.six library loaded successfully")
except ImportError:
    PDFMINER_AVAILABLE = False
    print("pdfminer.six not available")

# Optional Gemini fallback
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# =====================================================================
# 1. RAW TEXT EXTRACTION (PDF / DOCX)
# =====================================================================

def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF file using multiple fallback libraries for best fidelity."""
    print(f"\n=== PDF EXTRACTION START ===")
    print(f"Extracting text from PDF: {file_path}")
    
    extraction_results = {}

    # Method 1: pdfplumber
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    extracted_text += page_text + "\n"
                extraction_results['pdfplumber'] = extracted_text
        except Exception:
            extraction_results['pdfplumber'] = ''

    # Method 2: PyMuPDF
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(file_path)
            extracted_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                extracted_text += page_text + "\n"
            doc.close()
            extraction_results['pymupdf'] = extracted_text
        except Exception:
            extraction_results['pymupdf'] = ''

    # Method 3: pdfminer
    if PDFMINER_AVAILABLE:
        try:
            extracted_text = pdfminer_extract_text(file_path)
            extraction_results['pdfminer'] = extracted_text
        except Exception:
            extraction_results['pdfminer'] = ''

    # Method 4: PyPDF2
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            extracted_text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                extracted_text += page_text + "\n"
            extraction_results['pypdf2'] = extracted_text
    except Exception:
        extraction_results['pypdf2'] = ''

    # Clean and pick highest-scoring result
    cleaned_results = {}
    for method, raw_text in extraction_results.items():
        cleaned = clean_pdf_text(raw_text or "")
        cleaned_results[method] = cleaned

    def score(text: str) -> Tuple[int, int]:
        words = set(text.split())
        return (len(words), len(text))

    if not cleaned_results:
        return ""

    best_method = max(cleaned_results, key=lambda m: score(cleaned_results[m]))
    best_text = cleaned_results[best_method]

    print(f"Best PDF extraction method: {best_method} ({len(best_text)} chars, {len(set(best_text.split()))} unique words)")
    print(f"=== PDF EXTRACTION COMPLETE ===")
    return best_text.strip()


def clean_pdf_text(text: str) -> str:
    """Clean and normalize PDF extracted text while preserving semantic layout."""
    if not text:
        return ""
    
    text = text.replace('\x00', ' ')
    text = text.replace('–', '—').replace('−', '—')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        return text.strip()
    except Exception as e:
        print(f"DOCX extraction failed: {e}")
        return ""


def extract_text_from_file(file_path: str) -> str:
    """Extract raw text from PDF or DOCX file instantly without LLM overhead."""
    if not file_path or not os.path.exists(file_path):
        return ""
    if file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    return extract_text_from_pdf(file_path)


# =====================================================================
# 2. SOCIAL PROFILES / GITHUB USERNAME EXTRACTION
# =====================================================================

def extract_github_username(text: str) -> Optional[str]:
    """
    Extract clean GitHub username from resume text.
    Handles URLs (github.com/username), handle prefixes (Github: username, Github - username),
    and contact/social lines.
    """
    if not text:
        print("❌ extract_github_username: Empty text provided")
        return None

    # Strip URLs and tags
    patterns = [
        r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})(?:/|\b|\s|$)',
        r'(?i)\bgithub\s*[:\-–—|]\s*(?:https?://)?(?:www\.)?(?:github\.com/)?@?([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})\b',
        r'(?i)\bgithub\s+username\s*[:\-–—|]\s*@?([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})\b',
        r'@([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})\s*\(\s*github\s*\)',
    ]

    invalid_names = {'com', 'www', 'http', 'https', 'github', 'null', 'none', 'user', 'username', 'profile', 'portfolio', 'link'}

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            candidate = match.group(1).strip().strip('/').strip('@')
            if candidate and candidate.lower() not in invalid_names and len(candidate) >= 1:
                print(f"✅ GitHub username extracted successfully: '{candidate}' (matched pattern: {pattern})")
                return candidate

    print("ℹ️ No GitHub username found in resume text")
    return None


def extract_leetcode_username(text: str) -> Optional[str]:
    """Extract LeetCode handle from resume text."""
    if not text:
        return None

    patterns = [
        r'(?:https?://)?(?:www\.)?leetcode\.com/(?:u/)?([a-zA-Z0-9_-]{2,30})(?:/|\b|\s|$)',
        r'(?i)\bleetcode\s*[:\-–—|]\s*(?:https?://)?(?:www\.)?(?:leetcode\.com/(?:u/)?)?@?([a-zA-Z0-9_-]{2,30})\b',
        r'(?i)\bleetcode\s+username\s*[:\-–—|]\s*@?([a-zA-Z0-9_-]{2,30})\b',
    ]

    invalid_names = {'com', 'www', 'http', 'https', 'leetcode', 'u', 'null', 'none', 'profile', 'problem', 'contest'}

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            candidate = match.group(1).strip().strip('/').strip('@')
            if candidate and candidate.lower() not in invalid_names and len(candidate) >= 1:
                print(f"✅ LeetCode username extracted: '{candidate}'")
                return candidate

    return None


# =====================================================================
# 3. LLM-BASED STRUCTURED RESUME EXTRACTION
# =====================================================================

def _clean_json_text(text: str) -> str:
    """Extract pure JSON from LLM output by removing markdown fences or commentary."""
    text = text.strip()
    if "```" in text:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            text = match.group(1).strip()

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text


def _call_openrouter_extraction(raw_text: str) -> Optional[Dict[str, Any]]:
    """Query OpenRouter API for structured resume JSON."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    model_name = os.getenv("OPENROUTER_MODEL", OPENROUTER_MODEL)
    base_url = os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL).rstrip("/")

    system_prompt = (
        "You are an expert, precise resume parser. Extract structured candidate data from resume text into strict JSON.\n\n"
        "Return ONLY a single valid JSON object with EXACTLY this structure:\n"
        "{\n"
        '  "name": "Candidate Full Name or null",\n'
        '  "email": "Email address or null",\n'
        '  "phone": "Phone number or null",\n'
        '  "technical_skills": ["Language1", "Framework1", "Tool1"],\n'
        '  "soft_skills": ["SoftSkill1", "SoftSkill2"],\n'
        '  "projects": [\n'
        '    {\n'
        '      "name": "Project Name",\n'
        '      "description": "Short description of project and technologies"\n'
        '    }\n'
        '  ],\n'
        '  "experience": [\n'
        '    {\n'
        '      "role": "Role / Title",\n'
        '      "company": "Company Name",\n'
        '      "duration": "Duration / Dates",\n'
        '      "description": "Responsibilities"\n'
        '    }\n'
        '  ],\n'
        '  "education": [\n'
        '    {\n'
        '      "institution": "University / School",\n'
        '      "degree": "Degree / Field",\n'
        '      "year": "Graduation Year / Dates"\n'
        '    }\n'
        '  ],\n'
        '  "github_username": "GitHub handle without url/@ or null",\n'
        '  "leetcode_username": "LeetCode handle without url/@ or null"\n'
        "}\n\n"
        "CRITICAL EXTRACTION RULES:\n"
        "1. technical_skills: ONLY include programming languages, frameworks, developer tools, libraries, and technologies provable via code repositories (e.g. Python, React, Solidity, Docker, PostgreSQL, Git). NEVER put soft skills here.\n"
        "2. soft_skills: ONLY include interpersonal/organizational skills (e.g. Leadership, Public Speaking, Community Management, Teamwork, Communication). NEVER put soft skills in technical_skills.\n"
        "3. projects: ONLY extract actual software/engineering projects from a genuine Projects section. DO NOT extract hackathons, awards, prizes, extracurricular clubs, or job experiences as projects.\n"
        "4. Do NOT classify job titles, certifications, or company names as skills.\n"
        "5. Output valid, parseable JSON with no additional explanation."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "ProfileAuditor",
    }

    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"RESUME TEXT:\n\n{raw_text[:8000]}"}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        print(f"🤖 Querying OpenRouter model '{model_name}' for structured resume parsing...")
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=body, timeout=30)
        
        if response.status_code != 200:
            print(f"OpenRouter extraction returned status {response.status_code}: {response.text}")
            return None

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return None

        content = choices[0].get("message", {}).get("content", "")
        clean_json = _clean_json_text(content)
        parsed = json.loads(clean_json)
        print("✅ Successfully extracted and parsed JSON from OpenRouter")
        return parsed

    except Exception as e:
        print(f"⚠️ OpenRouter extraction error: {e}")
        return None


def _call_gemini_extraction(raw_text: str) -> Optional[Dict[str, Any]]:
    """Fallback to Google Gemini SDK if configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not genai:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", GEMINI_MODEL))
        prompt = (
            "You are an expert resume parser. Output ONLY a valid JSON object extracting:\n"
            "name, email, phone, technical_skills (list), soft_skills (list), "
            "projects (list of {name, description}), experience (list), education (list), "
            "github_username, leetcode_username.\n"
            "Do NOT include hackathons/awards as projects. Distinguish technical vs soft skills strictly.\n\n"
            f"RESUME TEXT:\n{raw_text[:8000]}"
        )
        resp = model.generate_content(prompt)
        text = _clean_json_text(resp.text or "")
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ Gemini extraction error: {e}")
        return None


def _fallback_extract_information(text: str) -> Dict[str, Any]:
    """
    Clean, generic heuristic extraction used only if LLM APIs are completely unavailable/offline.
    """
    print("ℹ️ Running generic fallback parser (offline/no LLM key)...")
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', text)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    
    name = None
    for line in text.split('\n')[:5]:
        line_clean = line.strip()
        if line_clean and not re.search(r'[@\(\)\+\d]|resume|curriculum|email|phone', line_clean, re.IGNORECASE):
            name = line_clean
            break

    common_tech = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Rust",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI",
        "HTML", "CSS", "Tailwind", "Bootstrap", "SQL", "PostgreSQL", "MySQL", "MongoDB",
        "AWS", "Docker", "Kubernetes", "Git", "GitHub", "Solidity", "GraphQL", "REST API"
    ]
    
    common_soft = [
        "Leadership", "Communication", "Public Speaking", "Community Management",
        "Teamwork", "Problem Solving", "Time Management", "Project Management"
    ]

    found_tech = [t for t in common_tech if re.search(r'\b' + re.escape(t) + r'\b', text, re.IGNORECASE)]
    found_soft = [s for s in common_soft if re.search(r'\b' + re.escape(s) + r'\b', text, re.IGNORECASE)]

    projects = []
    project_sec = re.search(r'(?i)projects?\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z\s]{4,}\s*[:\n]|$))', text, re.DOTALL)
    if project_sec:
        for line in project_sec.group(1).split('\n'):
            line = line.strip()
            dash_match = re.match(r'^([^—\n]+?)\s*—\s*([^[\n]+)', line)
            if dash_match:
                p_name = re.sub(r'\[.*?\]', '', dash_match.group(1)).strip()
                p_desc = re.sub(r'\[.*?\]', '', dash_match.group(2)).strip()
                if len(p_name) >= 3:
                    projects.append({"name": p_name, "description": p_desc})

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "technical_skills": found_tech,
        "soft_skills": found_soft,
        "skills": found_tech,
        "projects": projects,
        "experience": [],
        "education": [],
        "github_username": extract_github_username(text),
        "leetcode_username": extract_leetcode_username(text),
        "status": "completed"
    }


def extract_information(text: str) -> Dict[str, Any]:
    """
    Main extraction pipeline:
    1. Runs LLM-based structured extraction (OpenRouter -> Gemini).
    2. Falls back to generic heuristic parser if no LLM response.
    3. Runs authoritative social handle extractors (GitHub, LeetCode) on raw text.
    4. Ensures clean data contract (technical_skills, soft_skills, projects).
    """
    print(f"Starting structured extraction on resume text ({len(text)} chars)...")
    
    # 1. Attempt LLM Structured Extraction
    parsed = _call_openrouter_extraction(text)
    if not parsed:
        parsed = _call_gemini_extraction(text)
    
    # 2. Fallback to generic offline parser if LLM failed
    if not parsed:
        parsed = _fallback_extract_information(text)

    # 3. Authoritative Handle Detection from Raw Text
    raw_github = extract_github_username(text)
    raw_leetcode = extract_leetcode_username(text)

    github_user = raw_github or parsed.get("github_username")
    if github_user and isinstance(github_user, str):
        github_user = github_user.replace("https://github.com/", "").replace("github.com/", "").strip().strip("/").strip("@")
        parsed["github_username"] = github_user
    else:
        parsed["github_username"] = None

    leetcode_user = raw_leetcode or parsed.get("leetcode_username")
    if leetcode_user and isinstance(leetcode_user, str):
        leetcode_user = leetcode_user.replace("https://leetcode.com/u/", "").replace("https://leetcode.com/", "").replace("leetcode.com/u/", "").replace("leetcode.com/", "").strip().strip("/").strip("@")
        parsed["leetcode_username"] = leetcode_user
    else:
        parsed["leetcode_username"] = None

    # 4. Standardize technical vs soft skills
    tech_skills = parsed.get("technical_skills") or []
    soft_skills = parsed.get("soft_skills") or []
    
    parsed["technical_skills"] = [str(s).strip() for s in tech_skills if str(s).strip()]
    parsed["soft_skills"] = [str(s).strip() for s in soft_skills if str(s).strip()]
    parsed["skills"] = parsed["technical_skills"]

    # 5. Clean projects
    raw_projects = parsed.get("projects") or []
    cleaned_projects = []
    for p in raw_projects:
        if isinstance(p, dict) and p.get("name"):
            cleaned_projects.append({
                "name": str(p["name"]).strip(),
                "description": str(p.get("description", "")).strip()
            })
        elif isinstance(p, str) and p.strip():
            cleaned_projects.append({
                "name": p.strip(),
                "description": ""
            })
    parsed["projects"] = cleaned_projects
    parsed["status"] = "completed"

    print(f"=== EXTRACTION COMPLETE ===")
    print(f"Candidate: {parsed.get('name')}")
    print(f"GitHub Handle: {parsed.get('github_username')}")
    print(f"LeetCode Handle: {parsed.get('leetcode_username')}")
    print(f"Technical Skills ({len(parsed['technical_skills'])}): {parsed['technical_skills']}")
    print(f"Soft Skills ({len(parsed['soft_skills'])}): {parsed['soft_skills']}")
    print(f"Projects ({len(parsed['projects'])}): {[p['name'] for p in parsed['projects']]}")

    return parsed

    # 4. Standardize technical vs soft skills
    tech_skills = parsed.get("technical_skills") or []
    soft_skills = parsed.get("soft_skills") or []
    
    # Ensure lists of clean strings
    parsed["technical_skills"] = [str(s).strip() for s in tech_skills if str(s).strip()]
    parsed["soft_skills"] = [str(s).strip() for s in soft_skills if str(s).strip()]
    # Populate "skills" with technical_skills for backwards compatibility
    parsed["skills"] = parsed["technical_skills"]

    # 5. Clean projects
    raw_projects = parsed.get("projects") or []
    cleaned_projects = []
    for p in raw_projects:
        if isinstance(p, dict) and p.get("name"):
            cleaned_projects.append({
                "name": str(p["name"]).strip(),
                "description": str(p.get("description", "")).strip()
            })
        elif isinstance(p, str) and p.strip():
            cleaned_projects.append({
                "name": p.strip(),
                "description": ""
            })
    parsed["projects"] = cleaned_projects
    parsed["status"] = "completed"

    print(f"=== EXTRACTION COMPLETE ===")
    print(f"Candidate: {parsed.get('name')}")
    print(f"GitHub Handle: {parsed.get('github_username')}")
    print(f"Technical Skills ({len(parsed['technical_skills'])}): {parsed['technical_skills']}")
    print(f"Soft Skills ({len(parsed['soft_skills'])}): {parsed['soft_skills']}")
    print(f"Projects ({len(parsed['projects'])}): {[p['name'] for p in parsed['projects']]}")

    return parsed


def parse_resume(file_path: str) -> Dict[str, Any]:
    """Parse resume file and extract information."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith((".doc", ".docx")):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    return extract_information(text)


def parse_resume_with_text(file_path: str) -> Tuple[Dict[str, Any], str]:
    """Parse resume file, returning both structured data and the raw extracted text."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith((".doc", ".docx")):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    parsed_data = extract_information(text)
    return parsed_data, text
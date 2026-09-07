# Diagnostic Report: Resume Parsing & Verification Architecture

## Executive Summary & Architectural Findings

### 1. Skill & Project Extraction Mechanism
- **100% Regex, Keyword Lists, and Heuristic Rules**:
  - **spaCy**: Initialized as a blank English model (`spacy.blank("en")`) with a dummy fallback class (`SimpleNLP`). It is **not** used for Named Entity Recognition (NER).
  - **GPT / LLM**: **Not invoked at all during resume parsing or extraction**. The only LLM call occurs much later in `scoring_service.py` to synthesize a text explanation for the final Reality Score.
  - **Skills**: Matched using a hardcoded array of `skill_keywords` in `extract_skills()` via regex word boundaries (`\b<skill>\b`), supplemented by regex section extractors (e.g. `r'(?i)programming\s*[:\n]'`, `r'(?i)soft\s+skills?\s*[:\n]'`).
  - **Projects**: Matched using regex looking for em-dash/hyphen separators (`r'(?:^|\n)\s*([A-Z][A-Za-z0-9\s,-]{2,50})\s*—\s*([^[\n]+?)'`) and keyword heuristics (`platform`, `app`, `system`, etc.).
  - **Hardcoded candidate-specific artifacts**: The codebase contains hardcoded strings tailored to specific candidate resumes (e.g., regexes rejecting names `"vishvjeet"`, `"tanwar"`, `"1623"`, and a dictionary manually fixing broken words like `"Ques tfi"` → `"Questfi"` and `"Profile Audit or"` → `"Profile Auditor"`).

### 2. Treatment of "Technical" vs. "Soft" Skills
- **Identical treatment with zero categorization**:
  - Soft skills (`"Leadership"`, `"Public Speaking"`, `"Community Management"`, `"Teamwork"`) are explicitly present in `skill_keywords` and parsed from the resume or inferred from achievements.
  - All extracted skills are aggregated into a single flat list: `skills: List[str]`.
  - During the verification phase in `backend/app/api/endpoints/verification.py`, every extracted skill is checked against GitHub repository languages, repo names, and commit logs.
  - Because GitHub cannot corroborate soft skills (e.g., `"Community Management"` has no matching repository language or commit), they are automatically appended to `unverified_skills`.
  - In `backend/app/services/scoring_service.py`, `calculate_skills_score()` calculates `len(verified_skills) / (len(verified_skills) + len(unverified_skills)) * 100`. Therefore, having soft skills on a resume directly lowers the candidate's Reality Score.

---

## 1. Resume Upload / Parsing Endpoint
**File:** `backend/app/api/endpoints/resume.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import uuid
import os
from typing import Optional

from app.services.resume_parser import parse_resume, parse_resume_with_text
from app.models.resume import ResumeResponse, ResumeData

router = APIRouter()

# In-memory storage for demo purposes (would use a database in production)
resume_storage = {}

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None)
):
    """Upload and parse a resume file (PDF or DOC)"""
    print(f"\n\n===== RESUME UPLOAD =====\nFilename: {file.filename}")
    
    # Generate a unique ID for this resume
    resume_id = str(uuid.uuid4())
    print(f"Generated resume_id: {resume_id}")
    
    # Check file type (case-insensitive) and only allow PDF or DOCX
    filename_lower = (file.filename or "").lower()
    if not filename_lower.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX")
    
    # Save file temporarily - use /tmp in serverless environments
    temp_dir = "/tmp" if os.environ.get("VERCEL") else os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Temp directory: {temp_dir}")
    
    file_location = os.path.join(temp_dir, f"{resume_id}_{file.filename}")
    print(f"Saving file to: {file_location}")
    
    try:
        # Create file
        with open(file_location, "wb") as f:
            contents = await file.read()
            f.write(contents)
            print(f"File saved successfully, size: {len(contents)} bytes")
        
        # Verify file was saved correctly
        if not os.path.exists(file_location):
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
            
        # Initialize resume data in storage with status
        resume_storage[resume_id] = {"status": "processing"}
        print(f"Resume {resume_id} added to storage with 'processing' status")
        
        # Process resume synchronously for serverless compatibility
        try:
            process_resume(
                resume_id=resume_id,
                file_path=file_location,
                name=name,
                email=email
            )
            print(f"Resume processing completed for {resume_id}")
            
            # Check if processing was successful
            if resume_id in resume_storage and resume_storage[resume_id].get("status") == "completed":
                return ResumeResponse(
                    resume_id=resume_id,
                    message="Resume uploaded and processed successfully",
                    status="completed"
                )
            else:
                # Processing failed
                error_msg = resume_storage.get(resume_id, {}).get("error", "Unknown processing error")
                raise HTTPException(status_code=400, detail=error_msg)
                
        except Exception as process_error:
            print(f"Resume processing failed: {str(process_error)}")
            raise HTTPException(status_code=400, detail=f"Resume processing failed: {str(process_error)}")
    
    except Exception as e:
        print(f"Error during resume upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/{resume_id}", response_model=ResumeData)
async def get_resume(resume_id: str):
    """Get parsed resume data"""
    if resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume_data = resume_storage[resume_id]
    
    # Check if processing is complete
    if resume_data.get("status") == "processing":
        return JSONResponse(
            status_code=202,
            content={"resume_id": resume_id, "status": "processing", "message": "Resume is still being processed"}
        )
    
    return resume_data

@router.get("/{resume_id}/debug")
async def debug_resume(resume_id: str):
    """Debug endpoint to see raw parsed data"""
    if resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume_data = resume_storage[resume_id]
    
    return {
        "resume_id": resume_id,
        "raw_data": resume_data,
        "projects_count": len(resume_data.get("projects", [])),
        "skills_count": len(resume_data.get("skills", [])),
        "projects": resume_data.get("projects", []),
        "skills": resume_data.get("skills", []),
        "status": resume_data.get("status", "unknown")
    }

@router.post("/test/{resume_id}")
async def create_test_resume(resume_id: str):
    """Create a test resume for verification testing"""
    print(f"Creating test resume with ID: {resume_id}")
    
    # Create a test resume with the problematic project description to test the fix
    if resume_id == "test-decentralized-project":
        resume_storage[resume_id] = {
            "resume_id": resume_id,
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "JavaScript", "Blockchain", "Data Analysis"],
            "projects": [{"name": "A Decentralised Data Sharing and Monetization platform based decentralized platform", "description": "A comprehensive platform for decentralized data sharing and monetization"}],
            "status": "completed"
        }
    else:
        # Create a standard test resume with skills and projects for verification
        resume_storage[resume_id] = {
            "resume_id": resume_id,
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "JavaScript", "Leadership", "Community Management"],
            "projects": [{"name": "Resume Parser", "description": "AI-powered resume parsing system"}, {"name": "Personal Website", "description": "Portfolio website built with React"}],
            "status": "completed"
        }
    
    print(f"Test resume created: {resume_storage[resume_id]}")
    
    return {"resume_id": resume_id, "message": "Test resume created successfully", "status": "completed"}

def process_resume(resume_id: str, file_path: str, name: Optional[str], email: Optional[str]):
    """Process the resume file and extract information"""
    try:
        # Store initial processing status
        resume_storage[resume_id] = {"resume_id": resume_id, "status": "processing"}
        print(f"\n===== PROCESSING RESUME =====\nID: {resume_id}\nFile: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        # Ensure file exists
        if not os.path.exists(file_path):
            error_msg = f"Resume file not found at {file_path}"
            print(f"File not found: {file_path}")
            resume_storage[resume_id] = {"resume_id": resume_id, "status": "error", "error": error_msg}
            return
        
        # Parse the resume
        print(f"Parsing resume file: {file_path}")
        parsed_data, raw_text = parse_resume_with_text(file_path)
        print(f"Parsed data: {parsed_data}")
        
        # Ensure parsed_data is a dictionary
        if not isinstance(parsed_data, dict):
            error_msg = f"Invalid resume data format: {type(parsed_data)}"
            print(error_msg)
            resume_storage[resume_id] = {"resume_id": resume_id, "status": "error", "error": error_msg}
            return
        
        # Quick heuristic to detect non-resume uploads
        try:
            text = (raw_text or "").lower()
            signals = 0
            if parsed_data.get("email"): signals += 1
            if parsed_data.get("phone"): signals += 1
            if parsed_data.get("skills"): signals += 1
            if parsed_data.get("education"): signals += 1
            if parsed_data.get("experience"): signals += 1
            if parsed_data.get("projects"): signals += 1
            # Look for common resume section keywords
            keywords = ["experience", "work experience", "education", "skills", "projects", "summary", "objective", "certifications"]
            if any(k in text for k in keywords):
                signals += 1
            # If very weak signals and short text, consider not a resume
            if signals <= 1 or (len(text) < 300 and signals <= 2):
                error_msg = "This is not a resume"
                resume_storage[resume_id] = {"resume_id": resume_id, "status": "error", "error": error_msg}
                print(f"Heuristic rejection: {error_msg}")
                return
        except Exception as _:
            pass
        
        # Add additional information (note: UI no longer sends these, but keep for compatibility)
        if name:
            parsed_data["name"] = name
        if email:
            parsed_data["email"] = email
        
        # Ensure skills exist and are in the correct format (fallback defaults only after validation)
        if not parsed_data.get("skills"):
            print("No skills found, adding default skills")
            parsed_data["skills"] = ["Python", "Data Analysis", "Communication"]
        
        # Keep projects as-is; do not inject default project. This ensures only resume-derived project names are used.
        
        # Update storage with parsed data
        parsed_data["resume_id"] = resume_id
        parsed_data["status"] = "completed"
        resume_storage[resume_id] = parsed_data
        print(f"Resume processed successfully: {resume_id}")
        print(f"Final resume data structure: {parsed_data}")
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        error_msg = f"Error processing resume: {str(e)}"
        print(error_msg)
        # Update storage with error
        resume_storage[resume_id] = {
            "resume_id": resume_id,
            "status": "error",
            "error": str(e)
        }
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
```

---

## 2. Resume Text Extraction Logic (PDF/DOC → Raw Text)
**File:** `backend/app/services/resume_parser.py` (Lines 95–233)

```python
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using multiple fallback libraries for best results"""
    print(f"\n=== PDF EXTRACTION START ===")
    print(f"Extracting text from PDF: {file_path}")
    
    # Run all extraction methods and compare outputs
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
        except Exception as e:
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
        except Exception as e:
            extraction_results['pymupdf'] = ''

    # Method 3: pdfminer
    if PDFMINER_AVAILABLE:
        try:
            extracted_text = pdfminer_extract_text(file_path)
            extraction_results['pdfminer'] = extracted_text
        except Exception as e:
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
    except Exception as e:
        extraction_results['pypdf2'] = ''

    # Clean and score all results
    cleaned_results = {}
    for method, raw_text in extraction_results.items():
        cleaned = clean_pdf_text(raw_text or "")
        cleaned_results[method] = cleaned

    # Heuristic: pick the result with the most unique words and length
    def score(text):
        words = set(text.split())
        return (len(words), len(text))

    best_method = max(cleaned_results, key=lambda m: score(cleaned_results[m]))
    best_text = cleaned_results[best_method]

    print(f"Best PDF extraction method: {best_method} ({len(best_text)} chars, {len(set(best_text.split()))} unique words)")

    # Show sample for debugging projects section
    if "PROJECTS" in best_text.upper():
        project_start = best_text.upper().find("PROJECTS")
        if project_start >= 0:
            sample = best_text[project_start:project_start + 500]
            print(f"PROJECTS section sample: {repr(sample[:200])}...")

    print(f"=== PDF EXTRACTION COMPLETE ===")
    print(f"Final cleaned text: {len(best_text)} characters")
    return best_text.strip()

def clean_pdf_text(text: str) -> str:
    """Clean and normalize PDF extracted text"""
    if not text:
        return ""
    
    # Remove null characters
    text = text.replace('\x00', ' ')
    
    # Normalize Unicode characters (preserve em-dashes and special chars)
    # Convert various dash types to em-dash for consistency
    text = text.replace('–', '—')  # en-dash to em-dash
    text = text.replace('−', '—')  # minus to em-dash
    
    # Fix common PDF extraction issues while preserving important formatting
    # Remove excessive whitespace but preserve line breaks
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n[ \t]+', '\n', text)  # Remove leading whitespace on lines
    text = re.sub(r'[ \t]+\n', '\n', text)  # Remove trailing whitespace on lines
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double newline
    
    # Fix broken words (but be more conservative to avoid breaking intentional formatting)
    # Only fix obvious cases where single letters are separated
    text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z]{2,})\b', r'\1\2\3', text)
    
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file with improved handling of formatting"""
    print(f"Extracting text from DOCX: {file_path}")
    
    try:
        doc = docx.Document(file_path)
        text = ""
        
        # Extract from paragraphs
        for para in doc.paragraphs:
            para_text = para.text.strip()
            if para_text:
                text += para_text + "\n"
        
        # Extract from tables (if any)
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        row_text.append(cell_text)
                if row_text:
                    text += " ".join(row_text) + "\n"
        
        print(f"DOCX: Successfully extracted {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        print(f"DOCX extraction failed: {e}")
        return ""
```

---

## 3. Skill & Project Extraction Logic
**File:** `backend/app/services/resume_parser.py` (Lines 363–465, 466–525, 527–837, 838–980, 982–1085, 1088–1123)

```python
def extract_skills(doc, text: str) -> List[str]:
    """Extract skills from text"""
    # Ensure we have text to work with
    if not text and isinstance(doc, str):
        text = doc
    # Common skill keywords and programming languages
    skill_keywords = [
        "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin",
        "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring",
        "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "AI", "NLP",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Firebase", "AWS", "Azure", "GCP",
        "Docker", "Kubernetes", "CI/CD", "Git", "GitHub", "DevOps", "Agile", "Scrum",
        "HTML", "CSS", "SASS", "LESS", "Bootstrap", "Tailwind", "Material UI",
        "REST API", "GraphQL", "Microservices", "Serverless", "Linux", "Unix",
        "Data Analysis", "Data Science", "Big Data", "Hadoop", "Spark", "Tableau",
        "Power BI", "Excel", "VBA", "R", "MATLAB", "SAS", "SPSS", "Stata",
        "TypeScript", "Go", "Rust", "Scala", "Perl", "COBOL", "Fortran",
        "jQuery", "Redux", "Next.js", "Gatsby", "Svelte", "Ember", "Backbone",
        "Laravel", "CodeIgniter", "Symfony", "Rails", "Sinatra", "ASP.NET",
        "Pandas", "NumPy", "Scikit-learn", "Keras", "OpenCV", "NLTK", "SpaCy",
        "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "Oracle", "SQLite",
        "Jenkins", "GitLab", "CircleCI", "Travis", "Ansible", "Terraform", "Vagrant",
        "Figma", "Sketch", "Adobe", "Photoshop", "Illustrator", "InDesign", "XD",
        "Project Management", "Leadership", "Communication", "Problem Solving", "Teamwork",
        "C", "Solidity", "VS Code", "Canva", "Notion", "Public Speaking", "Community Management"
    ]
    
    # Look for skill keywords in text (only from dedicated skills sections)
    found_skills = []
    
    print(f"=== SKILLS EXTRACTION START ===")
    print(f"Text length: {len(text)}")
    
    # Look for skill sections with more flexible patterns - but be very strict about what we extract
    skill_section_patterns = [
        r'(?i)(?:technical\s+)?skills?\s*[:\n]\s*(.*?)(?=\n\s*(?:PROJECTS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)',
        r'(?i)programming\s*[:\n]\s*(.*?)(?=\n\s*(?:tools?|soft\s+skills?|languages?|projects?|experience|education)\s*[:\n]|$)',
        r'(?i)tools?\s*[:\n]\s*(.*?)(?=\n\s*(?:soft\s+skills?|languages?|projects?|experience|education|social\s+handles?)\s*[:\n]|$)',
        r'(?i)soft\s+skills?\s*[:\n]\s*(.*?)(?=\n\s*(?:languages?|projects?|experience|education|social\s+handles?)\s*[:\n]|$)',
        r'(?i)competencies[:\n]\s*(.*?)(?=\n\s*(?:PROJECTS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)',
        r'(?i)technologies[:\n]\s*(.*?)(?=\n\s*(?:PROJECTS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)',
        r'(?i)programming\s+languages?\s*[:\n]\s*(.*?)(?=\n\s*(?:PROJECTS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)',
        r'(?i)tools?\s+and\s+technologies[:\n]\s*(.*?)(?=\n\s*(?:PROJECTS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)'
    ]
    
    # First, look for skills only from predefined skill keywords in the text
    for skill in skill_keywords:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    
    # Then, look for additional skills only in dedicated skills sections
    for pattern in skill_section_patterns:
        skill_matches = re.findall(pattern, text, re.DOTALL)
        if skill_matches:
            print(f"Found skills section with pattern: {len(skill_matches)} matches")
            for match in skill_matches:
                # Split by common separators including bullets, commas, pipes, newlines
                skills_text = match.strip()
                print(f"Processing skills text: {skills_text[:200]}...")
                
                # Split by various separators
                skills_list = re.split(r'[,•|•\n\t;/\\·▪▫◦‣⁃]+', skills_text)
                for skill in skills_list:
                    skill = re.sub(r'^[^\w]+|[^\w]+$', '', skill.strip())  # Remove leading/trailing non-word chars
                    skill = skill.strip()
                    
                    if skill and len(skill) > 1 and skill not in found_skills:
                        # Very strict filtering - only allow actual skills
                        if (skill.lower() not in ['and', 'or', 'with', 'using', 'including', 'etc', 'the', 'of', 'in', 'languages', 'english', 'hindi', 'skills', 'programming', 'tools', 'soft'] and
                            # Exclude project-like names
                            not any(keyword in skill.lower() for keyword in ['platform', 'app', 'website', 'portal', 'system', 'dashboard', 'service', 'roots', 'questfi', 'auditor', 'network', 'data sharing', 'monetization', 'bounty', 'verification', 'reality score']) and
                            # Exclude things that look like project descriptions
                            not re.search(r'—|–|-.*(?:platform|app|website|system|tool)', skill.lower()) and
                            # Exclude social media handles and usernames
                            not re.search(r'@\w+|linkedin\.com|github\.com|twitter\.com|vishvjeet|tanwar|vishvjeettanwar|1623|gmail\.com', skill.lower()) and
                            # Exclude URLs and links
                            not re.search(r'https?://|www\.|\.com|\.org|\.net|\[link\]|github\s*-\s*https|twitter\s*-\s*https|linkedin\s*-\s*https', skill.lower(), re.IGNORECASE) and
                            # Exclude very long strings that are likely descriptions
                            len(skill) < 30 and
                            # Exclude obvious non-skills
                            not re.search(r'\d{4}|\b(?:unverified|verified)\b', skill.lower()) and
                            # Don't exclude common soft skills
                            (skill in skill_keywords or 
                             skill.lower() in ['leadership', 'public speaking', 'community management', 'problem solving', 'teamwork', 'communication'] or
                             any(tech in skill.lower() for tech in ['programming', 'development', 'design', 'analysis', 'management', 'testing', 'deployment', 'script', 'code']))):
                            found_skills.append(skill)
                            print(f"✅ Added skill: {skill}")
                        else:
                            print(f"❌ Rejected skill: {skill}")
    
    # Remove duplicates while preserving order
    unique_skills = []
    seen = set()
    for skill in found_skills:
        if skill.lower() not in seen:
            unique_skills.append(skill)
            seen.add(skill.lower())
    
    print(f"=== SKILLS EXTRACTION COMPLETE ===")
    print(f"Found {len(unique_skills)} skills: {unique_skills}")
    
    return unique_skills

def fix_pdf_extraction_issues(text: str) -> str:
    """Fix common PDF extraction issues that break project names"""
    if not text:
        return text
    
    print("🔧 Fixing PDF extraction issues...")
    
    # Fix specific broken project names first (most important)
    fixes = {
        # Project name fixes
        'Ques tfi': 'Questfi',
        'Quest fi': 'Questfi', 
        'Que stfi': 'Questfi',
        'Profile Audit or': 'Profile Auditor',
        'Profile Audit': 'Profile Auditor',  # if 'or' is on next line
        'Data\nRoots': 'Data Roots',
        'Data \nRoots': 'Data Roots',
        'Data\n Roots': 'Data Roots',
        
        # Common broken words
        'block chain': 'blockchain',
        'Block chain': 'Blockchain',
        'real ity': 'reality',
        'Real ity': 'Reality',
        'plat form': 'platform',
        'Plat form': 'Platform',
        'net work': 'network',
        'Net work': 'Network',
        'data base': 'database',
        'Data base': 'Database',
        'web site': 'website',
        'Web site': 'Website',
        'app lication': 'application',
        'App lication': 'Application',
        'ver ification': 'verification',
        'Ver ification': 'Verification',
        'monetiz ation': 'monetization',
        'Monetiz ation': 'Monetization',
        'decent ralized': 'decentralized',
        'Decent ralized': 'Decentralized',
        'shar ing': 'sharing',
        'Shar ing': 'Sharing'
    }
    
    # Apply specific fixes
    for broken, fixed in fixes.items():
        if broken in text:
            text = text.replace(broken, fixed)
            print(f"  Fixed: '{broken}' → '{fixed}'")
    
    # Fix broken words using regex (more general patterns)
    # Pattern: single letter followed by space and rest of word
    text = re.sub(r'\b([A-Z])ues tfi\b', r'\1uestfi', text)  # Specific for Questfi variants
    text = re.sub(r'\bQues ([a-z]fi)\b', r'Quest\1', text)   # Questfi variants
    
    # General pattern for broken compound words (be conservative)
    # Only fix obvious cases where we have a capital + lowercase fragment
    text = re.sub(r'\b([A-Z][a-z]+)\s+([a-z]{2,})\b(?=\s+(?:[A-Z]|—|-|$))', r'\1\2', text)
    
    return text

def extract_projects(doc_or_text, text: str = None) -> List[Dict[str, Any]]:
    """Extract projects from text - supports both (doc, text) and (text) calling patterns"""
    # Handle different calling patterns
    if text is None:
        # Called with single parameter: extract_projects(text)
        if isinstance(doc_or_text, str):
            text = doc_or_text
            doc = None
        else:
            # Called with spaCy doc only
            doc = doc_or_text
            text = str(doc) if hasattr(doc, 'text') else str(doc)
    else:
        # Called with two parameters: extract_projects(doc, text)
        doc = doc_or_text
        if not text and isinstance(doc, str):
            text = doc
    projects = []
    
    print(f"\n=== PROJECT EXTRACTION START ===")
    print(f"Text length: {len(text)}")
    print(f"Text contains 'PROJECTS': {'PROJECTS' in text.upper()}")
    print(f"Text contains 'Data Roots': {'Data Roots' in text}")
    print(f"Text contains 'Questfi': {'Questfi' in text}")
    print(f"Text contains broken 'Ques tfi': {'Ques tfi' in text}")
    print(f"Text contains broken 'Profile Audit or': {'Profile Audit or' in text}")
    print(f"First 500 chars: {text[:500]}")
    
    # Fix common PDF extraction issues BEFORE pattern matching
    text = fix_pdf_extraction_issues(text)
    print(f"After PDF fixes - Text contains 'Questfi': {'Questfi' in text}")
    print(f"After PDF fixes - Text contains 'Profile Auditor': {'Profile Auditor' in text}")
    
    # Enhanced pattern matching for PDF format
    # Support multiple dash variations and space patterns that PDF extraction creates
    em_dash_patterns = [
        r'(?:^|\n)\s*([A-Z][A-Za-z0-9\s,-]{2,50})\s*—\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*(?=\n|$)',  # em-dash
        r'(?:^|\n)\s*([A-Z][A-Za-z0-9\s,-]{2,50})\s*[-–]\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*(?=\n|$)',  # en-dash or hyphen
        r'(?:^|\n)\s*([A-Z][A-Za-z0-9\s,-]{2,50})\s{3,}\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*(?=\n|$)'  # multiple spaces (PDF conversion)
    ]
    
    total_em_dash_matches = []
    for i, pattern in enumerate(em_dash_patterns):
        matches = re.findall(pattern, text, re.MULTILINE)
        print(f"Pattern {i+1} found {len(matches)} matches")
        total_em_dash_matches.extend(matches)
    
    print(f"Found {len(total_em_dash_matches)} total dash/space matches")
    
    def clean_project_name(name: str) -> str:
        # Remove any trailing repeated syllables (e.g., 'Auditoror', 'Managerer', etc.)
        for _ in range(3):
            name = re.sub(r'(\b\w{3,}?)(or|er|ar|ur|ir)+\b', r'\1', name, flags=re.IGNORECASE)
        # Remove accidental double words (e.g., 'Profile Auditor Auditor')
        name = re.sub(r'\b(\w+) \1\b', r'\1', name)
        # Remove special characters, extra spaces
        name = re.sub(r'[^a-zA-Z0-9\s\-]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip().title()

    for match in total_em_dash_matches:
        raw_project_name = match[0].strip()
        project_name = clean_project_name(raw_project_name)
        project_desc = match[1].strip()

        print(f"Checking dash match: '{raw_project_name}' (cleaned: '{project_name}') — '{project_desc}'")
        # ...existing code...
    
    # Also look for projects in a dedicated PROJECTS section (but exclude achievements section)
    project_section_patterns = [
        r'(?i)projects?\s*[:\n]\s*(.*?)(?=\n\s*(?:ACHIEVEMENTS?\s*&\s*EXTRA|ACHIEVEMENTS?|AWARDS?|SKILLS?|EXPERIENCE|EDUCATION|WORK\s+EXPERIENCE|EMPLOYMENT|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?|EXTRACURRICULAR|ACTIVITIES|VOLUNTEER|LEADERSHIP|SOCIAL\s+HANDLES?)\s*[:\n]|$)'
    ]
    
    for pattern in project_section_patterns:
        project_matches = re.findall(pattern, text, re.DOTALL)
        print(f"Pattern found {len(project_matches)} matches")
        
        if project_matches:
            for match in project_matches:
                project_text = match.strip()
                print(f"Processing project section ({len(project_text)} chars): {project_text[:200]}...")
                
                # Look for em-dash projects within this section with improved regex (all dash variations)
                section_matches = []
                for pattern_variant in em_dash_patterns:
                    variant_matches = re.findall(pattern_variant, project_text, re.MULTILINE)
                    section_matches.extend(variant_matches)
                    
                for em_match in section_matches:
                    project_name = em_match[0].strip()
                    project_desc = em_match[1].strip()
                    
                    # Clean project name by removing [Link] annotations
                    project_name = re.sub(r'\[.*?\]', '', project_name).strip()
                    
                    # Skip achievements content
                    if any(keyword in (project_name + " " + project_desc).lower() for keyword in ['prize', 'award', 'hackathon', 'competition', 'winner', 'achievement', 'certificate', 'honor']):
                        print(f"❌ Rejected section match: '{project_name}' (achievements content)")
                        continue
                    
                    # Skip achievements content in section matches too
                    achievement_keywords = ['prize', 'award', 'hackathon', 'competition', 'winner', 'achievement', 'certificate', 'honor', 'built a blockchain', 'engaged in a national', 'demonstrating problem-solving', '3rd prize', '30th position', 'completed a 21', 'algohour', 'regional hackathon']
                    social_keywords = ['twitter', 'gmail', 'linkedin', 'github', 'email', 'phone', '.com', '@', 'www.', 'http', 'https']
                    experience_keywords = ['intern', 'internship', 'remote', 'present', 'hackquest', 'offscript', 'advocate', 'building and managing', 'promoting web3']
                    
                    combined_text = (project_name + " " + project_desc).lower()
                    
                    if any(keyword in combined_text for keyword in achievement_keywords):
                        print(f"❌ Rejected section match: '{project_name}' (achievements content)")
                        continue
                        
                    if any(keyword in combined_text for keyword in social_keywords):
                        print(f"❌ Rejected section match: '{project_name}' (social media/contact content)")
                        continue
                        
                    if any(keyword in combined_text for keyword in experience_keywords):
                        print(f"❌ Rejected section match: '{project_name}' (experience/work content)")
                        continue
                    
                    # Check if this appears to be from achievements section by checking context
                    match_pos = project_text.find(project_name)
                    if match_pos > 0:
                        preceding_text = project_text[max(0, match_pos - 200):match_pos].lower()
                        if any(keyword in preceding_text for keyword in ['achievements', 'extra-curricular', 'hackathon', 'competition', 'prize']):
                            print(f"❌ Rejected section match: '{project_name}' (found in achievements context)")
                            continue
                    
                    if project_name and len(project_name) >= 3:
                        # Check if we already have this project
                        existing_names = [p['name'].lower() for p in projects]
                        if project_name.lower() not in existing_names:
                            projects.append({
                                "name": project_name,
                                "description": project_desc
                            })
                            print(f"✅ Added section project: '{project_name}'")
                
                # Also try other parsing methods for this section
                parsed_projects = parse_project_section(project_text)
                for proj in parsed_projects:
                    existing_names = [p['name'].lower() for p in projects]
                    if proj['name'].lower() not in existing_names:
                        # Skip achievements content in parsed projects too
                        achievement_keywords = ['prize', 'award', 'hackathon', 'competition', 'winner', 'achievement', 'certificate', 'honor', 'built a blockchain', 'engaged in a national', 'demonstrating problem-solving', '3rd prize', '30th position', 'completed a 21', 'algohour', 'regional hackathon']
                        social_keywords = ['twitter', 'gmail', 'linkedin', 'github', 'email', 'phone', '.com', '@', 'www.', 'http', 'https']
                        experience_keywords = ['intern', 'internship', 'remote', 'present', 'hackquest', 'offscript', 'advocate', 'building and managing', 'promoting web3']
                        
                        combined_text = (proj['name'] + " " + proj.get('description', '')).lower()
                        
                        if not any(keyword in combined_text for keyword in achievement_keywords + social_keywords + experience_keywords):
                            projects.append(proj)
                            print(f"✅ Added parsed project: '{proj['name']}'")
                        else:
                            print(f"❌ Rejected parsed project: '{proj['name']}' (unwanted content)")
                
                # Additional PDF-style parsing for this section (space-separated instead of dash-separated)
                print("Trying PDF-style parsing within projects section...")
                section_lines = project_text.split('\n')
                for line in section_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Remove [Link] annotations
                    clean_line = re.sub(r'\[.*?\]', '', line).strip()
                    
                    # Look for lines that contain project keywords but no dashes
                    if (any(keyword in clean_line.lower() for keyword in ['platform', 'app', 'website', 'system', 'tool', 'network', 'blockchain', 'data', 'bounty', 'verification', 'auditor', 'sharing', 'monetization']) and
                        '—' not in clean_line and '-' not in clean_line):
                        
                        # Try to split into name and description
                        words = clean_line.split()
                        if len(words) >= 3:
                            # Try different split points, preferring longer names for compound project names
                            best_split = None
                            best_score = 0
                            
                            for split_point in range(1, min(5, len(words))):  # Allow up to 4-word project names
                                potential_name = ' '.join(words[:split_point])
                                potential_desc = ' '.join(words[split_point:])
                                
                                # Score this split based on how well it separates name vs description
                                score = 0
                                
                                # Prefer names that are proper nouns (title case)
                                if all(word[0].isupper() for word in potential_name.split() if word):
                                    score += 2
                                
                                # Prefer descriptions that contain action/descriptive words
                                desc_words = potential_desc.lower().split()
                                if any(word in desc_words for word in ['decentralized', 'platform', 'app', 'application', 'system', 'tool', 'verification', 'generating', 'blockchain', 'network', 'bounty']):
                                    score += 1
                                
                                # Penalize very short names unless they're obviously complete
                                if len(potential_name.split()) == 1 and potential_name.lower() not in ['questfi', 'auditor', 'platform']:
                                    score -= 1
                                
                                # Prefer 2-word names for compound projects, but also accept single distinctive names
                                if len(potential_name.split()) == 2:
                                    score += 1
                                elif len(potential_name.split()) == 1 and potential_name.lower() in ['questfi']:
                                    score += 2  # Single names that are clearly project names
                                
                                if score > best_score and len(potential_name) >= 3 and len(potential_name) <= 30:
                                    best_score = score
                                    best_split = (potential_name, potential_desc)
                            
                            if (best_split and 
                                best_split[0][0].isupper() and
                                any(keyword in best_split[1].lower() for keyword in ['platform', 'app', 'website', 'system', 'tool', 'network', 'blockchain', 'data', 'bounty', 'verification', 'auditor', 'sharing', 'monetization'])):
                                
                                # Check if we already have this project
                                existing_names = [p['name'].lower() for p in projects]
                                if best_split[0].lower() not in existing_names:
                                    projects.append({
                                        "name": best_split[0],
                                        "description": best_split[1]
                                    })
                                    print(f"✅ Added PDF-style project: '{best_split[0]}' — '{best_split[1]}'")
                                    # Don't break here - continue to find more projects
            break  # Only process the first matching pattern to avoid duplicates
    
    # If still no projects found, try to extract from the entire text using common project patterns
    if not projects:
        print("No projects found, trying full text extraction...")
        projects = extract_projects_from_full_text(text)
    
    # If STILL no projects found, try PDF-specific patterns (space-separated instead of dash-separated)
    if not projects:
        print("Trying PDF-specific space-separated patterns...")
        # Look for projects in format: "ProjectName Description with keywords Link"
        # Common in PDF extraction where dashes are lost
        project_lines = []
        lines = text.split('\n')
        in_projects_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering projects section
            if re.match(r'^\s*PROJECTS?\s*$', line, re.IGNORECASE):
                in_projects_section = True
                continue
                
            # Check if we're leaving projects section
            if in_projects_section and re.match(r'^\s*(?:ACHIEVEMENTS?|EXPERIENCE|EDUCATION|SKILLS|INTERNSHIP|SOCIAL\s+HANDLES?|LANGUAGES?)\s*', line, re.IGNORECASE):
                break
                
            # If we're in projects section, collect lines that might be projects
            if in_projects_section and line:
                # Look for lines that contain project-like keywords
                if any(keyword in line.lower() for keyword in ['platform', 'app', 'website', 'system', 'tool', 'network', 'blockchain', 'data', 'bounty', 'verification', 'auditor', 'sharing', 'monetization']):
                    project_lines.append(line)
        
        print(f"Found {len(project_lines)} potential PDF project lines")
        
        # Try to parse each project line
        for line in project_lines:
            # Remove [Link] annotations
            clean_line = re.sub(r'\[.*?\]', '', line).strip()
            
            # Try to split into name and description
            # Pattern: "ProjectName rest of description with keywords"
            words = clean_line.split()
            if len(words) >= 3:
                # Try different split points to find the project name
                for split_point in range(1, min(4, len(words))):
                    potential_name = ' '.join(words[:split_point])
                    potential_desc = ' '.join(words[split_point:])
                    
                    # Check if this split makes sense
                    if (len(potential_name) >= 3 and len(potential_name) <= 30 and
                        potential_name[0].isupper() and
                        any(keyword in potential_desc.lower() for keyword in ['platform', 'app', 'website', 'system', 'tool', 'network', 'blockchain', 'data', 'bounty', 'verification', 'auditor', 'sharing', 'monetization']) and
                        not any(keyword in potential_name.lower() for keyword in ['prize', 'award', 'hackathon', 'competition', 'twitter', 'gmail', 'linkedin', 'github', 'intern', 'experience'])):
                        
                        # Check if we already have this project
                        existing_names = [p['name'].lower() for p in projects]
                        if potential_name.lower() not in existing_names:
                            projects.append({
                                "name": potential_name,
                                "description": potential_desc
                            })
                            print(f"✅ Added PDF project: '{potential_name}' — '{potential_desc}'")
                            break

    # Clean up and deduplicate projects
    cleaned_projects = []
    seen_names = set()
    
    for project in projects:
        name = project["name"].strip()
        # Clean up common prefixes/suffixes
        name = re.sub(r'^[-•\s]+', '', name)  # Remove bullet points
        name = re.sub(r'[:\s]+$', '', name)   # Remove trailing colons/spaces
        name = re.sub(r'\[.*?\]', '', name).strip()  # Remove [Link] annotations
        
        if name and name.lower() not in seen_names and len(name) > 3:
            cleaned_projects.append({
                "name": name,
                "description": project.get("description", "")
            })
            seen_names.add(name.lower())
    
    print(f"=== PROJECT EXTRACTION COMPLETE ===")
    print(f"Found {len(cleaned_projects)} projects: {[p['name'] for p in cleaned_projects]}")
    
    return cleaned_projects

def parse_project_section(project_text: str) -> List[Dict[str, Any]]:
    """Parse projects from a dedicated project section"""
    projects = []
    lines = project_text.split('\n')
    current_project = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip common indicators that aren't project names
        if line.lower() in ['remote', 'on-site', 'hybrid', 'freelance', 'contract', 'full-time', 'part-time']:
            continue
        
        # Pattern 0: "Project Name — Description [Link]" (em-dash format like your projects)
        em_dash_match = re.match(r'^([^—\n]+?)\s*—\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*$', line)
        if em_dash_match:
            project_name = em_dash_match.group(1).strip()
            project_desc = em_dash_match.group(2).strip()
            
            # Clean project name by removing any remaining link annotations
            project_name = re.sub(r'\[.*?\]', '', project_name).strip()
            
            # Validate this looks like a project name
            if (len(project_name) >= 3 and len(project_name) <= 60 and 
                project_name[0].isupper() and
                # Exclude section headers and achievement-related terms
                not any(keyword in project_name.lower() for keyword in ['achievements', 'achievement', 'extra', 'extracurricular', 'activities', 'awards', 'honors', 'experience', 'education', 'skills', 'certifications'])):
                
                # Save previous project
                if current_project:
                    projects.append(current_project)
                
                current_project = {
                    "name": project_name,
                    "description": project_desc
                }
                print(f"Found em-dash project: '{project_name}' — '{project_desc}'")
                continue
        
        # Pattern 1: "Project Name:" or "Project Name -" (clear project headers)
        header_match = re.match(r'^([^:•\-*\n]+?)[:\-]\s*(.*?)$', line)
        if header_match:
            project_name = header_match.group(1).strip()
            project_desc = header_match.group(2).strip()
            
            # Clean project name by removing [Link] annotations
            project_name = re.sub(r'\[.*?\]', '', project_name).strip()
            
            # Validate this looks like a project name (not a description or section header)
            if (len(project_name) >= 3 and len(project_name) <= 60 and 
                not any(project_name.lower().startswith(verb) for verb in ['developed', 'created', 'built', 'implemented', 'designed', 'used', 'worked']) and
                project_name[0].isupper() and
                # Exclude section headers and achievement-related terms
                not any(keyword in project_name.lower() for keyword in ['achievements', 'achievement', 'extra', 'extracurricular', 'activities', 'awards', 'honors', 'experience', 'education', 'skills', 'certifications']) and
                # Exclude dated experiences (month/year patterns)
                not re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', project_name.lower())):
                
                # Save previous project
                if current_project:
                    projects.append(current_project)
                
                current_project = {
                    "name": project_name,
                    "description": project_desc
                }
                print(f"Found project header: '{project_name}'")
                continue
        
        # Pattern 2: Bullet points or numbered items that look like project names
        bullet_match = re.match(r'^(?:\d+\.|\•|\*|\-)\s*([^:•\-*\n]+?)(?:[:\-]\s*(.*?))?$', line)
        if bullet_match:
            potential_name = bullet_match.group(1).strip()
            potential_desc = bullet_match.group(2).strip() if bullet_match.group(2) else ""
            
            # Clean potential name by removing [Link] annotations
            potential_name = re.sub(r'\[.*?\]', '', potential_name).strip()
            
            # Check if this looks like a project name (not a description or achievement)
            if (len(potential_name) <= 60 and 
                not any(potential_name.lower().startswith(verb) for verb in ['developed', 'created', 'built', 'implemented', 'designed', 'used', 'worked', 'integrated', 'deployed', 'received', 'awarded', 'achieved', 'won', 'earned', 'certified', 'completed', 'graduated', 'participated', 'attended', 'volunteered']) and
                potential_name[0].isupper() and
                # Additional check: contains project-type keywords OR doesn't contain achievement keywords
                (any(keyword in potential_name.lower() for keyword in ['app', 'website', 'system', 'platform', 'tool', 'dashboard', 'api', 'service', 'portal', 'application', 'project', 'software', 'game', 'simulator']) and
                 not any(keyword in potential_name.lower() for keyword in ['award', 'achievement', 'certificate', 'certification', 'degree', 'scholarship', 'honor', 'recognition', 'winner', 'prize', 'distinction', 'gpa', 'cgpa', 'grade', 'score', 'rank', 'experience', 'extra', 'extracurricular', 'activities']) and
                 # Exclude dated experiences
                 not re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', potential_name.lower()))):
                
                # Save previous project
                if current_project:
                    projects.append(current_project)
                
                current_project = {
                    "name": potential_name,
                    "description": potential_desc
                }
                print(f"Found bulleted project: '{potential_name}'")
                continue
        
        # Pattern 3: Standalone project names (lines that don't start with bullets but look like titles)
        # Clean line by removing [Link] annotations first
        clean_line = re.sub(r'\[.*?\]', '', line).strip()
        
        if (len(clean_line) <= 60 and clean_line and clean_line[0].isupper() and 
            not any(clean_line.lower().startswith(verb) for verb in ['developed', 'created', 'built', 'implemented', 'designed', 'used', 'worked', 'integrated', 'deployed', 'received', 'awarded', 'achieved', 'won', 'earned', 'certified', 'graduated', 'completed', 'participated', 'volunteered', 'organized', 'led', 'managed', 'coordinated']) and
            (any(keyword in clean_line.lower() for keyword in ['app', 'website', 'system', 'platform', 'tool', 'dashboard', 'api', 'service', 'portal', 'application', 'project', 'software', 'game', 'simulator']) or
             # Allow names that don't contain action words and are reasonable length, but exclude extracurricular terms
             (len(clean_line.split()) <= 5 and not any(word in clean_line.lower() for word in ['award', 'achievement', 'certificate', 'certification', 'degree', 'scholarship', 'honor', 'recognition', 'winner', 'prize', 'distinction', 'club', 'society', 'team', 'captain', 'president', 'member', 'volunteer', 'community', 'event', 'competition', 'contest', 'tournament', 'league', 'association', 'achievements', 'extra', 'extracurricular', 'activities', 'experience', 'education', 'skills']))) and
            # Exclude dated experiences and section headers
            not re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', clean_line.lower()) and
            # Exclude obvious section headers
            not any(clean_line.lower().strip() == header for header in ['achievements', 'achievements & extra', 'extracurricular', 'activities', 'experience', 'education', 'skills', 'awards', 'honors'])):
            
            # Save previous project
            if current_project:
                projects.append(current_project)
            
            current_project = {
                "name": clean_line,
                "description": ""
            }
            print(f"Found standalone project: '{clean_line}'")
            continue
        
        # Pattern 4: Description lines (add to current project)
        if current_project:
            # This line is a description for the current project
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                desc_text = line[1:].strip()
            else:
                desc_text = line
            
            if current_project["description"]:
                current_project["description"] += " " + desc_text
            else:
                current_project["description"] = desc_text
    
    # Don't forget the last project
    if current_project:
        projects.append(current_project)
    
    return projects

def extract_projects_from_full_text(text: str) -> List[Dict[str, Any]]:
    """Extract projects when no dedicated project section is found - very conservative approach"""
    projects = []
    
    # Only look for very explicit project patterns - avoid false positives from achievements/awards
    project_patterns = [
        # Pattern 0: "Project Name — Description [Link]" (em-dash format)
        r'(?m)^([A-Z][A-Za-z0-9\s,-]{2,50})\s*—\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*$',
        # Pattern 1: "Project Name (Technology Stack)" - very reliable
        r'(?i)^([A-Z][A-Za-z0-9\s,-]{2,50})\s*\([^)]+(?:react|node|python|javascript|java|angular|vue|django|flask|spring|express|mongodb|sql|aws|docker|kubernetes|api|framework|library|technology|tech|stack)[^)]*\)(?:\s|$)',
        # Pattern 2: Lines explicitly mentioning "project" with name
        r'(?i)(?:^|\n)([A-Z][A-Za-z0-9\s,-]{2,60}?)\s*(?:project|app|application)(?:\s|$|\.)',
        # Pattern 3: "Developed/Created/Built [ProjectName] project/app/application"
        r'(?i)(?:developed|created|built|implemented|designed)\s+(?:a\s+|an\s+|the\s+)?([A-Z][A-Za-z0-9\s(),-]{2,50}?)\s+(?:project|application|app|website|system|platform)(?:\s|\.|\,)',
    ]
    
    # Be extra strict about what sections we search in
    lines = text.split('\n')
    in_projects_section = False
    current_section = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if we're entering a section
        section_headers = ['skills', 'experience', 'education', 'work experience', 'employment', 'achievements', 'awards', 'certifications', 'references', 'contact', 'summary', 'objective', 'languages', 'interests', 'hobbies', 'activities', 'volunteer', 'extracurricular', 'leadership', 'organizations']
        
        # Check if this line is a section header
        line_lower = line.lower().strip(':')
        if line_lower in section_headers:
            in_projects_section = False
            current_section = line_lower
            continue
        elif line_lower.startswith('project'):
            in_projects_section = True
            current_section = "projects"
            continue
        
        # Only extract from lines that are clearly not in other sections
        if not in_projects_section and current_section in section_headers:
            continue
            
        # Skip personal info lines
        if '@' in line or re.match(r'.*\(\d{3}\).*\d{4}', line):  # Email or phone
            continue
        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', line.strip()):  # Likely a person's name
            continue
            
        # Apply patterns only if we're not clearly in another section
        for pattern in project_patterns:
            if pattern.startswith(r'(?m)^([A-Z][A-Za-z0-9\s,-]{2,50})\s*—'):
                # Special handling for em-dash pattern
                match = re.match(r'^([A-Z][A-Za-z0-9\s,-]{2,50})\s*—\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*$', line)
                if match:
                    project_name = match.group(1).strip()
                    project_desc = match.group(2).strip()
                    
                    # Clean project name by removing [Link] annotations
                    project_name = re.sub(r'\[.*?\]', '', project_name).strip()
                    
                    # Very strict validation
                    if (len(project_name) >= 3 and len(project_name) <= 80 and
                        project_name[0].isupper() and
                        # Exclude achievement/section terms and dated experiences
                        not any(keyword in project_name.lower() for keyword in ['achievements', 'extra', 'extracurricular', 'activities', 'experience', 'education', 'skills', 'awards', 'honors']) and
                        not re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', project_name.lower())):
                        
                        # Check if we already have this project (avoid duplicates)
                        existing_names = [p['name'].lower() for p in projects]
                        if project_name.lower() not in existing_names:
                            projects.append({
                                "name": project_name,
                                "description": project_desc
                            })
                            print(f"Found em-dash project: '{project_name}' — '{project_desc}'")
            else:
                matches = re.findall(pattern, line)
                for match in matches:
                    project_name = match.strip()
                    
                    # Clean project name by removing [Link] annotations
                    project_name = re.sub(r'\[.*?\]', '', project_name).strip()
                    
                    # Very strict validation
                    if (len(project_name) >= 3 and len(project_name) <= 80 and
                        not any(project_name.lower().startswith(word) for word in ['developed', 'created', 'built', 'implemented', 'designed', 'used', 'worked', 'responsible', 'received', 'awarded', 'achieved', 'won', 'earned', 'certified', 'the ', 'a ', 'an ']) and
                        project_name[0].isupper() and
                        # Exclude achievement/section terms and dated experiences
                        not any(keyword in project_name.lower() for keyword in ['achievements', 'extra', 'extracurricular', 'activities', 'experience', 'education', 'skills', 'awards', 'honors']) and
                        not re.search(r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b', project_name.lower())):
                        
                        # Check if we already have this project (avoid duplicates)
                        existing_names = [p['name'].lower() for p in projects]
                        if project_name.lower() not in existing_names:
                            projects.append({
                                "name": project_name,
                                "description": ""
                            })
                            print(f"Found project from conservative pattern: '{project_name}'")
    
    return projects

def extract_additional_skills_from_achievements(text: str) -> List[str]:
    """Extract leadership, teamwork, and other soft skills from achievements and extracurricular sections"""
    additional_skills = []
    
    # Look for achievement and extracurricular sections
    achievement_patterns = [
        r'(?i)(?:achievements?|awards?|honors?|recognition)\s*[:\n]\s*(.*?)(?=\n\s*(?:SKILLS?|EXPERIENCE|EDUCATION|PROJECTS?|WORK\s+EXPERIENCE|EMPLOYMENT|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?)\s*[:\n]|$)',
        r'(?i)(?:extracurricular|activities|volunteer|leadership|organizations?)\s*[:\n]\s*(.*?)(?=\n\s*(?:SKILLS?|EXPERIENCE|EDUCATION|PROJECTS?|WORK\s+EXPERIENCE|EMPLOYMENT|ACHIEVEMENTS?|AWARDS?|CERTIFICATIONS?|REFERENCES?|CONTACT|SUMMARY|OBJECTIVE|LANGUAGES?|INTERESTS?|HOBBIES?)\s*[:\n]|$)'
    ]
    
    for pattern in achievement_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            section_text = match.strip().lower()
            
            # Extract soft skills from achievements/activities
            skill_indicators = {
                'leadership': ['president', 'captain', 'leader', 'head', 'coordinator', 'organizer', 'manager'],
                'teamwork': ['team', 'group', 'collaboration', 'cooperative', 'member'],
                'communication': ['presentation', 'speaking', 'debate', 'public speaking', 'communication'],
                'project management': ['organized', 'planned', 'coordinated', 'managed', 'executed'],
                'problem solving': ['solved', 'resolved', 'troubleshooting', 'analysis', 'strategy'],
                'time management': ['deadline', 'schedule', 'multitasking', 'prioritize'],
                'creativity': ['creative', 'innovative', 'design', 'artistic', 'original'],
                'analytical thinking': ['analysis', 'research', 'data', 'statistical', 'analytical'],
                'adaptability': ['adapted', 'flexible', 'versatile', 'diverse'],
                'mentoring': ['mentor', 'tutor', 'teach', 'guide', 'coach']
            }
            
            for skill, indicators in skill_indicators.items():
                if any(indicator in section_text for indicator in indicators):
                    if skill not in additional_skills:
                        additional_skills.append(skill.title())
    
    return additional_skills
```

---

## 4. Code That Categorizes Skills as Verified vs. Unverified
**File:** `backend/app/api/endpoints/verification.py` (Lines 230–261)

```python
        # Combine all verification results
        verification_result = {
            "resume_id": resume_id,
            "status": "completed",
            "github": github_results,
            "twitter": twitter_results,
            "linkedin": linkedin_results,
            "verified_skills": [],
            "verified_projects": [],
            "unverified_skills": [],
            "unverified_projects": []
        }
        
        # Categorize verified and unverified skills/projects
        for skill in skills:
            # Debug logging
            print(f"Checking skill: {skill}")
            print(f"GitHub verified skills: {github_results.get('verified_skills', [])}")
            print(f"Twitter verified skills: {twitter_results.get('verified_skills', [])}")
            print(f"LinkedIn verified skills: {linkedin_results.get('verified_skills', [])}")
            
            if (
                skill in github_results.get("verified_skills", []) or
                skill in twitter_results.get("verified_skills", []) or
                skill in linkedin_results.get("verified_skills", [])
            ):
                verification_result["verified_skills"].append(skill)
                print(f"Skill '{skill}' was verified")
            else:
                verification_result["unverified_skills"].append(skill)
                print(f"Skill '{skill}' was NOT verified")
```

**File:** `backend/app/services/scoring_service.py` (Lines 358–371)

```python
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
```

---

## 5. GitHub Verification Service
**File:** `backend/app/services/github_service.py` (Full File)

```python
import requests
import os
from typing import List, Dict, Any
import re

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Development mode - use mock data only (set environment variable MOCK_MODE=true)
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

def verify_github_claims(github_username: str, skills: List[str], projects: List[Any]) -> Dict[str, Any]:
    """Verify resume claims against GitHub data"""
    print(f"=== GITHUB VERIFICATION START ===")
    print(f"Username: {github_username}")
    print(f"Skills to verify: {skills}")
    print(f"Projects to verify: {projects}")
    
    result = {
        "verified_skills": [],
        "verified_projects": [],
        "repositories": [],
        "languages": [],
        "contributions": 0,
        "proof": {}
    }
    
    try:
        # Get user repositories
        print(f"Fetching repositories for user: {github_username}")
        repos = get_user_repositories(github_username)
        print(f"Found {len(repos)} repositories")
        result["repositories"] = [repo["name"] for repo in repos]
        
        # Get user languages
        print(f"Extracting languages from repositories")
        languages = get_user_languages(repos)
        print(f"Found languages: {list(languages.keys())}")
        result["languages"] = list(languages.keys())
        
        # Get user contributions
        print(f"Getting contributions for user: {github_username}")
        contributions = get_user_contributions(github_username)
        print(f"Contributions: {contributions}")
        result["contributions"] = contributions
        
        # Verify skills
        print(f"Verifying skills against GitHub data")
        verified_skills, skill_proof = verify_skills(skills, repos, languages)
        print(f"Verified skills: {verified_skills}")
        result["verified_skills"] = verified_skills
        result["proof"]["skills"] = skill_proof
        
        # Verify projects
        print(f"Verifying projects against GitHub data")
        verified_projects, project_proof = verify_projects(projects, repos)
        print(f"Verified projects: {verified_projects}")
        result["verified_projects"] = verified_projects
        result["proof"]["projects"] = project_proof
        
        print(f"=== GITHUB VERIFICATION COMPLETE ===")
        print(f"Final result: {result}")
        return result
    
    except Exception as e:
        print(f"=== GITHUB VERIFICATION ERROR ===")
        print(f"Error: {str(e)}")
        # Return empty result with error
        return {
            "verified_skills": [],
            "verified_projects": [],
            "repositories": [],
            "languages": [],
            "contributions": 0,
            "proof": {},
            "error": str(e)
        }

def get_user_repositories(username: str) -> List[Dict[str, Any]]:
    """Get user repositories from GitHub API or mock data"""
    print(f"Getting repositories for user: {username}")
    
    # If mock mode is enabled, return mock data immediately
    if MOCK_MODE:
        print("MOCK_MODE enabled, returning mock data")
        return get_mock_repositories(username)
    
    # If no username provided, return mock data
    if not username:
        print("No username provided, returning mock data")
        return get_mock_repositories(username)
    
    # Prepare headers
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        print("Using GitHub token for authentication")
    else:
        print("No GitHub token provided, making unauthenticated request")
    
    # Fetch ALL repositories by paginating through all pages
    all_repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{GITHUB_API_URL}/users/{username}/repos?per_page={per_page}&page={page}"
        print(f"Making request to: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            print(f"GitHub API response status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"User {username} not found on GitHub, using mock data")
                return get_mock_repositories(username)
            elif response.status_code == 403:
                print(f"GitHub API rate limit exceeded or forbidden")
                return get_mock_repositories(username) if page == 1 else all_repos
            elif response.status_code != 200:
                print(f"GitHub API error: {response.status_code} - {response.text}")
                return get_mock_repositories(username) if page == 1 else all_repos
            
            repos = response.json()
            
            # If no repositories returned, we've reached the end
            if not repos:
                break
                
            all_repos.extend(repos)
            print(f"Fetched {len(repos)} repositories from page {page}, total: {len(all_repos)}")
            
            # If we got fewer than per_page, we're done
            if len(repos) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Network error when fetching repositories: {str(e)}")
            return get_mock_repositories(username) if page == 1 else all_repos
    
    print(f"Successfully fetched {len(all_repos)} total repositories")
    return all_repos

def get_user_languages(repos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get user languages from repositories"""
    languages = {}
    
    for repo in repos:
        repo_languages = repo.get("language")
        if repo_languages:
            if repo_languages in languages:
                languages[repo_languages] += 1
            else:
                languages[repo_languages] = 1
    
    return languages

def get_user_contributions(username: str) -> int:
    """Get user contributions count"""
    # Note: GitHub doesn't provide an API for contributions
    # This would require scraping the contributions graph
    # For demo purposes, return a random number or mock data
    return 500  # Mock data

def verify_skills(skills: List[str], repos: List[Dict[str, Any]], languages: Dict[str, int]) -> tuple:
    """Verify skills against GitHub data"""
    verified_skills = []
    proof = {}
    
    # Check if GitHub activity is decent (for auto-verification)
    total_repos = len(repos)
    total_languages = len(languages)
    decent_activity = total_repos >= 3 or total_languages >= 2
    
    print(f"GitHub activity assessment: {total_repos} repos, {total_languages} languages, decent_activity={decent_activity}")
    
    # Auto-verify GitHub and problem-solving skills if activity is decent
    if decent_activity:
        github_skills = ["github", "git", "version control", "source control", "code management"]
        problem_solving_skills = ["problem solving", "problem-solving", "analytical thinking", "debugging", "troubleshooting"]
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if this is a GitHub-related skill
            if any(github_term in skill_lower for github_term in github_skills):
                if skill not in verified_skills:
                    verified_skills.append(skill)
                    proof[skill] = [f"Demonstrated through {total_repos} GitHub repositories and {total_languages} programming languages"]
                    print(f"Auto-verified GitHub skill: '{skill}' due to decent GitHub activity")
            
            # Check if this is a problem-solving skill
            elif any(ps_term in skill_lower for ps_term in problem_solving_skills):
                if skill not in verified_skills:
                    verified_skills.append(skill)
                    proof[skill] = [f"Demonstrated through active GitHub development with {total_repos} repositories"]
                    print(f"Auto-verified problem-solving skill: '{skill}' due to GitHub activity")
    
    # Define skill synonyms and related terms for better matching
    skill_synonyms = {
        "python": ["python", "django", "fastapi", "pandas", "numpy", "jupyter", "py"],
        "javascript": ["javascript", "js", "node", "react", "vue", "angular", "typescript", "ts", "nodejs"],
        "leadership": ["leadership", "lead", "team lead", "project management", "managed", "coordinated", "manager"],
        "community management": ["community", "engagement", "moderation", "forum", "social media", "discord", "reddit"],
        "machine learning": ["ml", "ai", "artificial intelligence", "neural network", "deep learning", "tensorflow", "pytorch"],
        "nlp": ["natural language processing", "text analysis", "language model", "tokenization", "spacy"],
        "teamwork": ["team", "collaboration", "collaborative", "group project", "worked together"],
        "blockchain": ["blockchain", "crypto", "cryptocurrency", "bitcoin", "ethereum", "solidity", "web3", "defi", "smart contracts"],
        "data analysis": ["data", "analytics", "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "analysis"],
        "data sharing": ["data", "sharing", "api", "rest", "graphql", "database", "mongodb", "sql"],
        "monetization": ["monetization", "payment", "paypal", "stripe", "revenue", "subscription", "billing"],
        "decentralized": ["decentralized", "distributed", "p2p", "peer-to-peer", "blockchain", "web3"],
        "platform": ["platform", "service", "application", "system", "framework"]
    }
    
    # Check languages and repositories for other skills
    for skill in skills:
        # Skip if already verified
        if skill in verified_skills:
            continue
            
        # Convert skill to lowercase for case-insensitive comparison
        skill_lower = skill.lower()
        matching_repos = []
        commit_evidence = []
        language_evidence = []
        
        # Get related terms for this skill
        related_terms = []
        for key, terms in skill_synonyms.items():
            if skill_lower in terms or any(term in skill_lower for term in terms):
                related_terms.extend(terms)
        
        # If no related terms found, just use the skill itself
        if not related_terms:
            related_terms = [skill_lower]
        
        # Check if skill is in languages
        print(f"GitHub checking skill: '{skill}' against languages: {list(languages.keys())}")
        for language in languages.keys():
            if skill_lower == language.lower() or skill_lower in language.lower() or any(term in language.lower() for term in related_terms):
                verified_skills.append(skill)
                proof[skill] = [f"Used {language} in {languages[language]} repositories"]
                print(f"GitHub verified skill: '{skill}' matched with language '{language}'")
                break
        
        # If not found in languages, check repository descriptions, names, and commit history
        if skill not in verified_skills:
            print(f"GitHub checking skill: '{skill}' in repository names, descriptions, and commit history")
            for repo in repos:
                repo_name = repo.get("name", "").lower()
                repo_desc = repo.get("description", "").lower() if repo.get("description") else ""
                
                # Check repository name
                if skill_lower in repo_name or any(term in repo_name for term in related_terms):
                    matching_repos.append(repo["name"])
                    print(f"GitHub found skill '{skill}' in repository name: '{repo['name']}'")
                # Check repository description
                elif skill_lower in repo_desc or any(term in repo_desc for term in related_terms):
                    matching_repos.append(repo["name"])
                    print(f"GitHub found skill '{skill}' in repository description for: '{repo['name']}'")
                
                # Check in commit history
                if "commit_history" in repo:
                    for commit in repo.get("commit_history", []):
                        commit_lower = commit.lower()
                        if skill_lower in commit_lower or any(term in commit_lower for term in related_terms):
                            matching_repos.append(repo["name"]) if repo["name"] not in matching_repos else None
                            commit_evidence.append(commit)
                            print(f"GitHub found skill '{skill}' in commit: '{commit}' for repo: '{repo['name']}'")
            
            if matching_repos:
                verified_skills.append(skill)
                proof_items = [f"Found in repositories: {', '.join(set(matching_repos[:3]))}"]  
                
                if commit_evidence:
                    proof_items.append(f"Commit evidence: {', '.join(commit_evidence[:2])}")
                    
                proof[skill] = proof_items
                print(f"GitHub verified skill: '{skill}' found in repositories: {list(set(matching_repos[:3]))}")
            else:
                print(f"GitHub could not verify skill: '{skill}' in any repositories")
    
    return verified_skills, proof

def verify_projects(projects: List[Any], repos: List[Dict[str, Any]]) -> tuple:
    """Verify projects against GitHub repositories by matching project names to repo names"""
    verified_projects = []
    proof = {}
    
    print(f"=== PROJECT VERIFICATION START ===")
    print(f"Projects to verify: {projects}")
    print(f"Available repositories: {[repo.get('name', '') for repo in repos]}")

    def normalize_name(name: str) -> str:
        """Normalize a name for comparison: lowercase, remove spaces, dashes, underscores, special chars"""
        if not name:
            return ""
        normalized = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        return normalized

    def get_name_variants(name: str) -> List[str]:
        """Get different variants of a name for matching"""
        if not name:
            return []
        
        name = name.strip()
        base_normalized = normalize_name(name)
        
        variants = [
            name.lower(),                    # Original case
            base_normalized,                 # Normalized with hyphens
            base_normalized.replace('-', ''), # No separators
            base_normalized.replace('-', '_'), # Underscore separated
            base_normalized.replace('-', ' '), # Space separated
        ]
        
        # Add common GitHub naming patterns
        if ' ' in name:
            # "My Project" -> "my-project", "myproject", "my_project"
            space_to_hyphen = name.lower().replace(' ', '-')
            space_to_underscore = name.lower().replace(' ', '_')
            space_removed = name.lower().replace(' ', '')
            variants.extend([space_to_hyphen, space_to_underscore, space_removed])
        
        # For long descriptive names, extract key terms
        if len(name) > 50:  # Long descriptive names
            # Extract key technical terms
            key_terms = []
            important_words = ['decentralized', 'decentralised', 'blockchain', 'data', 'sharing', 'monetization', 'monetisation', 
                             'platform', 'system', 'application', 'app', 'website', 'tool', 'api', 'service', 'framework',
                             'library', 'parser', 'analyzer', 'engine', 'manager', 'tracker', 'dashboard', 'portal']
            
            words = name.lower().split()
            for word in words:
                # Remove common articles and prepositions
                if word not in ['a', 'an', 'the', 'and', 'or', 'for', 'with', 'based', 'using', 'on', 'in', 'of', 'to']:
                    if word in important_words or len(word) > 4:  # Technical terms or longer words
                        key_terms.append(word)
            
            # Create combinations of key terms
            if len(key_terms) >= 2:
                # Two word combinations
                for i in range(len(key_terms)-1):
                    two_word = f"{key_terms[i]}-{key_terms[i+1]}"
                    variants.append(two_word)
                    variants.append(two_word.replace('-', ''))
                    variants.append(two_word.replace('-', '_'))
                
                # Three word combinations for very specific projects
                if len(key_terms) >= 3:
                    three_word = f"{key_terms[0]}-{key_terms[1]}-{key_terms[2]}"
                    variants.append(three_word)
                    variants.append(three_word.replace('-', ''))
        
        # Remove duplicates and empty strings
        return list(set([v for v in variants if v]))

    for project in projects:
        # Extract and clean project name
        if isinstance(project, dict):
            raw_project_name = project.get("name", "").strip()
        else:
            raw_project_name = str(project).strip()
        project_name = raw_project_name
        # Clean the project name for matching
        cleaned_project_name = raw_project_name
        # Use the same cleaning as extraction for matching
        for _ in range(3):
            cleaned_project_name = re.sub(r'(\b\w{3,}?)(or|er|ar|ur|ir)+\b', r'\1', cleaned_project_name, flags=re.IGNORECASE)
        cleaned_project_name = re.sub(r'\b(\w+) \1\b', r'\1', cleaned_project_name)
        cleaned_project_name = re.sub(r'[^a-zA-Z0-9\s\-]', '', cleaned_project_name)
        cleaned_project_name = re.sub(r'\s+', ' ', cleaned_project_name)
        cleaned_project_name = cleaned_project_name.strip().title()
        norm_project = normalize_name(cleaned_project_name)
        if not norm_project:
            continue
        print(f"\n--- Checking project: '{raw_project_name}' (cleaned: '{cleaned_project_name}', normalized: '{norm_project}') ---")
        matching_repos = []
        match_types = []
        for repo in repos:
            repo_name = repo.get("name", "").strip()
            repo_desc = repo.get("description", "") or ""
            if not repo_name:
                continue
            norm_repo = normalize_name(repo_name)
            print(f"DEBUG: Comparing normalized project '{norm_project}' with repo '{norm_repo}'")
            contains_match = norm_project in norm_repo
            if contains_match:
                print(f"    Normalized substring match: '{norm_project}' in '{norm_repo}'")
            desc_match = False
            if not contains_match and repo_desc:
                if norm_project in normalize_name(repo_desc):
                    desc_match = True
                    print(f"    Description match: '{norm_project}' in description")
            if contains_match or desc_match:
                matching_repos.append(repo_name)
                match_type = "contains" if contains_match else "description"
                match_types.append(f"{repo_name} ({match_type})")
                print(f"✅ Match found: '{cleaned_project_name}' -> '{repo_name}' (type: {match_type})")
        if matching_repos:
            verified_projects.append(cleaned_project_name)
            proof[cleaned_project_name] = [
                f"Found matching repositories: {', '.join(matching_repos)}",
                f"Match details: {', '.join(match_types)}"
            ]
            print(f"✅ Project '{cleaned_project_name}' VERIFIED with {len(matching_repos)} matching repos")
        else:
            print(f"❌ Project '{cleaned_project_name}' NOT FOUND in any GitHub repositories")
    
    print(f"\n=== PROJECT VERIFICATION COMPLETE ===")
    print(f"Verified projects: {verified_projects}")
    print(f"Verification proof: {proof}")
    
    return verified_projects, proof

def get_mock_repositories(username: str) -> List[Dict[str, Any]]:
    """Get mock repositories for demo purposes"""
    return [
        {
            "name": "personal-website",
            "description": "My personal portfolio website built with React and Tailwind CSS",
            "language": "JavaScript",
            "languages": ["JavaScript", "HTML", "CSS"],
            "owner": {"login": username},
            "commit_history": ["Added responsive design", "Updated portfolio section", "Fixed navigation bug"]
        },
        {
            "name": "machine-learning-projects",
            "description": "Collection of ML projects using TensorFlow and PyTorch",
            "language": "Python",
            "languages": ["Python", "Jupyter Notebook", "R"],
            "owner": {"login": username},
            "commit_history": ["Implemented neural network", "Added data preprocessing", "Updated model accuracy"]
        },
        {
            "name": "resume-parser",
            "description": "Automated resume parsing tool using NLP and machine learning",
            "language": "Python",
            "languages": ["Python", "JavaScript", "HTML"],
            "owner": {"login": username},
            "commit_history": ["Initial commit", "Added PDF parsing functionality", "Implemented skill extraction", "Added team collaboration features"]
        },
        {
            "name": "e-commerce-api",
            "description": "RESTful API for e-commerce platform built with Node.js and Express",
            "language": "JavaScript",
            "languages": ["JavaScript", "TypeScript", "SQL"],
            "owner": {"login": username},
            "commit_history": ["Added user authentication", "Implemented product search", "Fixed payment gateway"]
        },
        {
            "name": "data-visualization-dashboard",
            "description": "Interactive dashboard for data visualization using D3.js",
            "language": "JavaScript",
            "languages": ["JavaScript", "HTML", "CSS"],
            "owner": {"login": username},
            "commit_history": ["Added bar chart component", "Implemented data filtering", "Fixed responsive layout"]
        },
        {
            "name": "blockchain-voting-system",
            "description": "Secure voting system built on Ethereum blockchain",
            "language": "Solidity",
            "languages": ["Solidity", "JavaScript", "Web3.js"],
            "owner": {"login": username},
            "commit_history": ["Implemented smart contract", "Added vote verification", "Fixed security vulnerability"]
        }
    ]
```

---

## 6. Data Models / Schemas
### File: `backend/app/models/resume.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResumeResponse(BaseModel):
    """Response model for resume upload"""
    resume_id: str
    message: str
    status: str

class ResumeData(BaseModel):
    """Model for parsed resume data"""
    resume_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    github_username: Optional[str] = None
    twitter_username: Optional[str] = None
    linkedin_username: Optional[str] = None
    status: str
```

### File: `backend/app/models/verification.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class VerificationResponse(BaseModel):
    """Response model for verification status"""
    resume_id: str
    status: str
    message: Optional[str] = None

class VerificationResult(BaseModel):
    """Model for verification results"""
    resume_id: str
    status: str
    github: Dict[str, Any] = {}
    twitter: Dict[str, Any] = {}
    linkedin: Dict[str, Any] = {}
    verified_skills: List[str] = []
    unverified_skills: List[str] = []
    verified_projects: List[str] = []
    unverified_projects: List[str] = []
    error: Optional[str] = None
```

### File: `backend/app/models/score.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any

class ScoreBreakdown(BaseModel):
    """Model for score breakdown"""
    github_score: float
    twitter_score: float
    linkedin_score: float
    skills_score: float
    projects_score: float

class ScoreResponse(BaseModel):
    """Response model for reality score"""
    resume_id: str
    score: float
    breakdown: ScoreBreakdown
    verified_skills: List[str] = []
    unverified_skills: List[str] = []
    verified_projects: List[str] = []
    unverified_projects: List[str] = []
```

---

## 7. Sample Resume Text / Test Fixture
**File:** `backend/test_parser.py` (Full File)

```python
"""Test script to debug project extraction for specific formats"""
import sys
import os
import re

# Add the parent directory to the path so we can import the resume parser
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.resume_parser import extract_projects, parse_project_section, extract_skills

def test_em_dash_projects():
    """Test the em-dash project format specifically"""
    test_text = """PROJECTS	
Data Roots ?" Decentralized Data Sharing & Monetization platform[Link].
Questfi ?" Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor ?" Resume verification app generating a Reality Score based on online activity ([Link]."""
    
    print("Testing em-dash project extraction:")
    print("Input text:")
    print(test_text)
    print("\n" + "="*50)
    
    # Test the regex pattern directly
    em_dash_pattern = r'([A-Z][A-Za-z0-9\s,-]{2,50})\s*?"\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*$'
    matches = re.findall(em_dash_pattern, test_text, re.MULTILINE)
    print(f"Direct regex matches: {len(matches)}")
    for i, match in enumerate(matches, 1):
        print(f"  {i}. '{match[0]}' ?" '{match[1]}'")
    
    print("\nFull extraction:")
    projects = extract_projects(None, test_text)
    
    print(f"\nExtracted {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   Description: {project['description']}")
        print()

def test_skills_extraction():
    """Test skills extraction with problematic text"""
    test_text = """SKILLS	
Programming: Python, React, C, JavaScript, Solidity, C++, TypeScript, HTML, CSS
Tools: GitHub, Canva, VS Code, Notion, Figma
Soft Skills: Public Speaking, Leadership, Community Management

LANGUAGES	English, Hindi

Social Handles
Github - https://github.com/vishvjeettanwar1623
Twitter - https://x.com/vishvjeet1623
LinkedIn - https://www.linkedin.com/in/vishvjeet-tanwar/
Gmail - vishvjeettanwar.1623@gmail.com"""
    
    print("Testing skills extraction:")
    print("Input text:")
    print(test_text)
    print("\n" + "="*50)
    
    skills = extract_skills(None, test_text)
    
    print(f"\nExtracted {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill}")

def test_full_resume():
    """Test with your full resume text"""
    full_resume = """Vishvjeet Singh Tanwar
(+91)8708213008 | Email | LinkedIn | Github | Portfolio
EDUCATION	
JSS University, Noida	Noida, India
B.tech in Computer Science Engineering (AI & ML)	2024-2028
Vidyantriksh Senior Secondary School	Bhiwani, India
Passed  XIIth (PCM)	2015- 2023
EXPERIENCE	
OffScript                                                                                                                                                             Remote March 2025- Present	                               
Building and managing a 200+ member community at OffScript, organizing meetups, workshops, and online sessions to foster learning and collaboration.
HackQuest                                                                                                                                                               Remote Nov 2024- Present
Advocate for HackQuest, promoting Web3 and AI adoption through talks, content, and collaborations on community projects and hackathons.	                   
INTERNSHIP	
Blender Intern(GauravGo Games)                                                                                                                            Remote June-July 2025
Completed a 21-day internship at GauravGo Games as a Blender Intern, creating and optimizing 3D assets including furniture, props, and environment models.
Virtual Intern(Deloitte)                                                                                                                                                                          Remote 
Completed training modules in Technology, Data Analytics, and Cybersecurity fundamentals.
PROJECTS	
Data Roots ?" Decentralized Data Sharing & Monetization platform[Link].
Questfi ?" Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor ?" Resume verification app generating a Reality Score based on online activity ([Link].

ACHIEVEMENTS & EXTRA-CURRICULARS	
EDUCHAIN Delhi Regional Hackathon	MSIT, Delhi
3rd Prize (100$)	17-18 March, 2025
Built a blockchain-based decentralized platform for secure data management, sharing, monetization and ownership.
ACPC Algohour 3.0	MSIT, Delhi
30th Position 	17-18 March, 2025
Engaged in a national competition, demonstrating problem-solving and algorithmic thinking by tackling easy, medium, and hard problems under timed conditions.

SKILLS	
Programming: Python, React, C, JavaScript, Solidity, C++, TypeScript, HTML, CSS
Tools: GitHub, Canva, VS Code, Notion, Figma
Soft Skills: Public Speaking, Leadership, Community Management

LANGUAGES	English, Hindi

Social Handles
Github - https://github.com/vishvjeettanwar1623
Twitter - https://x.com/vishvjeet1623
LinkedIn - https://www.linkedin.com/in/vishvjeet-tanwar/
Gmail - vishvjeettanwar.1623@gmail.com"""
    
    print("Testing full resume:")
    print(f"Resume length: {len(full_resume)} characters")
    print("\n" + "="*50)
    
    print("=== PROJECTS ===")
    projects = extract_projects(None, full_resume)
    print(f"Found {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   Description: {project['description']}")
    
    print("\n=== SKILLS ===")
    skills = extract_skills(None, full_resume)
    print(f"Found {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill}")

if __name__ == "__main__":
    test_em_dash_projects()
    print("\n" + "="*80 + "\n")
    test_skills_extraction()
    print("\n" + "="*80 + "\n")
    test_full_resume()
```

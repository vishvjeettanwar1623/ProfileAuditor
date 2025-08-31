from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
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
    background_tasks: BackgroundTasks,
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
        
        # Parse resume in background
        background_tasks.add_task(
            process_resume, 
            resume_id=resume_id,
            file_path=file_location,
            name=name,
            email=email
        )
        print(f"Background task added to process resume {resume_id}")
        
        return ResumeResponse(
            resume_id=resume_id,
            message="Resume uploaded successfully and is being processed",
            status="processing"
        )
    
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
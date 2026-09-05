from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import uuid
import os
import re
from typing import Optional

from app.services.resume_parser import parse_resume, parse_resume_with_text, extract_text_from_file
from app.services.docx_service import convert_document_to_rich_doc, generate_docx_from_document
from app.models.resume import ResumeResponse, ResumeData

router = APIRouter()

# In-memory storage for demo purposes (would use a database in production)
resume_storage = {}

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """Upload and parse a resume file (PDF or DOC)"""
    print(f"\n\n===== RESUME UPLOAD =====\nFilename: {file.filename}")
    if job_description:
        print(f"Target Job Description provided ({len(job_description)} chars)")
    
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
                email=email,
                job_description=job_description
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


@router.post("/extract-text")
async def extract_resume_text(file: UploadFile = File(...)):
    """Extract raw text from an uploaded PDF or Word (DOCX) document for the Live Editor"""
    filename_lower = (file.filename or "").lower()
    if not filename_lower.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX format")
    
    temp_dir = "/tmp" if os.environ.get("VERCEL") else os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"extract_{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(temp_dir, temp_filename)
    
    try:
        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
            
        raw_text = extract_text_from_file(file_location) or ""
        
        if os.path.exists(file_location):
            os.remove(file_location)
            
        words = len((raw_text or "").split())
        return {
            "filename": file.filename,
            "raw_text": raw_text or "",
            "word_count": words,
            "status": "success"
        }
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Failed to extract document text: {str(e)}")


class ExportDocxRequest(BaseModel):
    raw_text: str
    document_name: Optional[str] = "Optimized_Resume"


@router.post("/convert-pdf-to-doc")
async def convert_pdf_to_doc(file: UploadFile = File(...)):
    """Convert an uploaded PDF or Word document into structured rich document HTML and text"""
    filename_lower = (file.filename or "").lower()
    if not filename_lower.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="File must be PDF or DOCX format")
    
    temp_dir = "/tmp" if os.environ.get("VERCEL") else os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"conv_{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(temp_dir, temp_filename)
    
    try:
        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
            
        doc_data = convert_document_to_rich_doc(file_location)
        
        if os.path.exists(file_location):
            os.remove(file_location)
            
        return {
            "filename": file.filename,
            "raw_text": doc_data["raw_text"],
            "rich_html": doc_data["rich_html"],
            "word_count": doc_data["word_count"],
            "status": "success"
        }
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Failed to convert document: {str(e)}")


@router.post("/export-docx")
async def export_docx(request: ExportDocxRequest):
    """Export edited resume content as an authentic Microsoft Word (.docx) file"""
    try:
        buffer = generate_docx_from_document(request.raw_text, request.document_name or "Resume")
        doc_bytes = buffer.getvalue()
        
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', request.document_name or "Resume")
        filename = f"{clean_name}.docx"
        
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Word document: {str(e)}")


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

def process_resume(resume_id: str, file_path: str, name: Optional[str], email: Optional[str], job_description: Optional[str] = None):
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
        
        # Add additional information
        if name:
            parsed_data["name"] = name
        if email:
            parsed_data["email"] = email
        if job_description:
            parsed_data["job_description"] = job_description
        if raw_text:
            parsed_data["raw_text"] = raw_text
        
        # Ensure technical_skills and soft_skills exist and are properly formatted
        if not parsed_data.get("technical_skills") and parsed_data.get("skills"):
            parsed_data["technical_skills"] = parsed_data.get("skills", [])
        if "soft_skills" not in parsed_data:
            parsed_data["soft_skills"] = []
        if not parsed_data.get("skills"):
            parsed_data["skills"] = parsed_data.get("technical_skills", [])
        
        # Keep projects as-is; do not inject default project.
        if "projects" not in parsed_data or not isinstance(parsed_data["projects"], list):
            parsed_data["projects"] = []
        
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
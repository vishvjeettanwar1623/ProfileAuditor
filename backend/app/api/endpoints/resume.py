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

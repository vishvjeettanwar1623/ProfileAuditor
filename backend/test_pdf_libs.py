#!/usr/bin/env python3

print("=== TESTING PDF LIBRARY AVAILABILITY ===")

# Test pdfplumber
try:
    import pdfplumber
    print("✅ pdfplumber is available")
    PDFPLUMBER_AVAILABLE = True
except ImportError as e:
    print(f"❌ pdfplumber NOT available: {e}")
    PDFPLUMBER_AVAILABLE = False

# Test PyMuPDF
try:
    import fitz
    print("✅ PyMuPDF (fitz) is available")
    PYMUPDF_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyMuPDF NOT available: {e}")
    PYMUPDF_AVAILABLE = False

# Test pdfminer.six
try:
    from pdfminer.high_level import extract_text
    print("✅ pdfminer.six is available")
    PDFMINER_AVAILABLE = True
except ImportError as e:
    print(f"❌ pdfminer.six NOT available: {e}")
    PDFMINER_AVAILABLE = False

# Test PyPDF2 (fallback)
try:
    import PyPDF2
    print("✅ PyPDF2 is available (fallback)")
    PYPDF2_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyPDF2 NOT available: {e}")
    PYPDF2_AVAILABLE = False

print("\n=== TESTING RESUME PARSER PROJECT EXTRACTION ===")

# Test the actual extract_projects function
try:
    from app.services.resume_parser import extract_projects
    
    # Test with sample broken PDF text (what you're seeing)
    broken_pdf_text = """
    PROJECTS
    Ques tfi
    Blockchain bounty platform
    
    Profile Audit or
    Resume verification
    
    Data
    Roots
    Decentralized platform
    """
    
    print("Testing with broken PDF text:")
    projects = extract_projects(broken_pdf_text)
    print(f"Projects found: {len(projects)}")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project.get('name', 'NO NAME')} - {project.get('description', 'NO DESC')[:50]}")
    
    # Test with good text (what DOCX gives)
    good_text = """
    PROJECTS
    Questfi — Blockchain bounty platform on U2U Network for task creation and payments
    Profile Auditor — Resume verification app generating a Reality Score based on online activity
    Data Roots — Decentralized Data Sharing & Monetization platform
    """
    
    print("\nTesting with good DOCX-style text:")
    projects = extract_projects(good_text)
    print(f"Projects found: {len(projects)}")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project.get('name', 'NO NAME')} - {project.get('description', 'NO DESC')[:50]}")

except Exception as e:
    print(f"❌ Error testing resume parser: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")

import sys
sys.path.append('.')
from app.services.resume_parser import extract_text_from_pdf, extract_text_from_docx, extract_projects

# Test what the PDF extraction is producing
print("=== PDF TEXT EXTRACTION TEST ===")

# Let's test with a sample text that might be coming from PDF extraction
# PDF extraction often breaks em-dashes and formatting
pdf_like_text = """PROJECTS  
Data Roots   Decentralized Data Sharing & Monetization platform[Link].
Questfi   Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor   Resume verification app generating a Reality Score based on online activity ([Link].

ACHIEVEMENTS & EXTRA-CURRICULARS  
EDUCHAIN Delhi Regional Hackathon  MSIT, Delhi
3rd Prize (100$)  17-18 March, 2025
Built a blockchain-based decentralized platform for secure data management, sharing, monetization and ownership."""

print("PDF-like text (without em-dashes):")
print(repr(pdf_like_text))
print("\n" + "="*50)

# Test project extraction from this
projects = extract_projects(None, pdf_like_text)
print(f"Found {len(projects)} projects from PDF-like text:")
for p in projects:
    print(f"  - {p['name']}: {p['description']}")

print("\n" + "="*80 + "\n")

# Test with proper em-dash text (like DOCX might preserve)
docx_like_text = """PROJECTS	
Data Roots — Decentralized Data Sharing & Monetization platform[Link].
Questfi — Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor — Resume verification app generating a Reality Score based on online activity ([Link].

ACHIEVEMENTS & EXTRA-CURRICULARS	
EDUCHAIN Delhi Regional Hackathon	MSIT, Delhi
3rd Prize (100$)	17-18 March, 2025
Built a blockchain-based decentralized platform for secure data management, sharing, monetization and ownership."""

print("DOCX-like text (with em-dashes):")
print(repr(docx_like_text))
print("\n" + "="*50)

# Test project extraction from this
projects = extract_projects(None, docx_like_text)
print(f"Found {len(projects)} projects from DOCX-like text:")
for p in projects:
    print(f"  - {p['name']}: {p['description']}")

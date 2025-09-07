import sys
sys.path.append('.')
from app.services.resume_parser import extract_projects

# Test with what might be coming from PDF extraction
# PDF often completely loses formatting and em-dashes
pdf_broken_text = """Vishvjeet Singh Tanwar
(+91)8708213008 | Email | LinkedIn | Github | Portfolio
EDUCATION JSS University, Noida Noida, India
B.tech in Computer Science Engineering (AI & ML) 2024-2028

PROJECTS
Data Roots Decentralized Data Sharing Monetization platform Link
Questfi Blockchain bounty platform on U2U Network for task creation and payments Link
Profile Auditor Resume verification app generating a Reality Score based on online activity Link

ACHIEVEMENTS EXTRA CURRICULARS
EDUCHAIN Delhi Regional Hackathon MSIT, Delhi
3rd Prize (100$) 17-18 March, 2025"""

print("Testing PDF-like broken formatting...")
print("=" * 60)
print(f"Text sample: {repr(pdf_broken_text[:200])}")
print("=" * 60)

projects = extract_projects(None, pdf_broken_text)

print(f"\n=== RESULTS ===")
print(f"Found {len(projects)} projects:")
for i, p in enumerate(projects, 1):
    print(f"{i}. Name: '{p['name']}'")
    print(f"   Desc: '{p['description']}'")
    print()

if len(projects) == 0:
    print("❌ PDF extraction completely failed - no projects found")
    print("This explains why PDF uploads show '0 of 0 projects'")
else:
    print("✅ PDF extraction working")

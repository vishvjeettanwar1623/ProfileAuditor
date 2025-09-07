import sys
sys.path.append('.')

# Test the complete PDF extraction pipeline
try:
    from app.services.resume_parser import extract_projects, clean_pdf_text
    
    print("=== PDF EXTRACTION DEBUGGING ===")
    
    # Simulate what a PDF might extract (based on our earlier findings)
    pdf_extracted_text = """Vishvjeet Singh Tanwar
(+91)8708213008 | Email | LinkedIn | Github | Portfolio
EDUCATION	
JSS University, Noida	Noida, India
B.tech in Computer Science Engineering (AI & ML)	2024-2028

PROJECTS	
Data Roots   Decentralized Data Sharing & Monetization platform[Link].
Questfi   Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor   Resume verification app generating a Reality Score based on online activity ([Link].

ACHIEVEMENTS & EXTRA-CURRICULARS	
EDUCHAIN Delhi Regional Hackathon	MSIT, Delhi
3rd Prize (100$)	17-18 March, 2025
Built a blockchain-based decentralized platform for secure data management, sharing, monetization and ownership."""

    print("Raw PDF-like text:")
    print(repr(pdf_extracted_text[:500]))
    print("\n" + "="*80)
    
    # Test the project extraction
    print("TESTING PROJECT EXTRACTION:")
    projects = extract_projects(None, pdf_extracted_text)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Number of projects found: {len(projects)}")
    for i, project in enumerate(projects, 1):
        print(f"{i}. Name: '{project['name']}'")
        print(f"   Description: '{project['description']}'")
        print()
    
    # Also test what happens with better formatting
    print("\n" + "="*80)
    print("TESTING WITH EM-DASHES (what good PDF extraction should give):")
    
    better_pdf_text = pdf_extracted_text.replace("   ", " — ")
    projects_better = extract_projects(None, better_pdf_text)
    
    print(f"Number of projects found with em-dashes: {len(projects_better)}")
    for i, project in enumerate(projects_better, 1):
        print(f"{i}. Name: '{project['name']}'")
        print(f"   Description: '{project['description']}'")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

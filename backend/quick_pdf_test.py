#!/usr/bin/env python3

# Quick test for PDF project extraction issues
print("=== TESTING PDF PROJECT EXTRACTION ===")

try:
    from app.services.resume_parser import extract_projects
    
    # Simulate what your PDF extraction produces (mangled text)
    pdf_mangled_text = """
PROJECTS

Ques tfi
Blockchain bounty platform on U2U Network for task creation and payments

Profile Audit or
Resume verification app generating a Reality Score based on online activity

Data
Roots
Decentralized Data Sharing & Monetization platform
"""

    print("Testing PDF-style mangled text:")
    print(f"Input: {repr(pdf_mangled_text[:200])}")
    
    projects = extract_projects(pdf_mangled_text)
    print(f"\nProjects found: {len(projects)}")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. '{project.get('name', 'NO NAME')}' — {project.get('description', 'NO DESC')[:50]}")
    
    if len(projects) == 0:
        print("\n❌ PROBLEM: No projects found in PDF text!")
        print("This suggests the project extraction patterns aren't matching the mangled PDF text")
    else:
        print(f"\n✅ Found {len(projects)} projects from PDF text")

except Exception as e:
    print(f"❌ Error testing: {e}")
    import traceback
    traceback.print_exc()

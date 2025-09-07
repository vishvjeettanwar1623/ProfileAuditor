import sys
sys.path.append('.')
from app.services.resume_parser import extract_projects

# Test with problematic DOCX-like content that's being extracted incorrectly
docx_problematic_text = """PROJECTS	
Data Roots — Decentralized Data Sharing & Monetization platform[Link].
Questfi — Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor — Resume verification app generating a Reality Score based on online activity ([Link].

EXPERIENCE	
HackQuest — Advocate for HackQuest, promoting Web3 and AI adoption through talks, content, and collaborations on community projects and hackathons.

ACHIEVEMENTS & EXTRA-CURRICULARS	
ACPC Algohour 3.0 — Engaged in a national competition, demonstrating problem-solving and algorithmic thinking.
EDUCHAIN Delhi Regional Hackathon — Built a blockchain-based decentralized platform for secure data management.

INTERNSHIP	
Completed a 21 — day internship at GauravGo Games as a Blender Intern.

Social Handles
Twitter — https://x.com/vishvjeet1623
Gmail — vishvjeettanwar.1623@gmail.com"""

print("Testing improved filtering with problematic content...")
print("=" * 60)

projects = extract_projects(None, docx_problematic_text)

print(f"\n=== FINAL RESULTS ===")
print(f"Found {len(projects)} projects:")
for i, p in enumerate(projects, 1):
    print(f"{i}. Name: '{p['name']}'")
    print(f"   Desc: '{p['description']}'")
    print()

expected_projects = ["Data Roots", "Questfi", "Profile Auditor"]
actual_projects = [p['name'] for p in projects]

print("Expected projects:", expected_projects)
print("Actual projects:", actual_projects)

correct = all(proj in actual_projects for proj in expected_projects)
no_extras = len(actual_projects) <= len(expected_projects)

print(f"✅ All expected projects found: {correct}")
print(f"✅ No extra projects: {no_extras}")
print(f"Overall success: {correct and no_extras}")

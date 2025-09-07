import sys
sys.path.append('.')
from app.services.resume_parser import extract_projects

# Test with your exact project text
test_text = """PROJECTS	
Data Roots — Decentralized Data Sharing & Monetization platform[Link].
Questfi — Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor — Resume verification app generating a Reality Score based on online activity ([Link]."""

print("Testing improved project extraction...")
projects = extract_projects(None, test_text)
print(f"\n=== RESULTS ===")
print(f"Found {len(projects)} projects:")
for i, p in enumerate(projects, 1):
    print(f"{i}. Name: '{p['name']}'")
    print(f"   Desc: '{p['description']}'")
    print()

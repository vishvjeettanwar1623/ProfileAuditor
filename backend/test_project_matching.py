import sys
sys.path.append('.')
from app.services.github_service import verify_projects

# Test the improved project matching logic
print("=== TESTING PROJECT MATCHING ===")

# Simulate your case: project "Questfi" should match repo "Questfi-Vietbuild"
test_projects = [
    {"name": "Questfi"},
    {"name": "Data Roots"},
    {"name": "Profile Auditor"}
]

# Simulate your GitHub repositories (including the Questfi-Vietbuild repo)
test_repos = [
    {"name": "Questfi-Vietbuild", "description": "Blockchain bounty platform"},
    {"name": "ProfileAuditor", "description": "Resume verification app"},
    {"name": "data-roots", "description": "Decentralized data sharing platform"},
    {"name": "some-other-repo", "description": "Unrelated repository"},
    {"name": "questfi", "description": "Alternative questfi repo"},  # Test exact match too
]

print(f"Test projects: {[p['name'] for p in test_projects]}")
print(f"Test repositories: {[r['name'] for r in test_repos]}")
print("\n" + "="*60)

# Run the verification
verified_projects, proof = verify_projects(test_projects, test_repos)

print(f"\n=== RESULTS ===")
print(f"Verified projects: {verified_projects}")
print(f"Expected: ['Questfi', 'Data Roots', 'Profile Auditor']")
print(f"Match: {set(verified_projects) == set(['Questfi', 'Data Roots', 'Profile Auditor'])}")

print(f"\nProof details:")
for project, evidence in proof.items():
    print(f"  {project}: {evidence}")

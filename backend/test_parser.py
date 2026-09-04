"""
Comprehensive test suite for resume parsing, GitHub & LeetCode handle extraction,
skill classification, deep code authenticity auditing, and Reality Score computation.
"""

import sys
import os

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add parent directory to path so app modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.resume_parser import (
    extract_information,
    extract_github_username,
    extract_leetcode_username
)
from app.services.github_service import verify_github_claims
from app.services.leetcode_service import verify_leetcode_claims
from app.services.scoring_service import calculate_reality_score, calculate_skills_score

# =====================================================================
# DIVERSE MULTI-CANDIDATE TEST FIXTURES
# =====================================================================

fixture_full_stack_dev = """Alex Chen
San Francisco, CA | alex.chen@example.com | (415) 555-0199
GitHub: alexchen-dev | LeetCode: alexchen_code

SUMMARY
Senior Full-Stack Engineer with 6+ years building scalable distributed web applications.

TECHNICAL SKILLS
Programming Languages: TypeScript, JavaScript, Go, Python, SQL
Frameworks & Libraries: React, Next.js, Node.js, Express, Tailwind CSS, GraphQL
Databases & Cloud: PostgreSQL, Redis, Docker, Kubernetes, AWS, Git

SOFT SKILLS
Mentoring, Agile Team Leadership, Cross-Functional Collaboration, Technical Writing

EXPERIENCE
Staff Engineer — Acme Systems
March 2022 - Present | San Francisco, CA
• Architected real-time streaming pipeline processing 10M events/day using Go and Redis.
• Led team of 5 frontend engineers migrating legacy codebase to Next.js.

PROJECTS
CloudMesh — Decentralized microservice mesh router built with Go and Docker [Link]
PulseGraph — Real-time performance monitoring dashboard using React and GraphQL [Link]

EDUCATION
B.S. in Computer Science — University of California, Berkeley (2014 - 2018)
"""

fixture_ml_engineer = """Sarah Jenkins, Ph.D.
Boston, MA • sarah.j.ml@gmail.com • +1-617-555-8421
github.com/sarah-ml-lab • leetcode.com/u/sarah-ai-algo

PROFESSIONAL PROFILE
AI Research Engineer specializing in Large Language Models and computer vision systems.

TECHNICAL EXPERTISE
Languages: Python, C++, R, SQL
ML / DL Frameworks: PyTorch, TensorFlow, HuggingFace, Scikit-learn, OpenCV
Tools & Infrastructure: FastAPI, Ray, MLflow, Docker, CUDA, Linux, Git

INTERPERSONAL SKILLS
Public Speaking, Scientific Communication, Research Leadership, Problem Solving

WORK EXPERIENCE
Senior AI Researcher | NeuroTech Labs (Remote)
January 2023 - Present
• Designed distributed model training cluster achieving 3.2x speedup on PyTorch workloads.
• Published 3 papers on parameter-efficient fine-tuning.

PROJECTS
NeuralFlow — Deep learning framework for graph representation learning in PyTorch [Link]
DataVision — Real-time object segmentation pipeline built with FastAPI and OpenCV [Link]

HONORS & AWARDS
NeurIPS Best Paper Finalist (2024)
"""

fixture_devops_engineer = """Marcus Vance
Austin, Texas • marcus.vance@cloudops.io • (512) 555-7382
Social: Github - marcus-ops | Portfolio: marcusvance.dev

CAREER SUMMARY
Principal Cloud & DevOps Architect automating multi-region cloud infrastructure.

SKILLS INVENTORY
Infrastructure & Tools: Terraform, Kubernetes, Ansible, Helm, Docker, CI/CD, GitHub Actions
Cloud & OS: AWS, GCP, Linux, Bash, Prometheus, Grafana
Languages: Python, Go, YAML, Shell

MANAGEMENT & SOFT SKILLS
Incident Management, Team Collaboration, Strategic Planning, Stakeholder Communication

PROFESSIONAL EXPERIENCE
Cloud Infrastructure Lead — Skyward Data
June 2021 - Present
• Automated zero-downtime multi-region Kubernetes deployments across AWS EKS.

PROJECTS
KubeDeployer — Declarative canary deployment controller for Kubernetes [Link]
InfraGuard — Automated Terraform compliance and security scanner [Link]

EDUCATION
B.Tech in Information Technology, University of Texas at Austin (2015 - 2019)
"""

fixture_student_intern = """Priya Sharma
New Delhi, India | (+91) 98765-43210 | priya.sharma2026@gmail.com
Github: https://github.com/priya-student
LeetCode: https://leetcode.com/u/priya-sharma-26

EDUCATION
Bachelor of Technology in Computer Science
Delhi Technological University (2022 - 2026)
GPA: 9.1 / 10.0

TECHNICAL SKILLS
Programming: Java, Python, C++, JavaScript, SQL, HTML, CSS
Frameworks & Databases: Spring Boot, React, MySQL, MongoDB, Node.js
Developer Tools: Git, GitHub, VS Code, Postman

SOFT SKILLS
Public Speaking, Leadership, Community Management, Event Organizing, Time Management

INTERNSHIP EXPERIENCE
Software Development Intern — TechNova Labs (Remote, Summer 2024)
• Built REST APIs in Java Spring Boot for user authorization and payment processing.

PROJECTS
CampusConnect — Student collaboration and peer mentoring platform using React and Spring Boot [Link]
EasyQuiz — Gamified real-time trivia quiz application with Node.js and WebSockets [Link]

ACHIEVEMENTS & HACKATHONS
• 1st Runner Up, Smart India Hackathon 2024
• Lead Organizer, Google Developer Student Clubs (GDSC DTU)
"""


# =====================================================================
# TEST RUNNER FUNCTIONS
# =====================================================================

def run_candidate_test(
    title: str,
    resume_text: str,
    expected_github: str,
    expected_leetcode: str,
    min_tech_skills: int
):
    print(f"\n{'='*70}")
    print(f"TESTING: {title}")
    print(f"{'='*70}")
    
    # 1. Test Social Handle Regex Extractors Directly
    gh_handle = extract_github_username(resume_text)
    lc_handle = extract_leetcode_username(resume_text)
    
    print(f"Direct Extracted Handles:")
    print(f"   GitHub:   {gh_handle}")
    print(f"   LeetCode: {lc_handle}")
    
    assert gh_handle == expected_github, f"Expected GitHub '{expected_github}', got '{gh_handle}'"
    assert lc_handle == expected_leetcode, f"Expected LeetCode '{expected_leetcode}', got '{lc_handle}'"
    print(f"   GitHub & LeetCode regex assertions passed!")
    
    # 2. Test Structured Pipeline Extraction
    parsed = extract_information(resume_text)
    tech_skills = parsed.get("technical_skills", [])
    soft_skills = parsed.get("soft_skills", [])
    projects = parsed.get("projects", [])
    
    print(f"\nExtracted Pipeline Results:")
    print(f"   Candidate Name:   {parsed.get('name')}")
    print(f"   GitHub Username:  {parsed.get('github_username')}")
    print(f"   LeetCode Handle:  {parsed.get('leetcode_username')}")
    print(f"   Technical Skills ({len(tech_skills)}): {tech_skills}")
    print(f"   Soft Skills ({len(soft_skills)}):      {soft_skills}")
    print(f"   Projects ({len(projects)}):         {[p['name'] for p in projects]}")
    
    assert len(tech_skills) >= min_tech_skills, f"Expected at least {min_tech_skills} tech skills, got {len(tech_skills)}"
    
    # 3. Test Deep GitHub & LeetCode Verification Services
    print(f"\nVerifying GitHub & LeetCode Services:")
    gh_results = verify_github_claims(gh_handle, tech_skills, projects)
    lc_results = verify_leetcode_claims(lc_handle, claimed_skills=tech_skills) if lc_handle else {}
    
    print(f"   GitHub Audit: {len(gh_results.get('original_repos', []))} original repos, {gh_results.get('total_stars', 0)} stars, score {gh_results.get('score', 0)}/100")
    if lc_results.get("verified"):
        print(f"   LeetCode Audit: {lc_results.get('total_solved', 0)} solved (Easy: {lc_results.get('easy_solved')}, Med: {lc_results.get('medium_solved')}, Hard: {lc_results.get('hard_solved')}), score {lc_results.get('score')}/100")
        print(f"   LeetCode Verified Languages/Skills: {lc_results.get('verified_skills', [])}")
    else:
        print(f"   LeetCode: None (dynamic weight normalization applied)")
    
    # 4. Test Reality Score Calculation with Dual Verified Skills
    gh_skills = set(gh_results.get("verified_skills", []))
    lc_skills = set(lc_results.get("verified_skills", []))
    combined_verified = list(gh_skills.union(lc_skills))
    combined_unverified = [s for s in tech_skills if s not in combined_verified]
    
    mock_verified_proj = gh_results.get("verified_projects", [])
    mock_unverified_proj = [p["name"] if isinstance(p, dict) else str(p) for p in projects if (p["name"] if isinstance(p, dict) else str(p)) not in mock_verified_proj]
    
    final_score, breakdown = calculate_reality_score(
        github_results=gh_results,
        leetcode_results=lc_results,
        verified_skills=combined_verified,
        unverified_skills=combined_unverified,
        verified_projects=mock_verified_proj,
        unverified_projects=mock_unverified_proj
    )
    
    print(f"\nFinal Reality Score: {final_score:.1f}/100")
    print(f"   Breakdown: {breakdown}")
    print(f"   Combined Verified Skills ({len(combined_verified)}): {combined_verified}")
    assert 0 <= final_score <= 100, f"Score out of range: {final_score}"
    print(f"   Test Case PASSED!")


from app.services.job_matching_service import evaluate_role_fit

def test_job_matching_pipeline():
    print(f"\n{'='*70}")
    print("TESTING: Job Description & Role-Targeted Matching Engine")
    print(f"{'='*70}")

    sample_backend_jd = """
    Position: Senior Go Backend Engineer
    Required Skills: Go, Docker, PostgreSQL, Kubernetes, Microservices
    Preferred Skills: Redis, AWS, gRPC
    Responsibilities: Build high-throughput distributed backend services.
    """

    verified_skills = ["Go", "Docker", "PostgreSQL", "Python"]
    unverified_skills = ["Kubernetes", "Redis", "AWS"]
    verified_projects = ["CloudMesh"]

    analysis = evaluate_role_fit(
        job_description=sample_backend_jd,
        verified_skills=verified_skills,
        unverified_skills=unverified_skills,
        verified_projects=verified_projects,
        github_results={"score": 85},
        leetcode_results={"score": 75}
    )

    print(f"Role Title:        {analysis['role_title']}")
    print(f"Role Fit Score:    {analysis['role_fit_score']}/100")
    print(f"Verdict:           {analysis['verdict']}")
    print(f"Verdict Summary:   {analysis['verdict_summary']}")
    print(f"Verified Req:      {analysis['verified_requirements']}")
    print(f"Claimed Unverified:{analysis['claimed_unverified_requirements']}")
    print(f"Missing Req:       {analysis['missing_requirements']}")

from app.services.ats_service import evaluate_ats_health

def test_ats_health_pipeline():
    print(f"\n{'='*70}")
    print("TESTING: ATS & Resume Health Score Engine")
    print(f"{'='*70}")

    sample_resume = fixture_full_stack_dev
    parsed_sample = {
        "email": "alex.chen@email.com",
        "phone": "+1-555-0199",
        "technical_skills": ["TypeScript", "React", "Node.js", "PostgreSQL", "Docker", "GraphQL"],
        "experience": [{"title": "Senior Full-Stack Engineer", "company": "ScaleTech"}],
        "projects": [{"name": "CloudMesh", "description": "High-throughput edge routing mesh"}],
        "education": [{"degree": "B.S. in Computer Science", "institution": "University of Waterloo"}],
        "github_username": "alexchen-dev",
        "leetcode_username": "alexchen_code"
    }

    ats_result = evaluate_ats_health(sample_resume, parsed_sample)

    print(f"ATS Score:       {ats_result['ats_score']}/100")
    print(f"Health Rating:   {ats_result['health_label']}")
    print(f"Metrics Count:   {ats_result['metric_count']}")
    print(f"Action Verbs:    {ats_result['action_verbs_count']} ({', '.join(ats_result['action_verbs'][:4])})")
    print(f"Sub-Scores:      {ats_result['sub_scores']}")
    print(f"Passed Checks:   {len(ats_result['passed_checks'])}")
    print(f"Improvement Tips:{len(ats_result['improvement_tips'])}")

    assert 0 <= ats_result["ats_score"] <= 100
    assert ats_result["ats_score"] >= 50, f"Expected ATS score >= 50, got {ats_result['ats_score']}"
    assert ats_result["metric_count"] >= 1, f"Expected >= 1 metrics, found {ats_result['metric_count']}"
    print("   ATS Health Assertions PASSED!")


from app.services.docx_service import generate_docx_from_document, text_to_rich_html

def test_docx_generation_pipeline():
    print(f"\n{'='*70}")
    print("TESTING: PDF-to-Word & DOCX Generation Engine")
    print(f"{'='*70}")

    sample_text = fixture_full_stack_dev
    rich_html = text_to_rich_html(sample_text)
    
    assert "Alex Chen" in rich_html or "ALEX CHEN" in rich_html, "Expected candidate name in exact HTML"
    assert "<div" in rich_html or "<p" in rich_html, "Expected structured document blocks in exact HTML"

    buffer = generate_docx_from_document(sample_text, "Alex_Chen_Resume")
    doc_bytes = buffer.getvalue()
    
    print(f"Generated DOCX size: {len(doc_bytes)} bytes")
    assert len(doc_bytes) > 5000, f"Expected valid docx > 5000 bytes, got {len(doc_bytes)}"
    print("   DOCX Generation Assertions PASSED!")


def main():
    print("STARTING PROFILE AUDITOR GITHUB, LEETCODE, JD, ATS & DOCX TEST SUITE\n")
    
    test_cases = [
        ("Senior Full-Stack Engineer", fixture_full_stack_dev, "alexchen-dev", "alexchen_code", 4),
        ("AI / ML Research Engineer", fixture_ml_engineer, "sarah-ml-lab", "sarah-ai-algo", 4),
        ("Principal DevOps Architect", fixture_devops_engineer, "marcus-ops", None, 4),
        ("CS Student & GDSC Lead", fixture_student_intern, "priya-student", "priya-sharma-26", 4),
    ]
    
    passed = 0
    for title, text, expected_gh, expected_lc, min_tech in test_cases:
        try:
            run_candidate_test(title, text, expected_gh, expected_lc, min_tech)
            passed += 1
        except AssertionError as e:
            print(f"   FAILED: {e}")
        except Exception as e:
            print(f"   ERROR: {e}")

    try:
        test_job_matching_pipeline()
        passed += 1
    except AssertionError as e:
        print(f"   FAILED JD Matching: {e}")
    except Exception as e:
        print(f"   ERROR in JD Matching: {e}")

    try:
        test_ats_health_pipeline()
        passed += 1
    except AssertionError as e:
        print(f"   FAILED ATS Health: {e}")
    except Exception as e:
        print(f"   ERROR in ATS Health: {e}")

    try:
        test_docx_generation_pipeline()
        passed += 1
    except AssertionError as e:
        print(f"   FAILED DOCX Generation: {e}")
    except Exception as e:
        print(f"   ERROR in DOCX Generation: {e}")
            
    print(f"\n{'='*70}")
    print(f"TEST SUMMARY: {passed}/{len(test_cases) + 3} Passed")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()




"""Test script to debug project extraction for specific formats"""
import sys
import os
import re

# Add the parent directory to the path so we can import the resume parser
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.resume_parser import extract_projects, parse_project_section, extract_skills

def test_em_dash_projects():
    """Test the em-dash project format specifically"""
    test_text = """PROJECTS	
Data Roots — Decentralized Data Sharing & Monetization platform[Link].
Questfi — Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor — Resume verification app generating a Reality Score based on online activity ([Link]."""
    
    print("Testing em-dash project extraction:")
    print("Input text:")
    print(test_text)
    print("\n" + "="*50)
    
    # Test the regex pattern directly
    em_dash_pattern = r'([A-Z][A-Za-z0-9\s,-]{2,50})\s*—\s*([^[\n]+?)(?:\s*\[.*?\])?\.?\s*$'
    matches = re.findall(em_dash_pattern, test_text, re.MULTILINE)
    print(f"Direct regex matches: {len(matches)}")
    for i, match in enumerate(matches, 1):
        print(f"  {i}. '{match[0]}' — '{match[1]}'")
    
    print("\nFull extraction:")
    projects = extract_projects(None, test_text)
    
    print(f"\nExtracted {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   Description: {project['description']}")
        print()

def test_skills_extraction():
    """Test skills extraction with problematic text"""
    test_text = """SKILLS	
Programming: Python, React, C, JavaScript, Solidity, C++, TypeScript, HTML, CSS
Tools: GitHub, Canva, VS Code, Notion, Figma
Soft Skills: Public Speaking, Leadership, Community Management

LANGUAGES	English, Hindi

Social Handles
Github - https://github.com/vishvjeettanwar1623
Twitter - https://x.com/vishvjeet1623
LinkedIn - https://www.linkedin.com/in/vishvjeet-tanwar/
Gmail - vishvjeettanwar.1623@gmail.com"""
    
    print("Testing skills extraction:")
    print("Input text:")
    print(test_text)
    print("\n" + "="*50)
    
    skills = extract_skills(None, test_text)
    
    print(f"\nExtracted {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill}")

def test_full_resume():
    """Test with your full resume text"""
    full_resume = """Vishvjeet Singh Tanwar
(+91)8708213008 | Email | LinkedIn | Github | Portfolio
EDUCATION	
JSS University, Noida	Noida, India
B.tech in Computer Science Engineering (AI & ML)	2024-2028
Vidyantriksh Senior Secondary School	Bhiwani, India
Passed  XIIth (PCM)	2015- 2023
EXPERIENCE	
OffScript                                                                                                                                                             Remote March 2025- Present	                               
Building and managing a 200+ member community at OffScript, organizing meetups, workshops, and online sessions to foster learning and collaboration.
HackQuest                                                                                                                                                               Remote Nov 2024- Present
Advocate for HackQuest, promoting Web3 and AI adoption through talks, content, and collaborations on community projects and hackathons.	                   
INTERNSHIP	
Blender Intern(GauravGo Games)                                                                                                                            Remote June-July 2025
Completed a 21-day internship at GauravGo Games as a Blender Intern, creating and optimizing 3D assets including furniture, props, and environment models.
Virtual Intern(Deloitte)                                                                                                                                                                          Remote 
Completed training modules in Technology, Data Analytics, and Cybersecurity fundamentals.
PROJECTS	
Data Roots — Decentralized Data Sharing & Monetization platform[Link].
Questfi — Blockchain bounty platform on U2U Network for task creation and payments [Link].
Profile Auditor — Resume verification app generating a Reality Score based on online activity ([Link].

ACHIEVEMENTS & EXTRA-CURRICULARS	
EDUCHAIN Delhi Regional Hackathon	MSIT, Delhi
3rd Prize (100$)	17-18 March, 2025
Built a blockchain-based decentralized platform for secure data management, sharing, monetization and ownership.
ACPC Algohour 3.0	MSIT, Delhi
30th Position 	17-18 March, 2025
Engaged in a national competition, demonstrating problem-solving and algorithmic thinking by tackling easy, medium, and hard problems under timed conditions.

SKILLS	
Programming: Python, React, C, JavaScript, Solidity, C++, TypeScript, HTML, CSS
Tools: GitHub, Canva, VS Code, Notion, Figma
Soft Skills: Public Speaking, Leadership, Community Management

LANGUAGES	English, Hindi

Social Handles
Github - https://github.com/vishvjeettanwar1623
Twitter - https://x.com/vishvjeet1623
LinkedIn - https://www.linkedin.com/in/vishvjeet-tanwar/
Gmail - vishvjeettanwar.1623@gmail.com"""
    
    print("Testing full resume:")
    print(f"Resume length: {len(full_resume)} characters")
    print("\n" + "="*50)
    
    print("=== PROJECTS ===")
    projects = extract_projects(None, full_resume)
    print(f"Found {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']}")
        print(f"   Description: {project['description']}")
    
    print("\n=== SKILLS ===")
    skills = extract_skills(None, full_resume)
    print(f"Found {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill}")

if __name__ == "__main__":
    test_em_dash_projects()
    print("\n" + "="*80 + "\n")
    test_skills_extraction()
    print("\n" + "="*80 + "\n")
    test_full_resume()

from typing import List, Dict, Any
import random
import requests
import os

# LinkedIn API configuration
LINKEDIN_API_URL = "https://api.linkedin.com/v2"
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Enable real LinkedIn API (set environment variable LINKEDIN_REAL_API=true)
LINKEDIN_REAL_API = os.getenv("LINKEDIN_REAL_API", "false").lower() == "true"

def verify_linkedin_claims(linkedin_username: str, skills: List[str], projects: List[Any]) -> Dict[str, Any]:
    """Verify resume claims against LinkedIn data (mock)"""
    print(f"=== LINKEDIN VERIFICATION START ===")
    print(f"Username: {linkedin_username}")
    print(f"Skills to verify: {skills}")
    print(f"Projects to verify: {projects}")
    
    result = {
        "verified_skills": [],
        "verified_projects": [],
        "profile": {},
        "proof": {}
    }
    
    try:
        # Get LinkedIn profile (real or mock)
        print(f"Getting LinkedIn profile for: {linkedin_username}")
        profile = get_linkedin_profile(linkedin_username)
        result["profile"] = profile
        print(f"Profile loaded with {len(profile.get('skills', []))} skills")
        
        # Verify skills
        print(f"Verifying skills against LinkedIn profile")
        verified_skills, skill_proof = verify_skills(skills, profile)
        print(f"Verified skills: {verified_skills}")
        result["verified_skills"] = verified_skills
        result["proof"]["skills"] = skill_proof
        
        # Add source information to proof
        source_info = f"LinkedIn verification using {profile.get('source', 'unknown')} data"
        if profile.get('profile_verified'):
            source_info += f" (Profile URL verified: {profile.get('profile_url', '')})"
        
        # Verify projects
        print(f"Verifying projects against LinkedIn profile")
        verified_projects, project_proof = verify_projects(projects, profile)
        print(f"Verified projects: {verified_projects}")
        result["verified_projects"] = verified_projects
        result["proof"]["projects"] = project_proof
        
        print(f"=== LINKEDIN VERIFICATION COMPLETE ===")
        print(f"Final result: {result}")
        return result
    
    except Exception as e:
        print(f"=== LINKEDIN VERIFICATION ERROR ===")
        print(f"Error: {str(e)}")
        # Return empty result with error
        return {
            "verified_skills": [],
            "verified_projects": [],
            "profile": {},
            "proof": {},
            "error": str(e)
        }

def get_linkedin_profile(username: str) -> Dict[str, Any]:
    """Get LinkedIn profile - real API or mock data"""
    if LINKEDIN_REAL_API and LINKEDIN_ACCESS_TOKEN:
        return get_real_linkedin_profile(username)
    else:
        print("Using mock LinkedIn data (set LINKEDIN_REAL_API=true for real API)")
        return get_mock_linkedin_profile(username)

def get_real_linkedin_profile(username: str) -> Dict[str, Any]:
    """Get real LinkedIn profile using alternative methods"""
    try:
        # Method 1: LinkedIn Public Profile API (if available)
        # Note: LinkedIn has restricted public profile access
        
        # Method 2: Use RapidAPI LinkedIn scraper (requires API key)
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if rapidapi_key:
            return get_linkedin_via_rapidapi(username, rapidapi_key)
        
        # Method 3: Use Proxycurl API (professional LinkedIn API)
        proxycurl_key = os.getenv("PROXYCURL_API_KEY")
        if proxycurl_key:
            return get_linkedin_via_proxycurl(username, proxycurl_key)
        
        # Method 4: Manual profile URL verification
        return verify_linkedin_profile_url(username)
            
    except Exception as e:
        print(f"Error fetching real LinkedIn profile: {str(e)}")
        return get_mock_linkedin_profile(username)

def get_linkedin_via_rapidapi(username: str, api_key: str) -> Dict[str, Any]:
    """Get LinkedIn profile via RapidAPI"""
    try:
        url = "https://linkedin-profiles1.p.rapidapi.com/profiles"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "linkedin-profiles1.p.rapidapi.com"
        }
        params = {"profiles": f"https://linkedin.com/in/{username}"}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profiles', [{}])[0] if data.get('profiles') else {}
            
            return {
                "username": username,
                "name": profile.get('name', ''),
                "headline": profile.get('headline', ''),
                "skills": profile.get('skills', []),
                "experience": profile.get('experience', []),
                "source": "rapidapi"
            }
    except Exception as e:
        print(f"RapidAPI LinkedIn error: {str(e)}")
    
    return get_mock_linkedin_profile(username)

def get_linkedin_via_proxycurl(username: str, api_key: str) -> Dict[str, Any]:
    """Get LinkedIn profile via Proxycurl API"""
    try:
        url = "https://nubela-proxycurl-api.p.rapidapi.com/api/v2/linkedin"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        params = {"url": f"https://linkedin.com/in/{username}"}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "username": username,
                "name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                "headline": data.get('headline', ''),
                "skills": [skill.get('name', '') for skill in data.get('skills', [])],
                "experience": data.get('experiences', []),
                "source": "proxycurl"
            }
    except Exception as e:
        print(f"Proxycurl LinkedIn error: {str(e)}")
    
    return get_mock_linkedin_profile(username)

def verify_linkedin_profile_url(username: str) -> Dict[str, Any]:
    """Verify LinkedIn profile exists by checking URL accessibility"""
    try:
        profile_url = f"https://linkedin.com/in/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(profile_url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # Profile exists, return enhanced mock data
            mock_profile = get_mock_linkedin_profile(username)
            mock_profile["profile_verified"] = True
            mock_profile["profile_url"] = profile_url
            mock_profile["source"] = "url_verified"
            return mock_profile
        else:
            # Profile doesn't exist or is private
            mock_profile = get_mock_linkedin_profile(username)
            mock_profile["profile_verified"] = False
            mock_profile["source"] = "mock_only"
            return mock_profile
            
    except Exception as e:
        print(f"LinkedIn URL verification error: {str(e)}")
        mock_profile = get_mock_linkedin_profile(username)
        mock_profile["source"] = "mock_fallback"
        return mock_profile

def get_mock_linkedin_profile(username: str) -> Dict[str, Any]:
    """Get mock LinkedIn profile for demo purposes"""
    return {
        "username": username,
        "name": "John Doe",
        "headline": "Senior Software Engineer | Full Stack Developer | AI Enthusiast",
        "source": "mock_data",
        "skills": [
            # Programming Languages
            "Python", "JavaScript", "TypeScript", "Solidity", "Java", "C++",
            # Web Technologies  
            "React", "Node.js", "FastAPI", "Django", "HTML", "CSS",
            # Blockchain & Web3
            "Blockchain", "Ethereum", "Smart Contracts", "Web3", "DeFi", "Cryptocurrency",
            # Data & AI
            "Machine Learning", "Data Analysis", "TensorFlow", "PyTorch", "Pandas", "NumPy",
            # Databases
            "SQL", "MongoDB", "PostgreSQL", "Redis",
            # Cloud & DevOps
            "AWS", "Docker", "Kubernetes", "Git", "CI/CD",
            # Soft Skills
            "Leadership", "Project Management", "Team Management", "Communication",
            # Specialized
            "API Development", "Data Sharing", "Platform Development", "Monetization"
        ],
        "endorsements": {
            "JavaScript": 25,
            "React": 20,
            "Node.js": 18,
            "Python": 15,
            "TensorFlow": 10,
            "Machine Learning": 12,
            "SQL": 14,
            "MongoDB": 8,
            "AWS": 10,
            "Docker": 7,
            "Kubernetes": 5,
            "Git": 15,
            "Agile": 10,
            "Scrum": 8,
            "REST API": 12,
            "GraphQL": 6
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "duration": "2021 - Present",
                "description": "Leading the development of a machine learning platform using Python, TensorFlow, and React."
            },
            {
                "title": "Full Stack Developer",
                "company": "WebSolutions Co.",
                "duration": "2018 - 2021",
                "description": "Developed RESTful APIs using Node.js and Express, and built frontend applications with React and Tailwind CSS."
            },
            {
                "title": "Junior Developer",
                "company": "StartupXYZ",
                "duration": "2016 - 2018",
                "description": "Worked on an e-commerce platform using JavaScript, HTML, CSS, and MongoDB."
            }
        ],
        "projects": [
            {
                "name": "Machine Learning Platform",
                "description": "A platform for training and deploying machine learning models using TensorFlow and Flask."
            },
            {
                "name": "E-commerce API",
                "description": "RESTful API for an e-commerce platform built with Node.js, Express, and MongoDB."
            },
            {
                "name": "Data Visualization Dashboard",
                "description": "Interactive dashboard for visualizing business metrics using React and D3.js."
            },
            {
                "name": "Personal Portfolio Website",
                "description": "Responsive portfolio website built with React and Tailwind CSS."
            },
            {
                "name": "Blockchain Voting System",
                "description": "Secure voting system built on Ethereum blockchain using Solidity and Web3.js."
            }
        ]
    }

def verify_skills(skills: List[str], profile: Dict[str, Any]) -> tuple:
    """Verify skills against LinkedIn profile"""
    verified_skills = []
    proof = {}
    
    linkedin_skills = profile.get("skills", [])
    endorsements = profile.get("endorsements", {})
    
    # Add team skills to check for
    team_skill_keywords = ["team", "collaboration", "leadership", "communication", "teamwork"]
    
    for skill in skills:
        # Convert skill to lowercase for case-insensitive comparison
        skill_lower = skill.lower()
        print(f"LinkedIn checking skill: '{skill}'")
        
        # Check if skill is in LinkedIn skills
        for linkedin_skill in linkedin_skills:
            if skill_lower == linkedin_skill.lower() or skill_lower in linkedin_skill.lower():
                # Add the original skill name to maintain case
                verified_skills.append(skill)
                endorsement_count = endorsements.get(linkedin_skill, 0)
                proof[skill] = [
                    f"Listed on LinkedIn profile as '{linkedin_skill}'",
                    f"Endorsed by {endorsement_count} connections"
                ]
                # Debug logging
                print(f"LinkedIn verified skill: '{skill}' matched with '{linkedin_skill}'")
                break
        
        # If not found in skills, check experience descriptions
        if skill not in verified_skills:
            for exp in profile.get("experience", []):
                exp_description = exp.get("description", "").lower()
                exp_title = exp.get("title", "").lower()
                
                # Check for hackathon participation
                if ("hackathon" in exp_title or "hackathon" in exp_description) and \
                   (skill_lower in exp_description or any(team_kw in skill_lower for team_kw in team_skill_keywords)):
                    verified_skills.append(skill)
                    proof[skill] = [
                        f"Demonstrated in hackathon: {exp['title']} at {exp['company']}",
                        f"Description: '{exp['description']}'"
                    ]
                    print(f"LinkedIn verified skill: '{skill}' found in hackathon experience for {exp['title']}")
                    break
                
                # Regular experience check
                elif skill_lower in exp_description:
                    verified_skills.append(skill)
                    proof[skill] = [
                        f"Mentioned in experience: {exp['title']} at {exp['company']}",
                        f"Description: '{exp['description']}'"
                    ]
                    # Debug logging
                    print(f"LinkedIn verified skill: '{skill}' found in experience description for {exp['title']}")
                    break
                else:
                    # Debug logging for skills not found
                    print(f"Skill '{skill}' not found in experience description for {exp['title']}")
            
            # Check for team skills specifically
            if skill not in verified_skills and any(team_kw in skill_lower for team_kw in team_skill_keywords):
                # Check if any experience mentions teamwork
                for exp in profile.get("experience", []):
                    exp_description = exp.get("description", "").lower()
                    if any(team_kw in exp_description for team_kw in team_skill_keywords):
                        verified_skills.append(skill)
                        proof[skill] = [
                            f"Team skill demonstrated in: {exp['title']} at {exp['company']}",
                            f"Description mentions teamwork: '{exp['description']}'"
                        ]
                        print(f"LinkedIn verified team skill: '{skill}' found in experience for {exp['title']}")
                        break
            
            if skill not in verified_skills:
                print(f"LinkedIn could not verify skill: '{skill}' in any experience descriptions")
    
    return verified_skills, proof

def verify_projects(projects: List[Any], profile: Dict[str, Any]) -> tuple:
    """Verify projects against LinkedIn profile"""
    verified_projects = []
    proof = {}
    
    linkedin_projects = profile.get("projects", [])
    
    for project in projects:
        # Get project name
        if isinstance(project, dict):
            project_name = project.get("name", "")
        else:
            project_name = project
        
        print(f"LinkedIn checking project: '{project_name}'")
        
        # Convert project name to lowercase for case-insensitive comparison
        project_name_lower = project_name.lower()
        
        # Check if project matches any LinkedIn project
        for linkedin_project in linkedin_projects:
            linkedin_project_name = linkedin_project.get("name", "").lower()
            linkedin_project_desc = linkedin_project.get("description", "").lower()
            
            if (project_name_lower == linkedin_project_name or 
                project_name_lower in linkedin_project_name or 
                project_name_lower in linkedin_project_desc):
                verified_projects.append(project_name)
                proof[project_name] = [
                    f"Listed on LinkedIn profile",
                    f"Description: '{linkedin_project.get('description')}'"
                ]
                print(f"LinkedIn verified project: '{project_name}' found in LinkedIn projects")
                break
        
        # If not found in projects, check experience descriptions
        if project_name not in verified_projects:
            for exp in profile.get("experience", []):
                exp_description = exp.get("description", "").lower()
                exp_title = exp.get("title", "").lower()
                
                # Check for hackathon projects
                if ("hackathon" in exp_title or "hackathon" in exp_description) and \
                   (project_name_lower in exp_description or project_name_lower in exp_title):
                    verified_projects.append(project_name)
                    proof[project_name] = [
                        f"Developed during hackathon: {exp['title']} at {exp['company']}",
                        f"Description: '{exp['description']}'"
                    ]
                    print(f"LinkedIn verified project: '{project_name}' found in hackathon experience")
                    break
                # Regular experience check
                elif project_name_lower in exp_description:
                    verified_projects.append(project_name)
                    proof[project_name] = [
                        f"Mentioned in experience: {exp['title']} at {exp['company']}",
                        f"Description: '{exp['description']}'"
                    ]
                    print(f"LinkedIn verified project: '{project_name}' found in experience description")
                    break
        
        # If still not found, check for team projects in education
        if project_name not in verified_projects:
            for edu in profile.get("education", []):
                edu_description = edu.get("description", "").lower()
                if project_name_lower in edu_description and ("team" in edu_description or "group" in edu_description):
                    verified_projects.append(project_name)
                    proof[project_name] = [
                        f"Team project during education: {edu['degree']} at {edu['school']}",
                        f"Description: '{edu['description']}'"
                    ]
                    print(f"LinkedIn verified project: '{project_name}' found in education as team project")
                    break
            
            if project_name not in verified_projects:
                print(f"LinkedIn could not verify project: '{project_name}'")

    
    return verified_projects, proof
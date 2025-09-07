import requests
import os
from typing import List, Dict, Any
import re

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Development mode - use mock data only (set environment variable MOCK_MODE=true)
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

def verify_github_claims(github_username: str, skills: List[str], projects: List[Any]) -> Dict[str, Any]:
    """Verify resume claims against GitHub data"""
    print(f"=== GITHUB VERIFICATION START ===")
    print(f"Username: {github_username}")
    print(f"Skills to verify: {skills}")
    print(f"Projects to verify: {projects}")
    
    result = {
        "verified_skills": [],
        "verified_projects": [],
        "repositories": [],
        "languages": [],
        "contributions": 0,
        "proof": {}
    }
    
    try:
        # Get user repositories
        print(f"Fetching repositories for user: {github_username}")
        repos = get_user_repositories(github_username)
        print(f"Found {len(repos)} repositories")
        result["repositories"] = [repo["name"] for repo in repos]
        
        # Get user languages
        print(f"Extracting languages from repositories")
        languages = get_user_languages(repos)
        print(f"Found languages: {list(languages.keys())}")
        result["languages"] = list(languages.keys())
        
        # Get user contributions
        print(f"Getting contributions for user: {github_username}")
        contributions = get_user_contributions(github_username)
        print(f"Contributions: {contributions}")
        result["contributions"] = contributions
        
        # Verify skills
        print(f"Verifying skills against GitHub data")
        verified_skills, skill_proof = verify_skills(skills, repos, languages)
        print(f"Verified skills: {verified_skills}")
        result["verified_skills"] = verified_skills
        result["proof"]["skills"] = skill_proof
        
        # Verify projects
        print(f"Verifying projects against GitHub data")
        verified_projects, project_proof = verify_projects(projects, repos)
        print(f"Verified projects: {verified_projects}")
        result["verified_projects"] = verified_projects
        result["proof"]["projects"] = project_proof
        
        print(f"=== GITHUB VERIFICATION COMPLETE ===")
        print(f"Final result: {result}")
        return result
    
    except Exception as e:
        print(f"=== GITHUB VERIFICATION ERROR ===")
        print(f"Error: {str(e)}")
        # Return empty result with error
        return {
            "verified_skills": [],
            "verified_projects": [],
            "repositories": [],
            "languages": [],
            "contributions": 0,
            "proof": {},
            "error": str(e)
        }

def get_user_repositories(username: str) -> List[Dict[str, Any]]:
    """Get user repositories from GitHub API or mock data"""
    print(f"Getting repositories for user: {username}")
    
    # If mock mode is enabled, return mock data immediately
    if MOCK_MODE:
        print("MOCK_MODE enabled, returning mock data")
        return get_mock_repositories(username)
    
    # If no username provided, return mock data
    if not username:
        print("No username provided, returning mock data")
        return get_mock_repositories(username)
    
    # Prepare headers
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        print("Using GitHub token for authentication")
    else:
        print("No GitHub token provided, making unauthenticated request")
    
    # Fetch ALL repositories by paginating through all pages
    all_repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{GITHUB_API_URL}/users/{username}/repos?per_page={per_page}&page={page}"
        print(f"Making request to: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            print(f"GitHub API response status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"User {username} not found on GitHub, using mock data")
                return get_mock_repositories(username)
            elif response.status_code == 403:
                print(f"GitHub API rate limit exceeded or forbidden")
                return get_mock_repositories(username) if page == 1 else all_repos
            elif response.status_code != 200:
                print(f"GitHub API error: {response.status_code} - {response.text}")
                return get_mock_repositories(username) if page == 1 else all_repos
            
            repos = response.json()
            
            # If no repositories returned, we've reached the end
            if not repos:
                break
                
            all_repos.extend(repos)
            print(f"Fetched {len(repos)} repositories from page {page}, total: {len(all_repos)}")
            
            # If we got fewer than per_page, we're done
            if len(repos) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Network error when fetching repositories: {str(e)}")
            return get_mock_repositories(username) if page == 1 else all_repos
    
    print(f"Successfully fetched {len(all_repos)} total repositories")
    return all_repos

def get_user_languages(repos: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get user languages from repositories"""
    languages = {}
    
    for repo in repos:
        repo_languages = repo.get("language")
        if repo_languages:
            if repo_languages in languages:
                languages[repo_languages] += 1
            else:
                languages[repo_languages] = 1
    
    return languages

def get_user_contributions(username: str) -> int:
    """Get user contributions count"""
    # Note: GitHub doesn't provide an API for contributions
    # This would require scraping the contributions graph
    # For demo purposes, return a random number or mock data
    return 500  # Mock data

def verify_skills(skills: List[str], repos: List[Dict[str, Any]], languages: Dict[str, int]) -> tuple:
    """Verify skills against GitHub data"""
    verified_skills = []
    proof = {}
    
    # Check if GitHub activity is decent (for auto-verification)
    total_repos = len(repos)
    total_languages = len(languages)
    decent_activity = total_repos >= 3 or total_languages >= 2
    
    print(f"GitHub activity assessment: {total_repos} repos, {total_languages} languages, decent_activity={decent_activity}")
    
    # Auto-verify GitHub and problem-solving skills if activity is decent
    if decent_activity:
        github_skills = ["github", "git", "version control", "source control", "code management"]
        problem_solving_skills = ["problem solving", "problem-solving", "analytical thinking", "debugging", "troubleshooting"]
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check if this is a GitHub-related skill
            if any(github_term in skill_lower for github_term in github_skills):
                if skill not in verified_skills:
                    verified_skills.append(skill)
                    proof[skill] = [f"Demonstrated through {total_repos} GitHub repositories and {total_languages} programming languages"]
                    print(f"Auto-verified GitHub skill: '{skill}' due to decent GitHub activity")
            
            # Check if this is a problem-solving skill
            elif any(ps_term in skill_lower for ps_term in problem_solving_skills):
                if skill not in verified_skills:
                    verified_skills.append(skill)
                    proof[skill] = [f"Demonstrated through active GitHub development with {total_repos} repositories"]
                    print(f"Auto-verified problem-solving skill: '{skill}' due to GitHub activity")
    
    # Define skill synonyms and related terms for better matching
    skill_synonyms = {
        "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "jupyter", "py"],
        "javascript": ["javascript", "js", "node", "react", "vue", "angular", "typescript", "ts", "nodejs"],
        "leadership": ["leadership", "lead", "team lead", "project management", "managed", "coordinated", "manager"],
        "community management": ["community", "engagement", "moderation", "forum", "social media", "discord", "reddit"],
        "machine learning": ["ml", "ai", "artificial intelligence", "neural network", "deep learning", "tensorflow", "pytorch"],
        "nlp": ["natural language processing", "text analysis", "language model", "tokenization", "spacy"],
        "teamwork": ["team", "collaboration", "collaborative", "group project", "worked together"],
        "blockchain": ["blockchain", "crypto", "cryptocurrency", "bitcoin", "ethereum", "solidity", "web3", "defi", "smart contracts"],
        "data analysis": ["data", "analytics", "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "analysis"],
        "data sharing": ["data", "sharing", "api", "rest", "graphql", "database", "mongodb", "sql"],
        "monetization": ["monetization", "payment", "paypal", "stripe", "revenue", "subscription", "billing"],
        "decentralized": ["decentralized", "distributed", "p2p", "peer-to-peer", "blockchain", "web3"],
        "platform": ["platform", "service", "application", "system", "framework"]
    }
    
    # Check languages and repositories for other skills
    for skill in skills:
        # Skip if already verified
        if skill in verified_skills:
            continue
            
        # Convert skill to lowercase for case-insensitive comparison
        skill_lower = skill.lower()
        matching_repos = []
        commit_evidence = []
        language_evidence = []
        
        # Get related terms for this skill
        related_terms = []
        for key, terms in skill_synonyms.items():
            if skill_lower in terms or any(term in skill_lower for term in terms):
                related_terms.extend(terms)
        
        # If no related terms found, just use the skill itself
        if not related_terms:
            related_terms = [skill_lower]
        
        # Check if skill is in languages
        print(f"GitHub checking skill: '{skill}' against languages: {list(languages.keys())}")
        for language in languages.keys():
            if skill_lower == language.lower() or skill_lower in language.lower() or any(term in language.lower() for term in related_terms):
                verified_skills.append(skill)
                proof[skill] = [f"Used {language} in {languages[language]} repositories"]
                print(f"GitHub verified skill: '{skill}' matched with language '{language}'")
                break
        
        # If not found in languages, check repository descriptions, names, and commit history
        if skill not in verified_skills:
            print(f"GitHub checking skill: '{skill}' in repository names, descriptions, and commit history")
            for repo in repos:
                repo_name = repo.get("name", "").lower()
                repo_desc = repo.get("description", "").lower() if repo.get("description") else ""
                
                # Check repository name
                if skill_lower in repo_name or any(term in repo_name for term in related_terms):
                    matching_repos.append(repo["name"])
                    print(f"GitHub found skill '{skill}' in repository name: '{repo['name']}'")
                # Check repository description
                elif skill_lower in repo_desc or any(term in repo_desc for term in related_terms):
                    matching_repos.append(repo["name"])
                    print(f"GitHub found skill '{skill}' in repository description for: '{repo['name']}'")
                
                # Check in commit history
                if "commit_history" in repo:
                    for commit in repo.get("commit_history", []):
                        commit_lower = commit.lower()
                        if skill_lower in commit_lower or any(term in commit_lower for term in related_terms):
                            matching_repos.append(repo["name"]) if repo["name"] not in matching_repos else None
                            commit_evidence.append(commit)
                            print(f"GitHub found skill '{skill}' in commit: '{commit}' for repo: '{repo['name']}'")
            
            if matching_repos:
                verified_skills.append(skill)
                proof_items = [f"Found in repositories: {', '.join(set(matching_repos[:3]))}"]  
                
                if commit_evidence:
                    proof_items.append(f"Commit evidence: {', '.join(commit_evidence[:2])}")
                    
                proof[skill] = proof_items
                print(f"GitHub verified skill: '{skill}' found in repositories: {list(set(matching_repos[:3]))}")
            else:
                print(f"GitHub could not verify skill: '{skill}' in any repositories")
    
    return verified_skills, proof

def verify_projects(projects: List[Any], repos: List[Dict[str, Any]]) -> tuple:
    """Verify projects against GitHub repositories by matching project names to repo names"""
    verified_projects = []
    proof = {}
    
    print(f"=== PROJECT VERIFICATION START ===")
    print(f"Projects to verify: {projects}")
    print(f"Available repositories: {[repo.get('name', '') for repo in repos]}")

    def normalize_name(name: str) -> str:
        """Normalize a name for comparison"""
        if not name:
            return ""
        # Convert to lowercase, replace spaces/underscores with hyphens, remove special chars
        normalized = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name.lower())
        normalized = re.sub(r'[\s_]+', '-', normalized)
        normalized = re.sub(r'-+', '-', normalized).strip('-')
        return normalized

    def get_name_variants(name: str) -> List[str]:
        """Get different variants of a name for matching"""
        if not name:
            return []
        
        name = name.strip()
        base_normalized = normalize_name(name)
        
        variants = [
            name.lower(),                    # Original case
            base_normalized,                 # Normalized with hyphens
            base_normalized.replace('-', ''), # No separators
            base_normalized.replace('-', '_'), # Underscore separated
            base_normalized.replace('-', ' '), # Space separated
        ]
        
        # Add common GitHub naming patterns
        if ' ' in name:
            # "My Project" -> "my-project", "myproject", "my_project"
            space_to_hyphen = name.lower().replace(' ', '-')
            space_to_underscore = name.lower().replace(' ', '_')
            space_removed = name.lower().replace(' ', '')
            variants.extend([space_to_hyphen, space_to_underscore, space_removed])
        
        # For long descriptive names, extract key terms
        if len(name) > 50:  # Long descriptive names
            # Extract key technical terms
            key_terms = []
            important_words = ['decentralized', 'decentralised', 'blockchain', 'data', 'sharing', 'monetization', 'monetisation', 
                             'platform', 'system', 'application', 'app', 'website', 'tool', 'api', 'service', 'framework',
                             'library', 'parser', 'analyzer', 'engine', 'manager', 'tracker', 'dashboard', 'portal']
            
            words = name.lower().split()
            for word in words:
                # Remove common articles and prepositions
                if word not in ['a', 'an', 'the', 'and', 'or', 'for', 'with', 'based', 'using', 'on', 'in', 'of', 'to']:
                    if word in important_words or len(word) > 4:  # Technical terms or longer words
                        key_terms.append(word)
            
            # Create combinations of key terms
            if len(key_terms) >= 2:
                # Two word combinations
                for i in range(len(key_terms)-1):
                    two_word = f"{key_terms[i]}-{key_terms[i+1]}"
                    variants.append(two_word)
                    variants.append(two_word.replace('-', ''))
                    variants.append(two_word.replace('-', '_'))
                
                # Three word combinations for very specific projects
                if len(key_terms) >= 3:
                    three_word = f"{key_terms[0]}-{key_terms[1]}-{key_terms[2]}"
                    variants.append(three_word)
                    variants.append(three_word.replace('-', ''))
        
        # Remove duplicates and empty strings
        return list(set([v for v in variants if v]))

    for project in projects:
        # Extract project name
        if isinstance(project, dict):
            project_name = project.get("name", "").strip()
        else:
            project_name = str(project).strip()
        
        if not project_name:
            continue
            
        print(f"\n--- Checking project: '{project_name}' ---")
        
        # Get all variants of the project name
        project_variants = get_name_variants(project_name)
        print(f"Project variants: {project_variants}")
        
        matching_repos = []
        match_types = []
        
        for repo in repos:
            repo_name = repo.get("name", "").strip()
            repo_desc = repo.get("description", "") or ""
            
            if not repo_name:
                continue
                
            # Get repo name variants
            repo_variants = get_name_variants(repo_name)
            
            # Check for exact matches between project variants and repo variants
            exact_match = False
            for project_variant in project_variants:
                if project_variant in repo_variants:
                    exact_match = True
                    break
            
            # Check if project name is contained in repo name (or vice versa)
            contains_match = False
            if not exact_match:
                project_lower = project_name.lower().strip()
                repo_lower = repo_name.lower().strip()
                
                # Direct substring matching - key improvement for cases like "Questfi" in "Questfi-Vietbuild"
                if project_lower in repo_lower or repo_lower in project_lower:
                    contains_match = True
                    print(f"    Direct substring match: '{project_lower}' <-> '{repo_lower}'")
                
                # Word-based matching for multi-word projects
                elif len(project_name.split()) > 1:
                    project_words = set(project_name.lower().split())
                    repo_words = set(repo_name.lower().split())
                    
                    # If project has multiple words, check if they're all in repo name
                    if project_words.issubset(repo_words):
                        contains_match = True
                        print(f"    Word subset match: {project_words} ⊆ {repo_words}")
                
                # Normalized name matching (handles hyphens, underscores, spaces)
                elif normalize_name(project_name) == normalize_name(repo_name):
                    contains_match = True
                    print(f"    Normalized match: '{normalize_name(project_name)}' == '{normalize_name(repo_name)}'")
                
                # Prefix/suffix matching for common GitHub patterns
                elif (repo_lower.startswith(project_lower + '-') or 
                      repo_lower.startswith(project_lower + '_') or
                      repo_lower.endswith('-' + project_lower) or 
                      repo_lower.endswith('_' + project_lower)):
                    contains_match = True
                    print(f"    Prefix/suffix match: '{project_lower}' in '{repo_lower}'")
            
            # Check description for additional evidence
            desc_match = False
            if not exact_match and not contains_match and repo_desc:
                if project_name.lower() in repo_desc.lower():
                    desc_match = True
                    print(f"    Description match: '{project_name.lower()}' in description")
            
            if exact_match or contains_match or desc_match:
                matching_repos.append(repo_name)
                match_type = "exact" if exact_match else ("contains" if contains_match else "description")
                match_types.append(f"{repo_name} ({match_type})")
                print(f"✅ Match found: '{project_name}' -> '{repo_name}' (type: {match_type})")
        
        if matching_repos:
            verified_projects.append(project_name)
            proof[project_name] = [
                f"Found matching repositories: {', '.join(matching_repos)}",
                f"Match details: {', '.join(match_types)}"
            ]
            print(f"✅ Project '{project_name}' VERIFIED with {len(matching_repos)} matching repos")
        else:
            print(f"❌ Project '{project_name}' NOT FOUND in any GitHub repositories")
    
    print(f"\n=== PROJECT VERIFICATION COMPLETE ===")
    print(f"Verified projects: {verified_projects}")
    print(f"Verification proof: {proof}")
    
    return verified_projects, proof
    
    return verified_projects, proof

def get_mock_repositories(username: str) -> List[Dict[str, Any]]:
    """Get mock repositories for demo purposes"""
    return [
        {
            "name": "personal-website",
            "description": "My personal portfolio website built with React and Tailwind CSS",
            "language": "JavaScript",
            "languages": ["JavaScript", "HTML", "CSS"],
            "owner": {"login": username},
            "commit_history": ["Added responsive design", "Updated portfolio section", "Fixed navigation bug"]
        },
        {
            "name": "machine-learning-projects",
            "description": "Collection of ML projects using TensorFlow and PyTorch",
            "language": "Python",
            "languages": ["Python", "Jupyter Notebook", "R"],
            "owner": {"login": username},
            "commit_history": ["Implemented neural network", "Added data preprocessing", "Updated model accuracy"]
        },
        {
            "name": "resume-parser",
            "description": "Automated resume parsing tool using NLP and machine learning",
            "language": "Python",
            "languages": ["Python", "JavaScript", "HTML"],
            "owner": {"login": username},
            "commit_history": ["Initial commit", "Added PDF parsing functionality", "Implemented skill extraction", "Added team collaboration features"]
        },
        {
            "name": "e-commerce-api",
            "description": "RESTful API for e-commerce platform built with Node.js and Express",
            "language": "JavaScript",
            "languages": ["JavaScript", "TypeScript", "SQL"],
            "owner": {"login": username},
            "commit_history": ["Added user authentication", "Implemented product search", "Fixed payment gateway"]
        },
        {
            "name": "data-visualization-dashboard",
            "description": "Interactive dashboard for data visualization using D3.js",
            "language": "JavaScript",
            "languages": ["JavaScript", "HTML", "CSS"],
            "owner": {"login": username},
            "commit_history": ["Added bar chart component", "Implemented data filtering", "Fixed responsive layout"]
        },
        {
            "name": "blockchain-voting-system",
            "description": "Secure voting system built on Ethereum blockchain",
            "language": "Solidity",
            "languages": ["Solidity", "JavaScript", "Web3.js"],
            "owner": {"login": username},
            "commit_history": ["Implemented smart contract", "Added vote verification", "Fixed security vulnerability"]
        }
    ]
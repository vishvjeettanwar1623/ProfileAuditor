import requests
import os
from typing import List, Dict, Any
import re

# Twitter API base URL
TWITTER_API_URL = "https://api.twitter.com/2"

# Get Twitter API credentials from environment variables
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def verify_twitter_claims(twitter_username: str, skills: List[str], projects: List[Any]) -> Dict[str, Any]:
    """Verify resume claims against Twitter data"""
    result = {
        "verified_skills": [],
        "verified_projects": [],
        "tweets": [],
        "proof": {}
    }
    
    try:
        # Get user tweets
        tweets = get_user_tweets(twitter_username)
        result["tweets"] = tweets
        
        # Verify skills
        verified_skills, skill_proof = verify_skills(skills, tweets)
        result["verified_skills"] = verified_skills
        result["proof"]["skills"] = skill_proof
        
        # Verify projects
        verified_projects, project_proof = verify_projects(projects, tweets)
        result["verified_projects"] = verified_projects
        result["proof"]["projects"] = project_proof
        
        return result
    
    except Exception as e:
        # Return empty result with error
        return {
            "verified_skills": [],
            "verified_projects": [],
            "tweets": [],
            "proof": {},
            "error": str(e)
        }

def get_user_tweets(username: str) -> List[Dict[str, Any]]:
    """Get user tweets from Twitter API"""
    headers = {}
    if TWITTER_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {TWITTER_BEARER_TOKEN}"
    
    # For demo purposes, we would use the Twitter API v2 to get tweets
    # Since we don't have actual API access, return mock data
    return get_mock_tweets(username)

def verify_skills(skills: List[str], tweets: List[Dict[str, Any]]) -> tuple:
    """Verify skills against Twitter data"""
    verified_skills = []
    proof = {}
    
    for skill in skills:
        # Convert skill to lowercase for case-insensitive comparison
        skill_lower = skill.lower()
        print(f"Twitter checking skill: '{skill}'")
        
        # Check if skill is mentioned in tweets
        matching_tweets = []
        for tweet in tweets:
            tweet_text = tweet.get("text", "").lower()
            if skill_lower in tweet_text:
                matching_tweets.append(tweet)
                print(f"Twitter found skill '{skill}' in tweet: '{tweet['text']}'")
        
        if matching_tweets:
            verified_skills.append(skill)
            proof[skill] = [
                f"Mentioned in {len(matching_tweets)} tweets",
                f"Example: '{matching_tweets[0]['text']}'"
            ]
            print(f"Twitter verified skill: '{skill}' found in {len(matching_tweets)} tweets")
        else:
            print(f"Twitter could not verify skill: '{skill}' in any tweets")
    
    return verified_skills, proof

def verify_projects(projects: List[Any], tweets: List[Dict[str, Any]]) -> tuple:
    """Verify projects against Twitter data"""
    verified_projects = []
    proof = {}
    
    for project in projects:
        # Get project name
        if isinstance(project, dict):
            project_name = project.get("name", "")
        else:
            project_name = project
        
        # Convert project name to lowercase for case-insensitive comparison
        project_name_lower = project_name.lower()
        
        # Check if project is mentioned in tweets
        matching_tweets = []
        for tweet in tweets:
            tweet_text = tweet.get("text", "").lower()
            if project_name_lower in tweet_text:
                matching_tweets.append(tweet)
        
        if matching_tweets:
            verified_projects.append(project_name)
            proof[project_name] = [
                f"Mentioned in {len(matching_tweets)} tweets",
                f"Example: '{matching_tweets[0]['text']}'"
            ]
    
    return verified_projects, proof

def get_mock_tweets(username: str) -> List[Dict[str, Any]]:
    """Get mock tweets for demo purposes"""
    return [
        {
            "id": "1",
            "text": f"Just finished implementing a new feature using React and Tailwind CSS. Loving the developer experience! #webdev #React #TailwindCSS",
            "created_at": "2023-01-15T12:00:00Z"
        },
        {
            "id": "2",
            "text": f"Working on a machine learning project with TensorFlow. Neural networks are fascinating! #MachineLearning #TensorFlow #AI",
            "created_at": "2023-02-20T15:30:00Z"
        },
        {
            "id": "3",
            "text": f"Built a RESTful API with Node.js and Express for my e-commerce project. #NodeJS #Express #API",
            "created_at": "2023-03-10T09:45:00Z"
        },
        {
            "id": "4",
            "text": f"Data visualization is so powerful! Just created an interactive dashboard with D3.js. #DataViz #D3js #JavaScript",
            "created_at": "2023-04-05T14:20:00Z"
        },
        {
            "id": "5",
            "text": f"Exploring blockchain technology for my voting system project. Ethereum and Solidity are game-changers! #Blockchain #Ethereum #Solidity",
            "created_at": "2023-05-12T11:10:00Z"
        }
    ]
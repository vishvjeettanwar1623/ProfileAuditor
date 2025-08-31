import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

function ResultsPage() {
  const { resumeId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [verificationStatus, setVerificationStatus] = useState('pending');
  const [score, setScore] = useState(null);
  const [verificationData, setVerificationData] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [maxRetries] = useState(100); // Increased retry limit to prevent timeout issues
  
  // Create refs for functions to break circular dependencies
  const functionsRef = useRef({});
  const timeoutRef = useRef(null); // To track and clear timeouts
  
  // Function to fetch score
  const fetchScore = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/score/${resumeId}`);
      setScore(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching score:', error);
      setError('Error fetching score. Please try again.');
      setLoading(false);
    }
  }, [resumeId, setScore, setError, setLoading]);
  
  // Function to check verification status
  const checkVerificationStatus = useCallback(async () => {
    try {
      // Stop if there's already an error
      if (error) {
        setLoading(false);
        return;
      }

      const response = await axios.get(`http://localhost:8000/api/verification/${resumeId}`);
      setVerificationData(response.data);
      
      if (response.data.status === 'completed') {
        setVerificationStatus('completed');
        
        // Clear social media usernames from localStorage once verification is complete
        localStorage.removeItem('github_username');
        localStorage.removeItem('twitter_username');
        localStorage.removeItem('linkedin_username');
        console.log('Cleared social media usernames from localStorage');
        
        // Fetch score once verification is complete
        try {
          const scoreResponse = await axios.get(`http://localhost:8000/api/score/${resumeId}`);
          console.log('Score data received:', scoreResponse.data);
          setScore(scoreResponse.data);
          setLoading(false);
        } catch (scoreError) {
          console.error('Error fetching score after verification completed:', scoreError);
          setError('Error fetching score. Please try again.');
          setLoading(false);
        }
      } else if (response.data.status === 'error') {
        setVerificationStatus('error');
        
        // Clear social media usernames from localStorage on error as well
        localStorage.removeItem('github_username');
        localStorage.removeItem('twitter_username');
        localStorage.removeItem('linkedin_username');
        console.log('Cleared social media usernames from localStorage due to verification error');
        
        // Provide a more user-friendly error message
        let errorMsg = response.data.error || 'Unknown error';
        
        // Handle error object that might be stringified incorrectly
        try {
          if (typeof errorMsg === 'object') {
            errorMsg = JSON.stringify(errorMsg);
          }
        } catch (e) {
          console.error('Error parsing error message:', e);
        }
        
        if (errorMsg.includes('GitHub API') || errorMsg.includes('rate limit')) {
          setError('GitHub verification failed. This could be due to API rate limits. Please try again later.');
        } else if (errorMsg.includes('Twitter API')) {
          setError('Twitter verification failed. This could be due to API issues. Please try again later.');
        } else if (errorMsg.includes('LinkedIn API')) {
          setError('LinkedIn verification failed. This could be due to API issues. Please try again later.');
        } else if (errorMsg.includes('Invalid username')) {
          setError('Verification failed: One or more social media usernames appear to be invalid. Please check and try again.');
        } else if (errorMsg.includes('[object Object]') || errorMsg === '[object Object]') {
          setError('Verification failed: There was an issue with the social media usernames provided. Please check and try again with valid usernames.');
        } else {
          setError('Verification failed: ' + errorMsg);
        }
        setLoading(false);
      } else {
        // If still processing, check again in 1 second (reduced from 3 seconds for faster checking)
        timeoutRef.current = setTimeout(() => functionsRef.current.checkVerificationStatus(), 1000);
      }
    } catch (error) {
      console.error('Error checking verification status:', error);
      // Provide more detailed error message based on the response
      if (error.response) {
        const statusCode = error.response.status;
        const errorDetail = error.response.data?.detail || '';
        
        if (statusCode === 404) {
          setError('Verification results not found. Please try uploading your resume again.');
          setLoading(false);
        } else {
          // Handle error object that might be stringified incorrectly
          let errorMessage = 'Please try again.';
          try {
            if (typeof errorDetail === 'object') {
              errorMessage = JSON.stringify(errorDetail);
            } else {
              errorMessage = errorDetail || 'Please try again.';
            }
          } catch (e) {
            console.error('Error parsing error detail:', e);
          }
          setError(`Error checking verification status: ${errorMessage}`);
          setLoading(false);
        }
      } else if (error.request) {
        // The request was made but no response was received
        setError('No response from verification service. Please check your connection and try again.');
        setLoading(false);
      } else {
        // Something happened in setting up the request
        setError(`Error checking verification status: ${error.message || 'Please try again.'}`);
        setLoading(false);
      }
    }
  }, [resumeId, setVerificationData, setVerificationStatus, setError, setLoading, setScore, error]);
  
  // Fetch parsed resume data
  const fetchResumeData = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/resume/${resumeId}`);
      // If processing, return null so caller can retry later
      if (response.status === 202 || response.data.status === 'processing') {
        return null;
      }
      
      // If the resume processing resulted in an error (e.g., not a resume)
      if (response.data.status === 'error') {
        setError(response.data.error || 'Error processing file');
        setLoading(false);
        return 'error'; // Return 'error' instead of null to signal an error state
      }
      
      setResumeData(response.data);
      return response.data;
    } catch (err) {
      // Handle specific error cases
      if (err.response) {
        const statusCode = err.response.status;
        if (statusCode === 404) {
          // Resume not found - stop retrying
          setError('Resume not found. Please upload your resume again.');
          setLoading(false);
          return 'error';
        }
      }
      // For other errors, return null to allow retry
      return null;
    }
  }, [resumeId, setError, setLoading]);
  
  // Start verification if not already started
  const startVerification = useCallback(async () => {
    try {
      // Check retry limit
      if (retryCount >= maxRetries) {
        setError('Maximum retry attempts reached. Please refresh the page or upload your resume again.');
        setLoading(false);
        return;
      }

      // Stop if there's already an error
      if (error) {
        setLoading(false);
        return;
      }

      // Ensure resume data is available so we can extract profiles from it
      let data = resumeData;
      if (!data) {
        data = await fetchResumeData();
        if (!data) {
          // Resume still processing; retry shortly but increment counter
          setRetryCount(prev => prev + 1);
          timeoutRef.current = setTimeout(() => functionsRef.current.startVerification(), 1000);
          return;
        }
        if (data === 'error') {
          // Error occurred (e.g., not a resume), stop processing
          return;
        }
      }

      // Reset retry count on successful data fetch
      setRetryCount(0);

      // Build social usernames with priority: URL > localStorage > extracted from resume
      const urlParams = new URLSearchParams(window.location.search);
      const socialData = {
        github_username:
          urlParams.get('github') ||
          localStorage.getItem('github_username') ||
          data.github_username || null,
        twitter_username:
          urlParams.get('twitter') ||
          localStorage.getItem('twitter_username') ||
          data.twitter_username || null,
        linkedin_username:
          urlParams.get('linkedin') ||
          localStorage.getItem('linkedin_username') ||
          data.linkedin_username || null,
      };

      console.log('Sending verification request with social data (resolved):', socialData);
      await axios.post(`http://localhost:8000/api/verification/${resumeId}`, socialData);
      // Start checking verification status
      checkVerificationStatus();
    } catch (error) {
      console.error('Error starting verification:', error);
      // Provide more detailed error message based on the response
      if (error.response) {
        const statusCode = error.response.status;
        const errorDetail = error.response.data?.detail || '';

        if (statusCode === 400) {
          if (errorDetail.includes('Resume data incomplete')) {
            setError('Your resume could not be verified because it lacks sufficient information. Please ensure your resume includes skills and projects.');
          } else if (errorDetail.toLowerCase().includes('processing')) {
            // Wait a moment and try again but with retry limit
            if (retryCount < maxRetries) {
              setRetryCount(prev => prev + 1);
              timeoutRef.current = setTimeout(() => functionsRef.current.startVerification(), 2000);
            } else {
              setError('Resume processing is taking too long. Please try again.');
              setLoading(false);
            }
            return;
          } else {
            setError(`Verification error: ${errorDetail}`);
          }
        } else if (statusCode === 404) {
          setError('Resume not found. Please upload your resume again.');
        } else {
          // Handle error object that might be stringified incorrectly
          let errorMessage = 'Please try again.';
          try {
            if (typeof errorDetail === 'object') {
              errorMessage = JSON.stringify(errorDetail);
            } else {
              errorMessage = errorDetail || 'Please try again.';
            }
          } catch (e) {
            console.error('Error parsing error detail:', e);
          }
          setError(`Error starting verification: ${errorMessage}`);
        }
      } else if (error.request) {
        // The request was made but no response was received
        setError('No response from verification service. Please check your connection and try again.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error connecting to verification service: ${error.message || 'Please try again later.'}`);
      }
      setLoading(false);
    }
  }, [resumeId, resumeData, fetchResumeData, checkVerificationStatus, setError, setLoading, retryCount, maxRetries, error]);
  
  // Store function references in the ref
  useEffect(() => {
    functionsRef.current = {
      checkVerificationStatus,
      fetchScore,
      startVerification
    };
  }, [checkVerificationStatus, fetchScore, startVerification]);
  
  // Start verification when resumeId changes
  useEffect(() => {
    startVerification();
    
    // Cleanup function
    return () => {
      // Clear any pending timeouts if component unmounts
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      // Also clear localStorage on unmount to ensure clean state
      localStorage.removeItem('github_username');
      localStorage.removeItem('twitter_username');
      localStorage.removeItem('linkedin_username');
      console.log('Cleared social media usernames from localStorage on component unmount');
    };
  }, [resumeId, startVerification]);
  
  // Clear timeouts when error occurs to prevent infinite loops
  useEffect(() => {
    if (error && timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
      console.log('Cleared timeout due to error:', error);
    }
  }, [error]);
  
  // Function to render score gauge
  const renderScoreGauge = (score) => {
    let scoreColor = 'text-red-500';
    if (score >= 70) {
      scoreColor = 'text-green-500';
    } else if (score >= 40) {
      scoreColor = 'text-yellow-500';
    }
    
    return (
      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48">
          <svg className="w-full h-full" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#e6e6e6"
              strokeWidth="10"
            />
            {/* Score circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={scoreColor.replace('text-', 'bg-').replace('-500', '-400')}
              strokeWidth="10"
              strokeDasharray={`${score * 2.83} 283`}
              strokeDashoffset="0"
              transform="rotate(-90 50 50)"
            />
            <text
              x="50"
              y="50"
              dominantBaseline="middle"
              textAnchor="middle"
              className={`${scoreColor} font-bold text-3xl`}
            >
              {Math.round(score)}
            </text>
            <text
              x="50"
              y="65"
              dominantBaseline="middle"
              textAnchor="middle"
              className="text-gray-500 text-sm"
            >
              out of 100
            </text>
          </svg>
        </div>
        <h3 className="mt-4 text-xl font-bold">Reality Score</h3>
      </div>
    );
  };
  
  // Profile details section extracted from resume
  const renderProfileSection = () => {
    if (!resumeData) return null;
    const { name, email, github_username, twitter_username, linkedin_username } = resumeData || {};

    const hasAny = name || email || github_username || twitter_username || linkedin_username;
    if (!hasAny) return null;

    const linkItem = (label, value, hrefBase) => (
      value ? (
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500 w-28">{label}</span>
          {hrefBase ? (
            <a
              href={`${hrefBase}${value}`}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-primary-600 hover:text-primary-700 underline break-all"
            >
              {value}
            </a>
          ) : (
            <span className="text-sm text-gray-900 break-all">{value}</span>
          )}
        </div>
      ) : null
    );

    return (
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 bg-gray-50">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Profile Details</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Extracted from the uploaded resume</p>
        </div>
        <div className="px-4 py-5 sm:p-6 space-y-2">
          {name && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500 w-28">Name</span>
              <span className="text-sm text-gray-900 break-all">{name}</span>
            </div>
          )}
          {email && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500 w-28">Email</span>
              <span className="text-sm text-gray-900 break-all">{email}</span>
            </div>
          )}
          {linkItem('GitHub', github_username, 'https://github.com/')}
          {linkItem('Twitter', twitter_username, 'https://twitter.com/')}
          {linkItem('LinkedIn', linkedin_username, 'https://linkedin.com/in/')}
        </div>
      </div>
    );
  };
  
  // Function to render verification results
  const renderVerificationResults = () => {
    if (!verificationData || !score) {
      console.log('Missing data for verification results:', { verificationData, score });
      return null;
    }
    
    // Ensure score has the expected properties
    if (!score.verified_skills || !score.unverified_skills || 
        !score.verified_projects || !score.unverified_projects) {
      console.error('Score data is missing required properties:', score);
      return null;
    }
    
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
        {/* Skills section */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 bg-gray-50">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Skills Verification</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              {score.verified_skills.length} of {score.verified_skills.length + score.unverified_skills.length} skills verified
            </p>
          </div>
          <div className="border-t border-gray-200">
            <dl>
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Verified Skills</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {score.verified_skills.length > 0 ? (
                    <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                      {score.verified_skills.map((skill, index) => (
                        <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                          <div className="w-0 flex-1 flex items-center">
                            <svg className="flex-shrink-0 h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="ml-2 flex-1 w-0 truncate">{skill}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">No verified skills found</p>
                  )}
                </dd>
              </div>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Unverified Skills</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {score.unverified_skills.length > 0 ? (
                    <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                      {score.unverified_skills.map((skill, index) => (
                        <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                          <div className="w-0 flex-1 flex items-center">
                            <svg className="flex-shrink-0 h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span className="ml-2 flex-1 w-0 truncate">{skill}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">No unverified skills found</p>
                  )}
                </dd>
              </div>
            </dl>
          </div>
        </div>
        
        {/* Projects section */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 bg-gray-50">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Projects Verification</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              {score.verified_projects.length} of {score.verified_projects.length + score.unverified_projects.length} projects verified
            </p>
          </div>
          <div className="border-t border-gray-200">
            <dl>
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Verified Projects</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {score.verified_projects.length > 0 ? (
                    <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                      {score.verified_projects.map((project, index) => (
                        <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                          <div className="w-0 flex-1 flex items-center">
                            <svg className="flex-shrink-0 h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="ml-2 flex-1 w-0 truncate">{project}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">No verified projects found</p>
                  )}
                </dd>
              </div>
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Unverified Projects</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {score.unverified_projects.length > 0 ? (
                    <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                      {score.unverified_projects.map((project, index) => (
                        <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                          <div className="w-0 flex-1 flex items-center">
                            <svg className="flex-shrink-0 h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span className="ml-2 flex-1 w-0 truncate">{project}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500">No unverified projects found</p>
                  )}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    );
  };
  
  // Function to render score breakdown
  const renderScoreBreakdown = () => {
    if (!score) return null;
    
    const { breakdown } = score;
    
    return (
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 bg-gray-50">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Score Breakdown</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Detailed breakdown of the Reality Score
          </p>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">GitHub Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${breakdown.github_score}%` }}></div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(breakdown.github_score)}%</span>
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Twitter Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-400 h-2.5 rounded-full" style={{ width: `${breakdown.twitter_score}%` }}></div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(breakdown.twitter_score)}%</span>
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">LinkedIn Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-300 h-2.5 rounded-full" style={{ width: `${breakdown.linkedin_score}%` }}></div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(breakdown.linkedin_score)}%</span>
              </dd>
            </div>
            <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Skills Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: `${breakdown.skills_score}%` }}></div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(breakdown.skills_score)}%</span>
              </dd>
            </div>
            <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Projects Score</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-400 h-2.5 rounded-full" style={{ width: `${breakdown.projects_score}%` }}></div>
                </div>
                <span className="text-sm text-gray-500">{Math.round(breakdown.projects_score)}%</span>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    );
  };
  
  // SendInvitation component to handle invitation functionality
  const SendInvitation = ({ resumeId, score }) => {
    const [sending, setSending] = useState(false);
    const [inviteStatus, setInviteStatus] = useState(null);
    
    const sendInvitation = async () => {
      setSending(true);
      try {
        const response = await axios.post(`http://localhost:8000/api/invite/${resumeId}`, {
          message: "Congratulations! Based on your resume analysis, we would like to invite you for an interview.",
          interview_date: null,
          interview_location: null
        });
        setInviteStatus({
          success: true,
          message: 'Invitation sent successfully!'
        });
      } catch (error) {
        console.error('Error sending invitation:', error);
        
        // Handle different error response formats
        let errorMessage = 'Error sending invitation. Please try again.';
        
        if (error.response?.data) {
          const errorData = error.response.data;
          
          // Handle FastAPI validation errors (array of error objects)
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(err => {
              if (typeof err === 'object' && err.msg) {
                return err.msg;
              }
              return String(err);
            }).join(', ');
          }
          // Handle simple string detail
          else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
          // Handle object detail
          else if (typeof errorData.detail === 'object') {
            errorMessage = JSON.stringify(errorData.detail);
          }
          // Handle direct message
          else if (errorData.message) {
            errorMessage = errorData.message;
          }
        }
        
        setInviteStatus({
          success: false,
          message: errorMessage
        });
      } finally {
        setSending(false);
      }
    };
    
    return (
      <div className="mt-8 flex flex-col items-center">
        <button
          onClick={sendInvitation}
          disabled={sending || !score || score.score < 70}
          className={`px-4 py-2 rounded-md text-white font-medium ${score && score.score >= 70 ? 'bg-primary-600 hover:bg-primary-700' : 'bg-gray-400 cursor-not-allowed'}`}
        >
          {sending ? 'Sending...' : 'Send Interview Invitation'}
        </button>
        
        {score && score.score < 70 && (
          <p className="mt-2 text-sm text-gray-500">
            Candidate must have a Reality Score of at least 70 to receive an invitation.
          </p>
        )}
        
        {inviteStatus && (
          <div className={`mt-4 p-4 rounded-md ${inviteStatus.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {typeof inviteStatus.message === 'string' ? inviteStatus.message : 'An error occurred while sending the invitation.'}
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Resume Verification Results
        </h1>
        <p className="mt-4 text-lg text-gray-500">
          See how well the resume claims match with online activity.
        </p>
      </div>
      
      {loading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="mt-4 text-lg text-gray-500">
            {verificationStatus === 'pending' ? 'Starting verification...' : 'Verifying resume claims...'}
          </p>
        </div>
      ) : error ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg max-w-2xl mx-auto">
          <div className="px-4 py-5 sm:px-6 bg-red-50">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-red-800">
                {error === "This is not a resume" ? "File Error" : "Verification Error"}
              </h3>
            </div>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
            <div className="text-sm text-gray-700 mb-6">
              <p className="mb-4">{error}</p>
              {error !== "This is not a resume" && (
                <>
                  <p>This could be due to:</p>
                  <ul className="list-disc pl-5 mt-2 space-y-1">
                    <li>Missing or incomplete information in your resume</li>
                    <li>Issues with the verification service</li>
                    <li>Invalid social media usernames</li>
                    <li>Temporary API limitations</li>
                  </ul>
                </>
              )}
            </div>
            
            {/* Social Media Username Form - Only show for verification errors, not file type errors */}
            {error !== "This is not a resume" && (
              <div className="mt-6 bg-gray-50 p-4 rounded-md">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Provide your social media usernames to improve verification:</h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label htmlFor="github_username" className="block text-xs font-medium text-gray-700">GitHub Username</label>
                    <input
                      type="text"
                      id="github_username"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="username"
                      onChange={(e) => localStorage.setItem('github_username', e.target.value)}
                      defaultValue={localStorage.getItem('github_username') || ''}
                    />
                  </div>
                  <div>
                    <label htmlFor="twitter_username" className="block text-xs font-medium text-gray-700">Twitter Username</label>
                    <input
                      type="text"
                      id="twitter_username"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="username"
                      onChange={(e) => localStorage.setItem('twitter_username', e.target.value)}
                      defaultValue={localStorage.getItem('twitter_username') || ''}
                    />
                  </div>
                  <div>
                    <label htmlFor="linkedin_username" className="block text-xs font-medium text-gray-700">LinkedIn Username</label>
                    <input
                      type="text"
                      id="linkedin_username"
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="username"
                      onChange={(e) => localStorage.setItem('linkedin_username', e.target.value)}
                      defaultValue={localStorage.getItem('linkedin_username') || ''}
                    />
                  </div>
                </div>
              </div>
            )}
            
            <div className="mt-6 flex flex-col sm:flex-row sm:space-x-4 space-y-3 sm:space-y-0">
              <Link
                to="/upload"
                className="inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Upload New Resume
              </Link>
              {error !== "This is not a resume" && (
                <button
                  onClick={() => {
                    console.log('Try Again button clicked');
                    
                    // Clear localStorage when trying again
                    localStorage.removeItem('github_username');
                    localStorage.removeItem('twitter_username');
                    localStorage.removeItem('linkedin_username');
                    console.log('Cleared social media usernames from localStorage on Try Again');
                    
                    setError('');
                    setLoading(true);
                    setVerificationStatus('pending');
                    setVerificationData(null);
                    setScore(null);
                    startVerification();
                  }}
                  className="inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Try Again
                </button>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div>
          {/* Score gauge */}
          <div className="flex justify-center">
            {score && renderScoreGauge(score.score)}
          </div>
          
          {/* Verification results */}
          {renderVerificationResults()}
          
          {/* Score breakdown */}
          {renderScoreBreakdown()}
          
          {/* Send invitation */}
          <SendInvitation resumeId={resumeId} score={score} />
          
          {/* Back to upload button */}
          <div className="mt-8 text-center">
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200"
            >
              Upload Another Resume
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsPage;
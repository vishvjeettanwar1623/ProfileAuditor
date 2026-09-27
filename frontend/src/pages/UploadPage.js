import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import WorkflowStepper from '../components/WorkflowStepper';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [consentGiven, setConsentGiven] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [error, setError] = useState('');
  const [showOverrides, setShowOverrides] = useState(false);
  const [githubUsername, setGithubUsername] = useState('');
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  
  // Job Description / Target Role state
  const [showJobDescription, setShowJobDescription] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  
  const navigate = useNavigate();

  const presets = [
    {
      title: 'Backend Go Engineer',
      text: 'Role: Senior Backend Engineer\nRequired Skills: Go, Docker, PostgreSQL, Kubernetes, Microservices, Git\nPreferred Skills: Redis, gRPC, AWS, Kafka\nResponsibilities: Build high-throughput distributed backend services, design resilient SQL schemas, and deploy containerized microservices.'
    },
    {
      title: 'Full-Stack React/Node',
      text: 'Role: Full-Stack Engineer\nRequired Skills: TypeScript, React, Node.js, Next.js, SQL, Tailwind CSS\nPreferred Skills: GraphQL, Docker, Redis\nResponsibilities: Develop interactive responsive web applications and scalable REST APIs.'
    },
    {
      title: 'AI / ML Engineer',
      text: 'Role: Machine Learning Engineer\nRequired Skills: Python, PyTorch, FastAPI, Docker, Scikit-learn, SQL\nPreferred Skills: Ray, MLflow, HuggingFace, CUDA\nResponsibilities: Train and serve large language models and computer vision pipelines.'
    }
  ];

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    multiple: false
  });

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a resume file (PDF or DOCX) to begin.');
      return;
    }
    
    setLoading(true);
    setLoadingStage('Parsing document text & structure...');
    setError('');

    // If manual usernames provided, store in localStorage
    if (githubUsername.trim()) {
      localStorage.setItem('github_username', githubUsername.trim().replace(/^@/, ''));
    }
    if (leetcodeUsername.trim()) {
      localStorage.setItem('leetcode_username', leetcodeUsername.trim().replace(/^@/, ''));
    }
    
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription.trim()) {
      formData.append('job_description', jobDescription.trim());
    }
    
    try {
      setTimeout(() => {
        setLoadingStage('Auditing GitHub commits, LeetCode metrics & JD fit...');
      }, 1200);

      const response = await axios.post(`${API_BASE_URL}/api/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const resumeId = response.data.resume_id;
      sessionStorage.setItem('profileauditor_last_resume_id', resumeId);

      // Append query params if manual overrides exist
      const queryParams = new URLSearchParams();
      if (githubUsername.trim()) queryParams.set('github', githubUsername.trim());
      if (leetcodeUsername.trim()) queryParams.set('leetcode', leetcodeUsername.trim());

      const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';
      navigate(`/results/${resumeId}${queryStr}`);
    } catch (err) {
      console.error('Error uploading resume:', err);
      let errorMessage = 'Failed to process resume. Please check your connection and try again.';
      
      if (err.code === 'ERR_NETWORK') {
        errorMessage = 'Cannot reach backend at http://localhost:8000. Ensure the FastAPI server is running.';
      } else if (err.response?.status === 400) {
        errorMessage = err.response.data?.detail || 'Invalid file format. Please upload a valid PDF or DOCX resume.';
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error during parsing. Please try again.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
      setLoadingStage('');
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-4 sm:py-6">
      {/* Interactive Workflow Pipeline Navigation */}
      <WorkflowStepper />

      {/* Header */}
      <div className="mb-6 text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Audit Developer Resume</h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Upload a resume to verify claimed languages, audit GitHub code authenticity, and evaluate match against target job requirements.
        </p>
      </div>

      {/* Main Upload Card */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 md:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dropzone */}
          <div>
            <div
              {...getRootProps()}
              className={`border border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                isDragActive
                  ? 'border-white bg-[#161A20]'
                  : file
                  ? 'border-slate-500 bg-[#161A20]/70'
                  : 'border-[#262C36] hover:border-slate-400 bg-[#161A20]/40 hover:bg-[#161A20]'
              }`}
            >
              <input {...getInputProps()} />

              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="w-12 h-12 rounded-xl bg-[#161A20] border border-[#262C36] flex items-center justify-center text-slate-300">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>

                {file ? (
                  <div>
                    <p className="text-xs font-semibold text-white">{file.name}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">{formatFileSize(file.size)}</p>
                    <p className="text-[10px] text-slate-500 mt-2">Click or drag to replace file</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-xs font-medium text-slate-200">
                      Drag & drop resume here, or <span className="font-semibold text-white underline underline-offset-2">browse files</span>
                    </p>
                    <p className="text-[11px] text-slate-500 mt-1">
                      Supports PDF and DOCX documents (up to 10MB)
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Optional: Target Job Description / Role Requirements */}
          <div className="pt-2 border-t border-[#1F242D]">
            <button
              type="button"
              onClick={() => setShowJobDescription(!showJobDescription)}
              className="flex items-center justify-between w-full text-left text-xs font-medium text-slate-300 hover:text-white transition-colors py-1"
            >
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white">Target Job Description / Role Requirements</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#161A20] text-emerald-400 border border-emerald-500/20 font-medium">
                  Enables Role Fit Score
                </span>
              </div>
              <svg
                className={`w-3.5 h-3.5 text-slate-400 transition-transform ${showJobDescription ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showJobDescription && (
              <div className="mt-3 p-4 rounded-xl bg-[#161A20] border border-[#262C36] space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Quick Role Presets:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {presets.map((p, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setJobDescription(p.text)}
                        className="px-2.5 py-1 rounded-md text-[10px] font-medium bg-[#111418] hover:bg-[#1E232B] text-slate-300 border border-[#262C36] transition-all"
                      >
                        {p.title}
                      </button>
                    ))}
                  </div>
                </div>

                <textarea
                  rows={4}
                  placeholder="Paste Job Description, required tech stack, or hiring requirements here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="w-full text-xs p-3 rounded-lg bg-[#111418] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600 leading-relaxed font-sans"
                />
                <p className="text-[10px] text-slate-500">
                  ProfileAuditor will cross-reference candidate's verified code proof directly against these required technical skills.
                </p>
              </div>
            )}
          </div>

          {/* Optional Profile Overrides */}
          <div className="pt-2 border-t border-[#1F242D]">
            <button
              type="button"
              onClick={() => setShowOverrides(!showOverrides)}
              className="flex items-center justify-between w-full text-left text-xs font-medium text-slate-400 hover:text-white transition-colors py-1"
            >
              <span>Optional: Specify candidate profiles manually</span>
              <svg
                className={`w-3.5 h-3.5 transition-transform ${showOverrides ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showOverrides && (
              <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 p-3.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">GitHub Username</label>
                  <input
                    type="text"
                    placeholder="e.g. torvalds"
                    value={githubUsername}
                    onChange={(e) => setGithubUsername(e.target.value)}
                    className="w-full text-xs px-3 py-2 rounded-lg bg-[#111418] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">LeetCode Username</label>
                  <input
                    type="text"
                    placeholder="e.g. neetcode"
                    value={leetcodeUsername}
                    onChange={(e) => setLeetcodeUsername(e.target.value)}
                    className="w-full text-xs px-3 py-2 rounded-lg bg-[#111418] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Form Consent Checkbox */}
          <div className="pt-2 border-t border-[#1F242D]">
            <label htmlFor="form-consent" className="flex items-start gap-3 cursor-pointer select-none">
              <input
                id="form-consent"
                type="checkbox"
                checked={consentGiven}
                onChange={(e) => setConsentGiven(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded bg-[#161A20] border-[#262C36] text-white focus:ring-2 focus:ring-white focus:outline-none cursor-pointer"
                aria-required="true"
              />
              <span className="text-xs text-slate-400 leading-relaxed">
                I confirm that I have the right to process this resume and agree to the{' '}
                <Link to="/terms" target="_blank" rel="noopener noreferrer" className="text-white underline hover:text-slate-200 font-medium">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" target="_blank" rel="noopener noreferrer" className="text-white underline hover:text-slate-200 font-medium">
                  Privacy Policy
                </Link>
                . No unauthorized data scraping or cross-site tracking is performed.
              </span>
            </label>
          </div>

          {/* Error notice */}
          {error && (
            <div className="p-3.5 rounded-lg bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2">
              <span className="font-bold">•</span>
              <span>{error}</span>
            </div>
          )}

          {/* Submit */}
          <div>
            <button
              type="submit"
              disabled={loading || !file || !consentGiven}
              className="w-full inline-flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-xs font-semibold text-[#090A0C] bg-white hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-[0.99] shadow-sm"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-[#090A0C]" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{loadingStage || 'Processing Resume...'}</span>
                </>
              ) : (
                <>
                  <span>Begin Verification Audit</span>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default UploadPage;
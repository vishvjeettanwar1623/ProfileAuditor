import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import WorkflowStepper from '../components/WorkflowStepper';

function ResultsPage() {
  const { resumeId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [verificationStatus, setVerificationStatus] = useState('pending');
  const [score, setScore] = useState(null);
  const [verificationData, setVerificationData] = useState(null);
  const [resumeData, setResumeData] = useState(null);

  useEffect(() => {
    if (resumeId) {
      sessionStorage.setItem('profileauditor_last_resume_id', resumeId);
    }
  }, [resumeId]);

  // Main linear audit pipeline
  useEffect(() => {
    let isMounted = true;
    let pollTimeout = null;

    const runAuditPipeline = async () => {
      try {
        setLoading(true);
        setError(null);

        // 1. Fetch parsed resume data
        const resumeRes = await axios.get(`${API_BASE_URL}/api/resume/${resumeId}`);
        if (!isMounted) return;

        if (resumeRes.status === 202 || resumeRes.data.status === 'processing') {
          // Still processing, poll in 1.2s
          pollTimeout = setTimeout(runAuditPipeline, 1200);
          return;
        }

        if (resumeRes.data.status === 'error') {
          setError(resumeRes.data.error || 'Failed to parse resume');
          setLoading(false);
          return;
        }

        const parsedResume = resumeRes.data;
        setResumeData(parsedResume);

        // 2. Check if verification was already executed
        let isAlreadyDone = false;
        try {
          const verCheck = await axios.get(`${API_BASE_URL}/api/verification/${resumeId}`);
          if (!isMounted) return;
          if (verCheck.data && verCheck.data.status === 'completed') {
            setVerificationData(verCheck.data);
            setVerificationStatus('completed');
            isAlreadyDone = true;
          }
        } catch (_) {
          // 404 is expected on first run before verification is started
        }

        // 3. If not already verified, start verification POST
        if (!isAlreadyDone) {
          const urlParams = new URLSearchParams(window.location.search);
          const handles = {
            github_username:
              urlParams.get('github') ||
              localStorage.getItem('github_username') ||
              parsedResume.github_username ||
              null,
            leetcode_username:
              urlParams.get('leetcode') ||
              localStorage.getItem('leetcode_username') ||
              parsedResume.leetcode_username ||
              null,
          };

          await axios.post(`${API_BASE_URL}/api/verification/${resumeId}`, handles);
          if (!isMounted) return;

          const verResult = await axios.get(`${API_BASE_URL}/api/verification/${resumeId}`);
          if (!isMounted) return;
          setVerificationData(verResult.data);
          setVerificationStatus('completed');
        }

        // 4. Fetch Reality Score
        const scoreRes = await axios.get(`${API_BASE_URL}/api/score/${resumeId}`);
        if (!isMounted) return;
        setScore(scoreRes.data);
        setLoading(false);

        // Clear overrides from local storage
        localStorage.removeItem('github_username');
        localStorage.removeItem('leetcode_username');

      } catch (err) {
        if (!isMounted) return;
        console.error('Audit pipeline error:', err);
        let msg = 'Failed to complete candidate verification audit.';
        if (err.response?.data?.detail) {
          msg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
        } else if (err.message) {
          msg = err.message;
        }
        setError(msg);
        setLoading(false);
      }
    };

    runAuditPipeline();

    return () => {
      isMounted = false;
      if (pollTimeout) clearTimeout(pollTimeout);
    };
  }, [resumeId]);

  const getScoreMeta = (scoreVal) => {
    if (scoreVal >= 80) {
      return {
        label: 'Strong Corroboration',
        subtext: 'High percentage of technical claims backed by original code and problem-solving records.',
        strokeColor: '#10B981',
        textColor: 'text-emerald-400',
        badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      };
    }
    if (scoreVal >= 50) {
      return {
        label: 'Moderate Alignment',
        subtext: 'Core claims corroborated, with some unverified skills or private repositories.',
        strokeColor: '#F59E0B',
        textColor: 'text-amber-400',
        badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      };
    }
    return {
      label: 'Low Verifiability',
      subtext: 'Significant gap between resume claims and discoverable public codebases.',
      strokeColor: '#EF4444',
      textColor: 'text-red-400',
      badgeBg: 'bg-red-500/10 text-red-400 border-red-500/20',
    };
  };

  // Sub-component: Send Invitation Email
  const SendInvitationModule = ({ scoreData }) => {
    const [sending, setSending] = useState(false);
    const [inviteStatus, setInviteStatus] = useState(null);
    const [interviewDate, setInterviewDate] = useState('');
    const [interviewLocation, setInterviewLocation] = useState('Google Meet');
    const [customMessage, setCustomMessage] = useState(
      `Hello, based on your audited profile (Reality Score: ${Math.round(scoreData?.score || 0)}/100), we would like to invite you for a technical interview.`
    );

    const handleSend = async (e) => {
      e.preventDefault();
      setSending(true);
      setInviteStatus(null);
      try {
        await axios.post(`${API_BASE_URL}/api/invite/${resumeId}`, {
          message: customMessage,
          interview_date: interviewDate || null,
          interview_location: interviewLocation || null,
        });
        setInviteStatus({
          success: true,
          message: 'Invitation email dispatched successfully.'
        });
      } catch (err) {
        console.error('Error sending invitation:', err);
        let errorMsg = 'Failed to dispatch email. Check SMTP configuration in backend/.env.';
        if (err.response?.data?.detail) {
          errorMsg = typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : JSON.stringify(err.response.data.detail);
        }
        setInviteStatus({
          success: false,
          message: errorMsg
        });
      } finally {
        setSending(false);
      }
    };

    return (
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 sm:p-8 mt-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#1F242D]">
          <div>
            <h3 className="text-base font-bold text-white">Send Candidate Interview Invitation</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Dispatch an official technical interview invitation directly to the candidate email.
            </p>
          </div>
          <div className="text-xs text-slate-300 font-mono bg-[#161A20] px-3 py-1.5 rounded-lg border border-[#262C36]">
            {resumeData?.email || 'No email extracted'}
          </div>
        </div>

        <form onSubmit={handleSend} className="pt-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Suggested Date & Time</label>
              <input
                type="text"
                placeholder="e.g. Tomorrow at 2:00 PM EST"
                value={interviewDate}
                onChange={(e) => setInterviewDate(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-lg bg-[#161A20] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Location / Video Link</label>
              <input
                type="text"
                value={interviewLocation}
                onChange={(e) => setInterviewLocation(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-lg bg-[#161A20] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Message Content</label>
            <textarea
              rows={3}
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              className="w-full text-xs p-3 rounded-lg bg-[#161A20] text-white border border-[#262C36] focus:outline-none focus:border-white"
            />
          </div>

          {inviteStatus && (
            <div className={`p-3 rounded-lg text-xs flex items-center gap-2 border ${
              inviteStatus.success
                ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
                : 'bg-red-950/40 border-red-800/60 text-red-300'
            }`}>
              <span className="font-bold">•</span>
              <span>{inviteStatus.message}</span>
            </div>
          )}

          <div className="flex items-center justify-between pt-1">
            <p className="text-[11px] text-slate-500">
              Sends via configured Gmail SMTP credentials.
            </p>

            <button
              type="submit"
              disabled={sending}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold text-[#090A0C] bg-white hover:bg-slate-200 disabled:opacity-50 transition-all active:scale-[0.98] shadow-sm"
            >
              {sending ? 'Sending...' : 'Dispatch Invitation'}
            </button>
          </div>
        </form>
      </div>
    );
  };

  // Main Loading View
  if (loading) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-4">
        <div className="w-10 h-10 rounded-full border-2 border-white border-t-transparent animate-spin mx-auto mb-2" />
        <h2 className="text-xl font-bold text-white tracking-tight">Auditing Candidate Footprint</h2>
        <p className="text-xs text-slate-400">
          {verificationStatus === 'pending'
            ? 'Querying GitHub repositories & LeetCode profile...'
            : 'Evaluating authentic code ownership & computing Reality Score...'}
        </p>
      </div>
    );
  }

  // Error View
  if (error) {
    return (
      <div className="max-w-md mx-auto py-12">
        <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 text-center space-y-4">
          <div className="w-10 h-10 rounded-full bg-red-950/40 border border-red-800/50 flex items-center justify-center text-red-400 mx-auto font-bold">
            !
          </div>
          <h2 className="text-lg font-bold text-white">Verification Notice</h2>
          <p className="text-xs text-slate-400">{error}</p>

          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg bg-white hover:bg-slate-200 text-[#090A0C] text-xs font-semibold shadow-sm transition-all"
            >
              Retry Audit
            </button>
            <Link
              to="/upload"
              className="px-4 py-2 rounded-lg bg-[#161A20] hover:bg-[#1E232B] text-slate-300 text-xs font-semibold border border-[#262C36] transition-all"
            >
              Upload Another Resume
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const realityScore = score?.score ? Math.round(score.score) : 0;
  const scoreMeta = getScoreMeta(realityScore);
  const candidateName = resumeData?.name || 'Candidate Report';
  const candidateEmail = resumeData?.email || 'No email specified';
  const githubUser = resumeData?.github_username || verificationData?.github_username || verificationData?.github?.username;
  const leetcodeUser = resumeData?.leetcode_username || verificationData?.leetcode_username || verificationData?.leetcode?.username;
  const breakdown = score?.breakdown || {};

  const verifiedSkills = score?.verified_skills || [];
  const unverifiedSkills = score?.unverified_skills || [];
  const softSkills = score?.soft_skills || verificationData?.soft_skills || resumeData?.soft_skills || [];
  const verifiedProjects = score?.verified_projects || [];
  const unverifiedProjects = score?.unverified_projects || [];

  const githubData = verificationData?.github || verificationData?.github_results || {};
  const leetcodeData = verificationData?.leetcode || {};

  return (
    <div className="max-w-5xl mx-auto space-y-6 pt-2">
      {/* Interactive Workflow Pipeline Navigation */}
      <WorkflowStepper activeResumeId={resumeId} candidateName={candidateName} />

      {/* Candidate Header & Reality Score Card */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-[#1F242D]">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-lg bg-white text-[#090A0C] flex items-center justify-center font-bold text-base shadow-sm">
              {candidateName.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-xl font-bold text-white tracking-tight">{candidateName}</h1>
                <span className="text-xs px-2.5 py-0.5 rounded bg-[#161A20] text-slate-200 font-semibold border border-[#262C36] font-mono">
                  Reality: {realityScore}/100
                </span>
                {score?.role_analysis && (
                  <span className="text-xs px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20 font-mono">
                    Role Fit: {score.role_analysis.role_fit_score}%
                  </span>
                )}
                {score?.ats_analysis && (
                  <span className="text-xs px-2.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-semibold border border-blue-500/20 font-mono">
                    ATS: {score.ats_analysis.ats_score}%
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                {candidateEmail} • ID: AUD-{resumeId.slice(0, 8)}
              </p>
            </div>
          </div>

          {/* Action buttons & Verified handles */}
          <div className="flex flex-wrap items-center gap-2">
            {githubUser && (
              <a
                href={`https://github.com/${githubUser}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-200 transition-colors border border-[#262C36]"
              >
                <span className="text-slate-400">GitHub:</span>
                <span className="font-semibold text-white">@{githubUser}</span>
              </a>
            )}
            {leetcodeUser && (
              <a
                href={`https://leetcode.com/u/${leetcodeUser}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-200 transition-colors border border-[#262C36]"
              >
                <span className="text-slate-400">LeetCode:</span>
                <span className="font-semibold text-white">@{leetcodeUser}</span>
              </a>
            )}
            
            <Link
              to={`/editor/${resumeId}`}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white hover:bg-slate-200 text-[#090A0C] transition-all shadow-sm active:scale-[0.98] focus:ring-2 focus:ring-white focus:outline-none"
            >
              <span>Live ATS Editor</span>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>

            <button
              onClick={() => window.print()}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-300 border border-[#262C36] transition-all"
            >
              Print Report
            </button>
          </div>
        </div>

        {/* Reality Score & Sub-scores Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 pt-6 items-center">
          {/* SVG Radial Gauge */}
          <div className="md:col-span-4 flex flex-col items-center justify-center p-5 rounded-xl bg-[#161A20] border border-[#262C36] text-center">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">Reality Score</span>

            <div className="relative w-36 h-36 my-1">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#1F242D"
                  strokeWidth="8"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke={scoreMeta.strokeColor}
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 50}`}
                  strokeDashoffset={`${2 * Math.PI * 50 * (1 - realityScore / 100)}`}
                  strokeLinecap="round"
                />
              </svg>

              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-white leading-none font-mono">
                  {realityScore}
                </span>
                <span className="text-[10px] text-slate-500 mt-0.5 font-mono">/ 100</span>
              </div>
            </div>

            <h3 className="font-bold text-white text-sm mt-1">{scoreMeta.label}</h3>
            <p className="text-[11px] text-slate-400 max-w-xs mt-0.5">{scoreMeta.subtext}</p>
          </div>

          {/* Sub-scores Progress Bars */}
          <div className="md:col-span-8 space-y-3.5">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Verification Breakdown
            </h3>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                  <span>GitHub Code Authenticity</span>
                  <span className="font-mono">{Math.round(breakdown.github_score || 0)}%</span>
                </div>
                <div className="w-full bg-[#1F242D] rounded-md h-2">
                  <div className="h-2 rounded-md bg-white transition-all" style={{ width: `${Math.min(100, breakdown.github_score || 0)}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                  <span>Technical Skills Verification</span>
                  <span className="font-mono">{Math.round(breakdown.skills_score || 0)}%</span>
                </div>
                <div className="w-full bg-[#1F242D] rounded-md h-2">
                  <div className="h-2 rounded-md bg-slate-300 transition-all" style={{ width: `${Math.min(100, breakdown.skills_score || 0)}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                  <span>Projects Verification</span>
                  <span className="font-mono">{Math.round(breakdown.projects_score || 0)}%</span>
                </div>
                <div className="w-full bg-[#1F242D] rounded-md h-2">
                  <div className="h-2 rounded-md bg-slate-300 transition-all" style={{ width: `${Math.min(100, breakdown.projects_score || 0)}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                  <span>LeetCode Problem Solving</span>
                  <span className="font-mono">{Math.round(breakdown.leetcode_score || 0)}%</span>
                </div>
                <div className="w-full bg-[#1F242D] rounded-md h-2">
                  <div className="h-2 rounded-md bg-slate-400 transition-all" style={{ width: `${Math.min(100, breakdown.leetcode_score || 0)}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Target Role & Job Description Evaluation Card (if provided) */}
      {score?.role_analysis && (
        <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3.5 border-b border-[#1F242D]">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Target Role Fit: {score.role_analysis.role_title}
                </h3>
                <span className="text-xs px-2.5 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold font-mono">
                  Role Fit: {score.role_analysis.role_fit_score}%
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Domain: {score.role_analysis.domain_focus} • Verified code evidence evaluated directly against job requirements.
              </p>
            </div>
            <span className="text-xs px-3 py-1 rounded-lg bg-[#161A20] font-bold text-white border border-[#262C36]">
              {score.role_analysis.verdict}
            </span>
          </div>

          {/* Hiring Verdict Banner */}
          <div className="p-3.5 rounded-xl bg-[#161A20] border border-[#262C36] text-xs text-slate-300 leading-relaxed flex items-start gap-2.5">
            <svg className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{score.role_analysis.verdict_summary}</span>
          </div>

          {/* Core Requirements Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
            {/* Verified in Code */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#161A20]/60 border border-[#262C36]">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#262C36]">
                <span className="font-bold text-emerald-400 uppercase tracking-wider text-[10px]">
                  Verified in Code ({score.role_analysis.verified_requirements.length})
                </span>
                <span className="text-[10px] font-semibold text-emerald-400 font-mono">MATCH</span>
              </div>
              {score.role_analysis.verified_requirements.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {score.role_analysis.verified_requirements.map((req, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                      {req}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 italic py-1">No core requirements verified in code.</p>
              )}
            </div>

            {/* Claimed Unverified */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#161A20]/60 border border-[#262C36]">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#262C36]">
                <span className="font-bold text-amber-400 uppercase tracking-wider text-[10px]">
                  Claimed Unverified ({score.role_analysis.claimed_unverified_requirements.length})
                </span>
                <span className="text-[10px] font-semibold text-amber-400 font-mono">PENDING</span>
              </div>
              {score.role_analysis.claimed_unverified_requirements.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {score.role_analysis.claimed_unverified_requirements.map((req, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
                      {req}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 italic py-1">All claimed JD skills were verified.</p>
              )}
            </div>

            {/* Missing from Resume */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#161A20]/60 border border-[#262C36]">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#262C36]">
                <span className="font-bold text-red-400 uppercase tracking-wider text-[10px]">
                  Missing from Resume ({score.role_analysis.missing_requirements.length})
                </span>
                <span className="text-[10px] font-semibold text-red-400 font-mono">GAP</span>
              </div>
              {score.role_analysis.missing_requirements.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {score.role_analysis.missing_requirements.map((req, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-red-500/10 text-red-300 border border-red-500/30">
                      {req}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 italic py-1">No missing requirements from JD.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ATS & Resume Health Evaluation Card */}
      {score?.ats_analysis && (
        <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3.5 border-b border-[#1F242D]">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  ATS & Resume Health Audit
                </h3>
                <span className="text-xs px-2.5 py-0.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold font-mono">
                  ATS Score: {score.ats_analysis.ats_score}%
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Evaluates quantifiable impact metrics, action verb variety, section structure, and formatting readability.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Link
                to={`/editor/${resumeId}`}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white hover:bg-slate-200 text-[#090A0C] transition-all shadow-sm"
              >
                <span>Edit & Optimize in Live Editor</span>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </Link>
              <span className="text-xs px-3 py-1.5 rounded-lg bg-[#161A20] font-bold text-white border border-[#262C36]">
                {score.ats_analysis.health_label}
              </span>
            </div>
          </div>

          {/* Sub-breakdown 4 metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 rounded-xl bg-[#161A20] border border-[#262C36]">
              <span className="text-[10px] text-slate-400 block font-medium">Impact Metrics</span>
              <span className="text-base font-bold text-white font-mono">{Math.round(score.ats_analysis.sub_scores?.impact_metrics || 0)}%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{score.ats_analysis.metric_count} detected</span>
            </div>
            <div className="p-3 rounded-xl bg-[#161A20] border border-[#262C36]">
              <span className="text-[10px] text-slate-400 block font-medium">Action Verbs</span>
              <span className="text-base font-bold text-white font-mono">{Math.round(score.ats_analysis.sub_scores?.action_verbs || 0)}%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{score.ats_analysis.action_verbs_count} unique</span>
            </div>
            <div className="p-3 rounded-xl bg-[#161A20] border border-[#262C36]">
              <span className="text-[10px] text-slate-400 block font-medium">Section Completeness</span>
              <span className="text-base font-bold text-white font-mono">{Math.round(score.ats_analysis.sub_scores?.structure_completeness || 0)}%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">ATS Standard</span>
            </div>
            <div className="p-3 rounded-xl bg-[#161A20] border border-[#262C36]">
              <span className="text-[10px] text-slate-400 block font-medium">Length & Format</span>
              <span className="text-base font-bold text-white font-mono">{Math.round(score.ats_analysis.sub_scores?.formatting_health || 0)}%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{score.ats_analysis.word_count} words</span>
            </div>
          </div>

          {/* Diagnostic checks & Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
            {/* Passed Checks */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#161A20]/60 border border-[#262C36]">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#262C36]">
                <span className="font-bold text-emerald-400 uppercase tracking-wider text-[10px]">
                  ATS Passed Diagnostics ({score.ats_analysis.passed_checks?.length || 0})
                </span>
                <span className="text-[10px] font-semibold text-emerald-400 font-mono">PASSED</span>
              </div>
              <ul className="space-y-1.5 pt-1">
                {score.ats_analysis.passed_checks?.map((check, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-sm bg-emerald-400 mt-1.5 flex-shrink-0"></span>
                    <span>{check}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Improvement Recommendations */}
            <div className="space-y-2 p-3.5 rounded-xl bg-[#161A20]/60 border border-[#262C36]">
              <div className="flex items-center justify-between pb-1.5 border-b border-[#262C36]">
                <span className="font-bold text-amber-400 uppercase tracking-wider text-[10px]">
                  Optimization Recommendations ({score.ats_analysis.improvement_tips?.length || 0})
                </span>
                <span className="text-[10px] font-semibold text-amber-400 font-mono">TIPS</span>
              </div>
              {score.ats_analysis.improvement_tips?.length > 0 ? (
                <ul className="space-y-1.5 pt-1">
                  {score.ats_analysis.improvement_tips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-300">
                      <span className="w-1.5 h-1.5 rounded-sm bg-amber-400 mt-1.5 flex-shrink-0"></span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[11px] text-slate-500 italic py-1">No major ATS optimizations needed. Excellent structure.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Engineering Signal Cards: Deep GitHub + LeetCode */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Deep GitHub Audit Card */}
        <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-5 text-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 pb-2.5 border-b border-[#1F242D]">
              <div className="flex items-center gap-2">
                <span className="font-bold uppercase tracking-wider text-white">GitHub Code Authenticity</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                  Anti-Fork Audit
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[11px] bg-[#161A20] text-slate-300 font-mono border border-[#262C36]">
                {githubUser ? `@${githubUser}` : 'Not provided'}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2.5 mb-3.5 text-center">
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block">Original Repos</span>
                <span className="text-base font-bold text-white font-mono">
                  {githubData.original_repos?.length || (githubData.repositories?.length ? githubData.repositories.length : 0)}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block">Total Stars</span>
                <span className="text-base font-bold text-white font-mono">
                  {githubData.total_stars || 0}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block">Recent Active</span>
                <span className="text-base font-bold text-white font-mono">
                  {githubData.recent_active_repos?.length || (githubData.repositories?.length ? Math.min(githubData.repositories.length, 3) : 0)}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between pb-1.5 border-b border-[#1F242D] text-slate-400">
                <span>Forked / Template Repos</span>
                <span className="font-semibold text-slate-200 font-mono">{githubData.forked_repos?.length || 0} filtered</span>
              </div>
              <div className="flex justify-between pb-1.5 border-b border-[#1F242D] text-slate-400">
                <span>Authored Contributions</span>
                <span className="font-semibold text-slate-200 font-mono">{githubData.contributions || 0}+ commits</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1 font-medium">Authored Languages</span>
                <div className="flex flex-wrap gap-1.5">
                  {githubData.languages && githubData.languages.length > 0 ? (
                    githubData.languages.map((lang, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#161A20] text-slate-200 border border-[#262C36]">
                        {lang}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-500 italic text-[11px]">No language records</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* LeetCode Problem-Solving Card */}
        <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-5 text-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 pb-2.5 border-b border-[#1F242D]">
              <div className="flex items-center gap-2">
                <span className="font-bold uppercase tracking-wider text-white">LeetCode Problem Solving</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                  DSA Proof
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[11px] bg-[#161A20] text-slate-300 font-mono border border-[#262C36]">
                {leetcodeUser ? `@${leetcodeUser}` : 'Not provided'}
              </span>
            </div>

            {leetcodeUser ? (
              <>
                <div className="grid grid-cols-4 gap-2 mb-3.5 text-center">
                  <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                    <span className="text-[10px] text-slate-400 block">Total</span>
                    <span className="text-sm font-bold text-white font-mono">{leetcodeData.total_solved || 0}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                    <span className="text-[10px] text-emerald-400 block">Easy</span>
                    <span className="text-sm font-bold text-emerald-400 font-mono">{leetcodeData.easy_solved || 0}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                    <span className="text-[10px] text-amber-400 block">Med</span>
                    <span className="text-sm font-bold text-amber-400 font-mono">{leetcodeData.medium_solved || 0}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                    <span className="text-[10px] text-red-400 block">Hard</span>
                    <span className="text-sm font-bold text-red-400 font-mono">{leetcodeData.hard_solved || 0}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between pb-1.5 border-b border-[#1F242D] text-slate-400">
                    <span>Global Ranking</span>
                    <span className="font-semibold text-slate-200 font-mono">
                      {leetcodeData.global_ranking ? `#${leetcodeData.global_ranking.toLocaleString()}` : 'Top Tier'}
                    </span>
                  </div>
                  <div className="flex justify-between pb-1.5 border-b border-[#1F242D] text-slate-400">
                    <span>Contest Rating</span>
                    <span className="font-semibold text-slate-200 font-mono">
                      {leetcodeData.contest_rating ? `${leetcodeData.contest_rating} pts` : 'Unrated'}
                    </span>
                  </div>
                  {leetcodeData.languages_solved && leetcodeData.languages_solved.length > 0 && (
                    <div className="pt-1">
                      <span className="text-slate-400 block mb-1 font-medium">Solved Problem Languages</span>
                      <div className="flex flex-wrap gap-1.5">
                        {leetcodeData.languages_solved.map((l, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#161A20] text-emerald-400 border border-emerald-500/20 font-mono">
                            {l.language} ({l.problems_solved})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {leetcodeData.badges && leetcodeData.badges.length > 0 && (
                    <div>
                      <span className="text-slate-400 block mb-1 font-medium">Earned Badges</span>
                      <div className="flex flex-wrap gap-1.5">
                        {leetcodeData.badges.map((b, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#161A20] text-slate-200 border border-[#262C36]">
                            {b}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-6 text-center text-slate-500">
                <span className="text-xs mb-1 text-slate-400">No LeetCode profile discovered in resume.</span>
                <span className="text-[11px] text-slate-500">Problem-solving score dynamically normalized across GitHub and project evidence.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 1. TECHNICAL SKILLS BREAKDOWN (Independent Section) */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 space-y-5">
        <div className="flex items-center justify-between pb-3.5 border-b border-[#1F242D]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Technical Skills Breakdown
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Programming languages, frameworks, and developer tools verified against public GitHub code and LeetCode solved problems.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-[#161A20] font-bold text-slate-200 border border-[#262C36] font-mono">
            {verifiedSkills.length} / {verifiedSkills.length + unverifiedSkills.length} Verified
          </span>
        </div>

        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
            Verified Technical Skills ({verifiedSkills.length})
          </h4>
          {verifiedSkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {verifiedSkills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                >
                  <span className="w-1.5 h-1.5 rounded-sm bg-emerald-400 flex-shrink-0"></span>
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No verified technical skills discovered in public code repositories.</p>
          )}
        </div>

        <div className="pt-4 border-t border-[#1F242D]">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
            Unverified Technical Skills ({unverifiedSkills.length})
          </h4>
          {unverifiedSkills.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {unverifiedSkills.map((skill, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400 bg-[#161A20] border border-[#262C36]"
                >
                  <span className="w-1.5 h-1.5 rounded-sm bg-slate-600 flex-shrink-0"></span>
                  {skill}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500">All claimed technical skills were corroborated by repository code.</p>
          )}
        </div>
      </div>

      {/* 2. PROJECTS & CODEBASE EVIDENCE (Independent Section) */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 space-y-5">
        <div className="flex items-center justify-between pb-3.5 border-b border-[#1F242D]">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Projects & Codebase Evidence
            </h3>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Genuine software engineering projects cross-referenced with candidate's original GitHub repositories.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-[#161A20] font-bold text-slate-200 border border-[#262C36] font-mono">
            {verifiedProjects.length} / {verifiedProjects.length + unverifiedProjects.length} Matched
          </span>
        </div>

        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
            Verified Projects ({verifiedProjects.length})
          </h4>
          {verifiedProjects.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {verifiedProjects.map((project, idx) => {
                const pName = typeof project === 'string' ? project : project.name || 'Project';
                const resumeProj = (resumeData?.projects || []).find(p => (p.name || '').toLowerCase() === pName.toLowerCase());
                const desc = resumeProj?.description || 'Repository codebase match confirmed on GitHub';

                return (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-[#161A20] border border-[#262C36] flex flex-col justify-between text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{pName}</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        VERIFIED REPO
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px] leading-relaxed">{desc}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No project repositories verified on candidate GitHub.</p>
          )}
        </div>

        {unverifiedProjects.length > 0 && (
          <div className="pt-4 border-t border-[#1F242D]">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Unverified Projects ({unverifiedProjects.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {unverifiedProjects.map((project, idx) => {
                const pName = typeof project === 'string' ? project : project.name || 'Project';
                const resumeProj = (resumeData?.projects || []).find(p => (p.name || '').toLowerCase() === pName.toLowerCase());
                const desc = resumeProj?.description || 'No matching public repository discovered on GitHub';

                return (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-[#161A20]/60 border border-[#262C36] flex flex-col justify-between text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-300 text-sm">{pName}</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] text-slate-500 bg-[#111418] border border-[#262C36] font-mono">
                        NO REPO FOUND
                      </span>
                    </div>
                    <p className="text-slate-500 text-[11px] leading-relaxed">{desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 3. SELF-REPORTED CANDIDATE SKILLS (Independent Section) */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3.5 border-b border-[#1F242D]">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Self-Reported Candidate Skills
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#161A20] text-slate-300 font-semibold border border-[#262C36]">
                Not Scored Against Code Repos
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Interpersonal, leadership, and domain capabilities extracted for hiring context. These do not penalize the Reality Score.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded bg-[#161A20] text-slate-300 border border-[#262C36] font-mono">
            {softSkills.length} Skills Listed
          </span>
        </div>

        {softSkills.length > 0 ? (
          <div className="flex flex-wrap gap-2 pt-1">
            {softSkills.map((skill, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-200 bg-[#161A20] border border-[#262C36] shadow-subtle"
              >
                <span className="w-1.5 h-1.5 rounded-sm bg-slate-500 flex-shrink-0"></span>
                {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic py-1">No self-reported soft skills were listed on the resume.</p>
        )}
      </div>

      {/* Automated Candidate Routing & Invitation */}
      <SendInvitationModule scoreData={score} />

      {/* Next Steps & Workflow Navigation Card */}
      <div className="bg-[#111418] rounded-xl border border-[#1F242D] shadow-card p-6 sm:p-8 mt-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
              Next Recommended Step
            </span>
            <h3 className="text-base font-bold text-white">
              Optimize & Export Candidate Resume in Live ATS Editor
            </h3>
            <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
              Open the parsed resume text directly in the exact-layout editor to insert verified impact metrics, strengthen weak action verbs, and generate an ATS-formatted Microsoft Word (.docx) document.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 flex-shrink-0">
            <Link
              to={`/editor/${resumeId}`}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold bg-white hover:bg-slate-200 text-[#090A0C] transition-all shadow-sm active:scale-[0.98] focus:ring-2 focus:ring-white focus:outline-none"
            >
              <span>Open in Live ATS Editor</span>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>

            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-300 border border-[#262C36] transition-all focus:ring-2 focus:ring-white focus:outline-none"
            >
              Audit Another Resume
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
import React from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';

function WorkflowStepper({ activeResumeId: propResumeId, candidateName }) {
  const location = useLocation();
  const params = useParams();
  
  const resumeId = propResumeId || params.resumeId || sessionStorage.getItem('profileauditor_last_resume_id');
  const pathname = location.pathname;

  const isUpload = pathname === '/upload';
  const isResults = pathname.startsWith('/results');
  const isEditor = pathname.startsWith('/editor');

  const isWorkflowRoute = isUpload || isResults || isEditor;
  if (!isWorkflowRoute) return null;

  const getStepStatus = (stepIndex) => {
    if (stepIndex === 1) {
      if (isUpload) return 'current';
      if (isResults || isEditor || resumeId) return 'completed';
      return 'upcoming';
    }
    if (stepIndex === 2) {
      if (isResults) return 'current';
      if (isEditor) return 'completed';
      if (resumeId) return 'accessible';
      return 'disabled';
    }
    if (stepIndex === 3) {
      if (isEditor) return 'current';
      if (resumeId) return 'accessible';
      return 'accessible';
    }
    return 'upcoming';
  };

  const steps = [
    {
      id: 1,
      title: '1. Ingest Resume',
      desc: 'PDF / DOCX parsing',
      to: '/upload',
      status: getStepStatus(1),
    },
    {
      id: 2,
      title: '2. Footprint Audit',
      desc: 'Code reality verification',
      to: resumeId ? `/results/${resumeId}` : '/upload',
      status: getStepStatus(2),
    },
    {
      id: 3,
      title: '3. Live ATS Editor',
      desc: 'Word export & optimization',
      to: resumeId ? `/editor/${resumeId}` : '/editor',
      status: getStepStatus(3),
    },
  ];

  return (
    <div className="w-full mb-6" role="navigation" aria-label="Resume Audit Pipeline">
      <div className="bg-[#111418] border border-[#1F242D] rounded-xl p-3 sm:p-4 shadow-sm">
        {/* Breadcrumb / Session Meta */}
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-[#1F242D] text-xs">
          <nav className="flex items-center gap-1.5 text-slate-400 font-medium" aria-label="Breadcrumb">
            <Link to="/" className="hover:text-white transition-colors focus:ring-2 focus:ring-white rounded px-1">
              Dashboard
            </Link>
            <span className="text-slate-600">/</span>
            <span className="text-white font-semibold">
              {isUpload && 'Upload & Parse Document'}
              {isResults && `Verification Report (${candidateName ? candidateName : resumeId ? `AUD-${resumeId.slice(0, 8)}` : 'Active'})`}
              {isEditor && `Live ATS Document Editor (${resumeId ? `AUD-${resumeId.slice(0, 8)}` : 'Sample Mode'})`}
            </span>
          </nav>

          {resumeId && (
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-slate-400 bg-[#161A20] px-2.5 py-0.5 rounded border border-[#262C36]">
                ID: AUD-{resumeId.slice(0, 8)}
              </span>
              <Link
                to="/upload"
                className="text-[11px] text-slate-300 hover:text-white underline underline-offset-2 transition-colors focus:ring-2 focus:ring-white rounded"
              >
                Switch Resume
              </Link>
            </div>
          )}
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
          {steps.map((step) => {
            const isCurrent = step.status === 'current';
            const isCompleted = step.status === 'completed';
            const isDisabled = step.status === 'disabled';

            const cardClasses = `flex items-center gap-3 p-2.5 sm:p-3 rounded-lg border transition-all text-left ${
              isCurrent
                ? 'bg-[#161A20] border-white text-white shadow-sm'
                : isCompleted || step.status === 'accessible'
                ? 'bg-[#111418] border-[#262C36] text-slate-300 hover:bg-[#161A20] hover:border-slate-400 hover:text-white cursor-pointer'
                : 'bg-[#0E1013] border-[#1A1F26] text-slate-600 opacity-60 cursor-not-allowed'
            }`;

            const content = (
              <>
                <div
                  className={`w-7 h-7 rounded-md flex items-center justify-center font-bold text-xs flex-shrink-0 transition-colors ${
                    isCurrent
                      ? 'bg-white text-[#090A0C]'
                      : isCompleted
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-[#161A20] text-slate-400 border border-[#262C36]'
                  }`}
                >
                  {isCompleted ? (
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    step.id
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className={`text-xs font-semibold truncate ${isCurrent ? 'text-white' : 'text-slate-200'}`}>
                      {step.title}
                    </p>
                    {isCurrent && (
                      <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-white text-[#090A0C] font-bold">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-500 truncate">{step.desc}</p>
                </div>
              </>
            );

            if (isDisabled) {
              return (
                <div key={step.id} className={cardClasses} aria-disabled="true">
                  {content}
                </div>
              );
            }

            return (
              <Link
                key={step.id}
                to={step.to}
                className={cardClasses}
                aria-current={isCurrent ? 'step' : undefined}
              >
                {content}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default WorkflowStepper;

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import WorkflowStepper from '../components/WorkflowStepper';

const DEFAULT_SAMPLE_RESUME = `ALEX CHEN
San Francisco, CA • alex.chen@email.com • (555) 019-2834
GitHub: github.com/alexchen-dev • LeetCode: leetcode.com/u/alexchen_code

SUMMARY
Senior Full-Stack Engineer with 5+ years of experience building scalable distributed cloud architectures, high-performance web applications, and resilient microservices.

TECHNICAL SKILLS
• Languages: TypeScript, JavaScript, Python, Go, SQL, HTML, CSS
• Frameworks & Libraries: React, Node.js, Next.js, FastAPI, Tailwind CSS, Express
• Infrastructure & Tools: Docker, Kubernetes, PostgreSQL, Redis, AWS, Git, GitHub

WORK EXPERIENCE
Senior Full-Stack Engineer | ScaleTech Cloud
Jan 2022 - Present | San Francisco, CA
• Architected distributed edge routing system handling 15M+ daily requests, reducing p99 latency by 38%.
• Optimized PostgreSQL query performance and caching strategies with Redis, cutting database load by 45%.
• Automated end-to-end CI/CD deployment pipelines using Docker and GitHub Actions across 12 microservices.
• Led and mentored a squad of 6 engineers, driving 100% test coverage standards and weekly code reviews.

Full-Stack Developer | InnovateLabs
June 2019 - Dec 2021 | Austin, TX
• Engineered responsive web applications with React and Next.js, improving mobile conversion rate by 24%.
• Designed RESTful microservices in Node.js and Go for payment processing handling $4.5M in monthly transactions.
• Spearheaded migration from legacy monolithic architecture to containerized services on AWS ECS.

PROJECTS
CloudMesh - High-Throughput Edge Routing Mesh
• Built an asynchronous traffic controller in Go and Docker featuring real-time telemetry and circuit breaking.
• Deployed canary routing algorithms supporting 50k concurrent WebSocket connections with sub-10ms overhead.

DataPulse - Real-Time Analytics Dashboard
• Developed high-speed analytics platform using React, FastAPI, and PostgreSQL with live WebSocket feeds.
• Integrated dynamic charting dashboards visualizing 500k telemetry events per minute.

EDUCATION
B.S. in Computer Science | University of California, Berkeley
GPA: 3.8 / 4.0 | Graduated 2019`;

const ACTION_VERBS = [
  'Architected', 'Optimized', 'Automated', 'Scaled', 'Engineered',
  'Spearheaded', 'Streamlined', 'Refactored', 'Designed', 'Implemented',
  'Deployed', 'Led', 'Integrated', 'Built', 'Accelerated'
];

const METRIC_SNIPPETS = [
  '• Reduced API latency by 35% across 10M daily requests.',
  '• Scaled microservices architecture to support 50k concurrent users.',
  '• Automated CI/CD pipelines, cutting deployment cycle times by 60%.',
  '• Optimized database queries, reducing infrastructure costs by $15,000/year.'
];

const SECTION_TEMPLATES = {
  'WORK EXPERIENCE': '\n\nWORK EXPERIENCE\n[Role Title] | [Company Name]\n[Month Year] - [Month Year] | [Location]\n• [Action Verb] [Task/System], resulting in [Quantifiable Metric % or $].\n• [Action Verb] [Feature/Architecture], scaling to [Metric Count/Volume].',
  'PROJECTS': '\n\nPROJECTS\n[Project Name] - [One-line summary]\n• Built [System/Application] using [Technologies], achieving [Performance Metric].\n• Implemented [Key Feature], supporting [Scale/Throughput].',
  'TECHNICAL SKILLS': '\n\nTECHNICAL SKILLS\n• Languages: [e.g. Python, Go, TypeScript, SQL]\n• Frameworks: [e.g. React, FastAPI, Docker, PostgreSQL]\n• Tools: [e.g. Git, Kubernetes, Redis, AWS]'
};

// Format raw text into clean, exact-layout HTML preserving line breaks and original hierarchy
const textToExactHtml = (rawText) => {
  if (!rawText) return '<div class="text-slate-400 italic">Click to start editing...</div>';

  const lines = rawText.split('\n');
  const blocks = [];
  const sectionHeaders = [
    'summary', 'professional summary', 'technical skills', 'skills',
    'work experience', 'experience', 'employment history', 'projects',
    'key projects', 'education', 'certifications', 'awards', 'leadership'
  ];

  let firstLine = true;

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const stripped = rawLine.trim();

    if (!stripped) {
      blocks.push('<div class="h-2.5"></div>');
      continue;
    }

    const cleanLower = stripped.toLowerCase().replace(/[:-]/g, '').trim();

    // First line: Candidate Name (clean, large uppercase)
    if (firstLine) {
      blocks.push(`<div class="text-xl sm:text-2xl font-extrabold text-center uppercase tracking-wide text-slate-900 mb-0.5">${stripped}</div>`);
      firstLine = false;
      continue;
    }

    // Contact line
    if ((stripped.includes('@') || stripped.includes('github') || stripped.includes('leetcode') || stripped.includes('•') || stripped.includes('|')) && blocks.length <= 3) {
      blocks.push(`<div class="text-xs text-center text-slate-600 mb-3 pb-2 border-b border-slate-300 tracking-normal">${stripped}</div>`);
      continue;
    }

    // Section Header
    if (sectionHeaders.includes(cleanLower) || (stripped.length < 35 && stripped === stripped.toUpperCase() && !stripped.startsWith('•') && !stripped.startsWith('-'))) {
      blocks.push(`
        <div class="mt-4 mb-2 pb-0.5 border-b-[1.5px] border-slate-900">
          <div class="text-xs font-bold uppercase tracking-wider text-slate-900">${stripped}</div>
        </div>
      `);
      continue;
    }

    // Bullet point line
    if (stripped.startsWith('•') || stripped.startsWith('-') || stripped.startsWith('*') || stripped.startsWith('+')) {
      const bulletText = stripped.replace(/^[•\-*+]\s*/, '');
      blocks.push(`
        <div class="flex items-baseline text-xs text-slate-800 leading-relaxed mb-1 pl-3">
          <span class="mr-2 font-bold select-none text-slate-900">•</span>
          <span>${bulletText}</span>
        </div>
      `);
      continue;
    }

    // Role / Project Row with dates / company
    if (stripped.includes('|') || stripped.includes('-')) {
      blocks.push(`<div class="text-xs font-bold text-slate-900 mt-2 mb-0.5">${stripped}</div>`);
    } else {
      blocks.push(`<div class="text-xs text-slate-800 leading-relaxed mb-1">${stripped}</div>`);
    }
  }

  return blocks.join('\n');
};

function ResumeEditorPage() {
  const { resumeId } = useParams();
  
  const [resumeText, setResumeText] = useState(DEFAULT_SAMPLE_RESUME);
  const [resumeHtml, setResumeHtml] = useState(textToExactHtml(DEFAULT_SAMPLE_RESUME));
  const [activeDocumentName, setActiveDocumentName] = useState(resumeId ? `Audit Resume (AUD-${resumeId.slice(0, 8)})` : 'Alex Chen - Senior Full-Stack Engineer');
  const [documentType, setDocumentType] = useState('text'); // 'text', 'pdf', 'docx'
  const [editorMode, setEditorMode] = useState('visual'); // 'visual' or 'source'
  const [fontFamily, setFontFamily] = useState('sans'); // 'sans', 'serif', 'mono'
  const [zoomLevel, setZoomLevel] = useState(100); // 75, 90, 100, 110, 125
  const [targetJd, setTargetJd] = useState('');
  const [showJdInput, setShowJdInput] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [copied, setCopied] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  
  const debounceTimerRef = useRef(null);
  const fileInputRef = useRef(null);
  const paperRef = useRef(null);

  // Evaluate ATS in real time
  const evaluateLiveAts = useCallback(async (text, jd) => {
    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE_URL}/api/score/live-ats`, {
        resume_text: text,
        job_description: jd || null
      });
      setAnalysis(res.data);
    } catch (err) {
      console.error('Live ATS evaluation error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch initial resume if resumeId provided
  useEffect(() => {
    if (resumeId) {
      const fetchInitial = async () => {
        try {
          const res = await axios.get(`${API_BASE_URL}/api/resume/${resumeId}`);
          if (res.data && res.data.raw_text) {
            setResumeText(res.data.raw_text);
            setResumeHtml(textToExactHtml(res.data.raw_text));
            setDocumentType('text');
            setActiveDocumentName(`Audit Resume (AUD-${resumeId.slice(0, 8)})`);
            if (res.data.job_description) {
              setTargetJd(res.data.job_description);
              setShowJdInput(true);
            }
          }
        } catch (e) {
          console.log('Using default sample resume text');
        }
      };
      fetchInitial();
    }
  }, [resumeId]);

  // Sync contentEditable innerText with resumeText when visual paper changes
  const handlePaperInput = () => {
    if (paperRef.current) {
      const text = paperRef.current.innerText || '';
      setResumeText(text);
    }
  };

  // Real-time debounced evaluation
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      evaluateLiveAts(resumeText, targetJd);
    }, 250);

    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, [resumeText, targetJd, evaluateLiveAts]);

  // Convert PDF or Word Document into structured editable document preserving exact original layout
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const filename = file.name.toLowerCase();
    if (!filename.endsWith('.pdf') && !filename.endsWith('.docx')) {
      setUploadError('Please select a valid PDF or Word (.docx) document.');
      return;
    }

    try {
      setUploadingDoc(true);
      setUploadError('');

      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post(`${API_BASE_URL}/api/resume/convert-pdf-to-doc`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data?.raw_text) {
        setResumeText(res.data.raw_text);
        const htmlToUse = res.data.exact_html || res.data.rich_html || textToExactHtml(res.data.raw_text);
        setResumeHtml(htmlToUse);
        setDocumentType(res.data.document_type || (filename.endsWith('.pdf') ? 'pdf' : 'docx'));
        setActiveDocumentName(file.name.replace(/\.[^/.]+$/, ''));
      }
    } catch (err) {
      console.error('Error converting document:', err);
      setUploadError(err.response?.data?.detail || 'Failed to convert document. Please try again.');
    } finally {
      setUploadingDoc(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Export as authentic Microsoft Word (.docx) file
  const handleExportDocx = async () => {
    try {
      setExportingDocx(true);
      const res = await axios.post(
        `${API_BASE_URL}/api/resume/export-docx`,
        {
          raw_text: resumeText,
          document_name: activeDocumentName
        },
        { responseType: 'blob' }
      );

      const blob = new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${activeDocumentName.replace(/[^a-zA-Z0-9_-]/g, '_')}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('DOCX export error:', err);
      alert('Failed to export Word document. Please try again.');
    } finally {
      setExportingDocx(false);
    }
  };

  // Insert helper
  const insertText = (insertion) => {
    const updated = resumeText + '\n' + insertion;
    setResumeText(updated);
    setResumeHtml(textToExactHtml(updated));
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(resumeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleLoadSample = () => {
    setResumeText(DEFAULT_SAMPLE_RESUME);
    setResumeHtml(textToExactHtml(DEFAULT_SAMPLE_RESUME));
    setDocumentType('text');
    setActiveDocumentName('Alex Chen - Senior Full-Stack Engineer');
    setUploadError('');
  };

  const handleClear = () => {
    setResumeText('');
    setResumeHtml('<div class="text-slate-400 italic">Click here to start editing your resume...</div>');
    setDocumentType('text');
    setActiveDocumentName('Untitled Resume');
  };

  const atsScore = analysis?.ats_score ? Math.round(analysis.ats_score) : 0;
  const atsData = analysis?.ats_analysis || {};
  const wordCount = resumeText.trim().split(/\s+/).filter(Boolean).length;
  const lineCount = resumeText.split('\n').filter(Boolean).length;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10B981'; // Emerald
    if (score >= 60) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
  };

  const getFontClass = () => {
    if (fontFamily === 'serif') return 'font-serif';
    if (fontFamily === 'mono') return 'font-mono';
    return 'font-sans';
  };

  return (
    <div className="w-full max-w-[1700px] mx-auto space-y-6 pt-2 pb-16 px-3 sm:px-6">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx"
        className="hidden"
      />

      {/* Interactive Workflow Pipeline Navigation */}
      <WorkflowStepper activeResumeId={resumeId} candidateName={activeDocumentName} />

      {/* Top Header Command Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#111418] p-5 rounded-xl border border-[#1F242D] shadow-card">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Exact-Layout Resume Document Editor</h1>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold font-mono flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-sm ${loading ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`} />
              <span>{loading ? 'Evaluating...' : 'Live Real-Time ATS'}</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Preserves the exact layout, font hierarchy, and design of your original resume with in-place editing and real-time ATS optimization.
          </p>
        </div>

        {/* Global Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadingDoc}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white hover:bg-slate-200 text-[#090A0C] transition-all shadow-sm active:scale-[0.98] disabled:opacity-50"
          >
            {uploadingDoc ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-[#090A0C]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Extracting Exact Layout...</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <span>Upload PDF / Word</span>
              </>
            )}
          </button>

          <button
            onClick={handleExportDocx}
            disabled={exportingDocx}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-sm active:scale-[0.98] disabled:opacity-50"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>{exportingDocx ? 'Generating Word...' : 'Download Word (.docx)'}</span>
          </button>

          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-200 border border-[#262C36] transition-all"
          >
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <span>Print / PDF</span>
          </button>

          <button
            onClick={handleCopy}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-200 border border-[#262C36] transition-all"
          >
            {copied ? 'Copied' : 'Copy Text'}
          </button>

          {resumeId ? (
            <Link
              to={`/results/${resumeId}`}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-[#161A20] hover:bg-[#1E232B] text-slate-200 border border-[#262C36] transition-all focus:ring-2 focus:ring-white focus:outline-none"
            >
              <span>View Footprint Audit</span>
              <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          ) : (
            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-[#161A20] hover:bg-[#1E232B] text-slate-200 border border-[#262C36] transition-all focus:ring-2 focus:ring-white focus:outline-none"
            >
              <span>Audit a Resume</span>
            </Link>
          )}
        </div>
      </div>

      {/* Editor Customizer & Ribbon Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[#111418] px-4 py-3 rounded-xl border border-[#1F242D] text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* View Mode Switcher */}
          <div className="flex items-center bg-[#161A20] p-0.5 rounded-lg border border-[#262C36]">
            <button
              type="button"
              onClick={() => setEditorMode('visual')}
              className={`px-3 py-1 rounded-md font-medium transition-all ${
                editorMode === 'visual'
                  ? 'bg-white text-[#090A0C] font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Exact Resume View
            </button>
            <button
              type="button"
              onClick={() => setEditorMode('source')}
              className={`px-3 py-1 rounded-md font-medium transition-all ${
                editorMode === 'source'
                  ? 'bg-white text-[#090A0C] font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Raw Text
            </button>
          </div>

          {/* Typography Selector */}
          <div className="flex items-center gap-1.5 text-slate-400">
            <span>Font:</span>
            <select
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
              className="bg-[#161A20] text-slate-200 border border-[#262C36] rounded-md px-2 py-1 text-xs focus:outline-none"
            >
              <option value="sans">Original Sans (Inter/Calibri)</option>
              <option value="serif">Original Serif (Garamond/Times)</option>
              <option value="mono">Clean Monospace</option>
            </select>
          </div>

          {/* Canvas Zoom Controls */}
          <div className="flex items-center gap-1 bg-[#161A20] px-2 py-0.5 rounded-lg border border-[#262C36] text-slate-300">
            <span className="text-[11px] text-slate-400 font-medium mr-1">Zoom:</span>
            <button
              type="button"
              onClick={() => setZoomLevel(prev => Math.max(60, prev - 10))}
              className="px-1.5 py-0.5 rounded hover:bg-[#262C36] text-slate-300 hover:text-white font-bold"
              title="Zoom Out"
            >
              -
            </button>
            <span className="text-[11px] font-mono px-1 min-w-[38px] text-center font-semibold text-white">
              {zoomLevel}%
            </span>
            <button
              type="button"
              onClick={() => setZoomLevel(prev => Math.min(150, prev + 10))}
              className="px-1.5 py-0.5 rounded hover:bg-[#262C36] text-slate-300 hover:text-white font-bold"
              title="Zoom In"
            >
              +
            </button>
            <button
              type="button"
              onClick={() => setZoomLevel(100)}
              className="text-[10px] text-slate-400 hover:text-white ml-1 underline underline-offset-2"
              title="Reset Zoom to 100%"
            >
              100%
            </button>
          </div>

          {/* Action Verbs Menu */}
          <div className="relative inline-block text-left group">
            <button
              type="button"
              className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-200 border border-[#262C36] transition-all flex items-center gap-1"
            >
              <span>+ Action Verb</span>
              <svg className="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div className="hidden group-hover:grid grid-cols-3 gap-1 absolute z-30 left-0 mt-1 w-64 p-2 bg-[#161A20] border border-[#262C36] rounded-lg shadow-xl">
              {ACTION_VERBS.map((verb, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => insertText(`• ${verb} `)}
                  className="text-left text-[11px] px-2 py-1 rounded hover:bg-[#1F242D] text-slate-300 hover:text-white transition-colors"
                >
                  {verb}
                </button>
              ))}
            </div>
          </div>

          {/* Metric Templates */}
          {METRIC_SNIPPETS.slice(0, 2).map((snip, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => insertText(snip)}
              className="px-2 py-1 rounded-md text-[10px] font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-300 hover:text-white border border-[#262C36] transition-all hidden sm:inline-block"
            >
              + Metric {idx + 1}
            </button>
          ))}
        </div>

        {/* Action Controls & Counters */}
        <div className="flex items-center gap-3 text-[11px]">
          <span className="text-slate-400 font-mono">
            {wordCount} words • {lineCount} lines
          </span>
          <span className="text-slate-600">•</span>
          <button
            onClick={() => setShowJdInput(!showJdInput)}
            className="text-emerald-400 hover:text-emerald-300 font-medium underline underline-offset-2"
          >
            {showJdInput ? 'Hide JD' : 'Target Job Description'}
          </button>
          <span className="text-slate-600">•</span>
          <button
            onClick={handleLoadSample}
            className="text-slate-400 hover:text-white underline underline-offset-2"
          >
            Sample
          </button>
          <span className="text-slate-600">•</span>
          <button
            onClick={handleClear}
            className="text-red-400 hover:text-red-300 underline underline-offset-2"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Upload Error Notice */}
      {uploadError && (
        <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center justify-between">
          <span>{uploadError}</span>
          <button onClick={() => setUploadError('')} className="text-red-400 hover:text-white font-bold ml-2">Dismiss</button>
        </div>
      )}

      {/* Optional Target JD Box */}
      {showJdInput && (
        <div className="p-4 rounded-xl bg-[#111418] border border-[#1F242D] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Target Job Description / Tech Stack Match
            </span>
            {analysis?.role_analysis && (
              <span className="text-xs font-mono font-bold text-emerald-400">
                JD Fit Match: {analysis.role_analysis.role_fit_score}%
              </span>
            )}
          </div>
          <textarea
            rows={2}
            value={targetJd}
            onChange={(e) => setTargetJd(e.target.value)}
            placeholder="Paste Job Description requirements (e.g. Go, Kubernetes, PostgreSQL, Docker, Redis)..."
            className="w-full text-xs p-3 rounded-lg bg-[#161A20] text-white border border-[#262C36] focus:outline-none focus:border-white placeholder-slate-600"
          />
        </div>
      )}

      {/* Main Workspace Split */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Authentic Exact Layout Document Canvas */}
        <div className="xl:col-span-8 space-y-3">
          {editorMode === 'visual' ? (
            /* Visual Exact Resume Paper Sheet */
            <div className="bg-[#0B0E14] p-4 sm:p-8 rounded-2xl border border-[#1F242D] shadow-2xl flex justify-center overflow-x-auto">
              <div
                style={{
                  transform: zoomLevel !== 100 ? `scale(${zoomLevel / 100})` : 'none',
                  transformOrigin: 'top center',
                  transition: 'transform 0.15s ease-out'
                }}
                className={`w-fit min-w-[800px] max-w-none min-h-[980px] bg-white text-slate-900 shadow-2xl rounded-sm ${
                  documentType === 'pdf' ? 'p-0 overflow-visible' : 'p-8 sm:p-12 w-full max-w-[860px]'
                } border border-slate-300 ${getFontClass()}`}
              >
                {/* Visual Direct-Edit Content */}
                <div
                  ref={paperRef}
                  contentEditable
                  suppressContentEditableWarning
                  onInput={handlePaperInput}
                  dangerouslySetInnerHTML={{ __html: resumeHtml }}
                  className={`focus:outline-none min-h-[850px] select-text ${documentType === 'pdf' ? '' : 'leading-relaxed'}`}
                />
              </div>
            </div>
          ) : (
            /* Plain Text Mode */
            <div className="bg-[#111418] rounded-xl border border-[#1F242D] p-4 shadow-card">
              <textarea
                rows={30}
                value={resumeText}
                onChange={(e) => {
                  setResumeText(e.target.value);
                  setResumeHtml(textToExactHtml(e.target.value));
                }}
                placeholder="Paste or edit resume text here..."
                className="w-full bg-transparent text-slate-100 font-mono text-xs leading-relaxed focus:outline-none placeholder-slate-600 resize-y"
                spellCheck="false"
              />
            </div>
          )}

          {/* Quick Section Adders Bar */}
          <div className="flex flex-wrap gap-1.5 p-2 bg-[#111418] rounded-xl border border-[#1F242D]">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider py-1 px-2">
              Insert Section:
            </span>
            {Object.keys(SECTION_TEMPLATES).map((sec, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => insertText(SECTION_TEMPLATES[sec])}
                className="px-2.5 py-1 rounded-md text-[10px] font-semibold bg-[#161A20] hover:bg-[#1E232B] text-blue-400 border border-blue-500/20 transition-all"
              >
                + {sec}
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Live Real-Time ATS Score & Diagnostics */}
        <div className="xl:col-span-4 space-y-4 xl:sticky xl:top-6">
          {/* Main Score Radial Meter */}
          <div className="bg-[#111418] p-5 rounded-xl border border-[#1F242D] shadow-card text-center space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-[#1F242D]">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Live ATS Health Score
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-[#161A20] text-slate-300 font-semibold border border-[#262C36]">
                {atsData.health_label || 'Evaluating...'}
              </span>
            </div>

            {/* Radial SVG Gauge */}
            <div className="flex justify-center items-center py-2">
              <div className="relative w-32 h-32">
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
                    stroke={getScoreColor(atsScore)}
                    strokeWidth="8"
                    strokeDasharray={`${2 * Math.PI * 50}`}
                    strokeDashoffset={`${2 * Math.PI * 50 * (1 - atsScore / 100)}`}
                    strokeLinecap="round"
                    className="transition-all duration-300 ease-out"
                  />
                </svg>

                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white leading-none font-mono">
                    {atsScore}
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest mt-1 font-mono">
                    / 100
                  </span>
                </div>
              </div>
            </div>

            {/* Live Sub-Score Grid */}
            <div className="grid grid-cols-2 gap-2 text-left pt-1">
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block font-medium">Impact Metrics</span>
                <span className="text-xs font-bold text-white font-mono">{Math.round(atsData.sub_scores?.impact_metrics || 0)}%</span>
                <span className="text-[10px] text-emerald-400 block">{atsData.metric_count || 0} detected</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block font-medium">Action Verbs</span>
                <span className="text-xs font-bold text-white font-mono">{Math.round(atsData.sub_scores?.action_verbs || 0)}%</span>
                <span className="text-[10px] text-emerald-400 block">{atsData.action_verbs_count || 0} unique</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block font-medium">Structure</span>
                <span className="text-xs font-bold text-white font-mono">{Math.round(atsData.sub_scores?.structure_completeness || 0)}%</span>
                <span className="text-[10px] text-slate-400 block">Completeness</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#161A20] border border-[#262C36]">
                <span className="text-[10px] text-slate-400 block font-medium">Length Balance</span>
                <span className="text-xs font-bold text-white font-mono">{Math.round(atsData.sub_scores?.formatting_health || 0)}%</span>
                <span className="text-[10px] text-slate-400 block">{wordCount} words</span>
              </div>
            </div>
          </div>

          {/* Action Verbs Detected & Suggestions */}
          <div className="bg-[#111418] p-4 rounded-xl border border-[#1F242D] shadow-card space-y-2 text-xs">
            <div className="flex items-center justify-between pb-1.5 border-b border-[#1F242D]">
              <span className="font-bold uppercase tracking-wider text-slate-300 text-[10px]">
                Active Verbs in Document ({atsData.action_verbs?.length || 0})
              </span>
            </div>
            {atsData.action_verbs && atsData.action_verbs.length > 0 ? (
              <div className="flex flex-wrap gap-1 pt-1">
                {atsData.action_verbs.map((v, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] border border-emerald-500/20 font-mono">
                    {v}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[11px] text-slate-500 italic">No strong action verbs detected yet. Try adding 'Architected' or 'Optimized'.</p>
            )}
          </div>

          {/* Real-time Diagnostics & Improvement Tips */}
          <div className="bg-[#111418] p-4 rounded-xl border border-[#1F242D] shadow-card space-y-3 text-xs">
            <div>
              <div className="flex items-center justify-between pb-1.5 border-b border-[#1F242D]">
                <span className="font-bold text-emerald-400 uppercase tracking-wider text-[10px]">
                  Passed Checks ({atsData.passed_checks?.length || 0})
                </span>
                <span className="text-[10px] font-semibold text-emerald-400 font-mono">PASSED</span>
              </div>
              <ul className="space-y-1.5 pt-2">
                {atsData.passed_checks?.map((check, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-300 text-[11px]">
                    <span className="w-1.5 h-1.5 rounded-sm bg-emerald-400 mt-1.5 flex-shrink-0"></span>
                    <span>{check}</span>
                  </li>
                ))}
              </ul>
            </div>

            {atsData.improvement_tips && atsData.improvement_tips.length > 0 && (
              <div className="pt-2 border-t border-[#1F242D]">
                <div className="flex items-center justify-between pb-1.5 border-b border-[#1F242D]">
                  <span className="font-bold text-amber-400 uppercase tracking-wider text-[10px]">
                    Live Suggestions ({atsData.improvement_tips.length})
                  </span>
                  <span className="text-[10px] font-semibold text-amber-400 font-mono">TIPS</span>
                </div>
                <ul className="space-y-1.5 pt-2">
                  {atsData.improvement_tips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-300 text-[11px]">
                      <span className="w-1.5 h-1.5 rounded-sm bg-amber-400 mt-1.5 flex-shrink-0"></span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResumeEditorPage;

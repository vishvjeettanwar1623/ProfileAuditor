import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="max-w-5xl mx-auto space-y-16 sm:space-y-20 pt-4 sm:pt-8">
      {/* Hero section */}
      <section className="text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#161A20] border border-[#262C36] text-xs font-medium text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Automated Engineering Resume Auditing</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-3xl mx-auto leading-[1.12]">
          Verify resume claims against authentic code and DSA proof.
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Upload a developer resume to audit public GitHub codebases, filter out forked templates, inspect commit authorship, and verify LeetCode problem solving.
        </p>

        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            to="/upload"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-white hover:bg-slate-200 text-[#090A0C] font-semibold text-sm transition-all active:scale-[0.98] shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Audit a Resume
          </Link>
          <a
            href="#how-it-works"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-[#161A20] hover:bg-[#1E232B] text-slate-200 font-medium text-sm border border-[#262C36] transition-all"
          >
            How It Works
          </a>
        </div>

        {/* Sample Audit Preview Card */}
        <div className="mt-12 max-w-3xl mx-auto bg-[#111418] rounded-xl border border-[#1F242D] p-6 text-left shadow-card">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#1F242D]">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-white text-[#090A0C] flex items-center justify-center font-bold text-sm">
                AC
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-white text-base">Alex Chen</h3>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#161A20] text-slate-300 font-medium border border-[#262C36]">
                    Senior Full-Stack Engineer
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5 font-mono">github.com/alexchen-dev • leetcode.com/u/alexchen_code</p>
              </div>
            </div>

            <div className="flex items-center gap-3 bg-[#161A20] border border-[#262C36] px-4 py-2 rounded-lg">
              <div className="text-right">
                <p className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">Reality Score</p>
                <p className="text-xl font-bold text-white leading-none font-mono">92<span className="text-xs font-normal text-slate-500">/100</span></p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-5 text-xs">
            <div className="p-3 rounded-lg bg-[#161A20] border border-[#262C36]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">GitHub Audit</span>
              <p className="text-sm font-bold text-white mt-1">16 Original Repos</p>
              <p className="text-[11px] text-slate-500 mt-0.5">430+ authored commits</p>
            </div>

            <div className="p-3 rounded-lg bg-[#161A20] border border-[#262C36]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">LeetCode Proof</span>
              <p className="text-sm font-bold text-white mt-1">248 Solved (128 Med)</p>
              <p className="text-[11px] text-slate-500 mt-0.5">Top 7.4% Contest Rating</p>
            </div>

            <div className="p-3 rounded-lg bg-[#161A20] border border-[#262C36]">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Codebase Match</span>
              <p className="text-sm font-bold text-white mt-1">2 / 2 Projects Verified</p>
              <p className="text-[11px] text-slate-500 mt-0.5">Source repositories matched</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works section */}
      <section id="how-it-works" className="pt-8 border-t border-[#1F242D]">
        <div className="text-center max-w-xl mx-auto mb-10">
          <h2 className="text-2xl font-bold text-white tracking-tight">
            How The Pipeline Works
          </h2>
          <p className="text-sm text-slate-400 mt-2">
            A grounded verification pipeline comparing resume assertions with verifiable public footprints.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-[#111418] p-5 rounded-xl border border-[#1F242D]">
            <div className="w-7 h-7 rounded bg-[#161A20] text-white flex items-center justify-center font-bold text-xs mb-3 border border-[#262C36]">
              1
            </div>
            <h3 className="font-bold text-white text-sm">Resume Extraction</h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Extracts text, contact details, social handles, technical skills, and genuine projects.
            </p>
          </div>

          <div className="bg-[#111418] p-5 rounded-xl border border-[#1F242D]">
            <div className="w-7 h-7 rounded bg-[#161A20] text-white flex items-center justify-center font-bold text-xs mb-3 border border-[#262C36]">
              2
            </div>
            <h3 className="font-bold text-white text-sm">Anti-Fork Code Audit</h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Filters out forked repositories, inspects commit logs, stars, and language byte frequency.
            </p>
          </div>

          <div className="bg-[#111418] p-5 rounded-xl border border-[#1F242D]">
            <div className="w-7 h-7 rounded bg-[#161A20] text-white flex items-center justify-center font-bold text-xs mb-3 border border-[#262C36]">
              3
            </div>
            <h3 className="font-bold text-white text-sm">LeetCode Verification</h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Queries LeetCode GraphQL API for actual solved problem metrics, contest rating, and rank.
            </p>
          </div>

          <div className="bg-[#111418] p-5 rounded-xl border border-[#1F242D]">
            <div className="w-7 h-7 rounded bg-[#161A20] text-white flex items-center justify-center font-bold text-xs mb-3 border border-[#262C36]">
              4
            </div>
            <h3 className="font-bold text-white text-sm">Reality Scoring</h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Calculates an objective Reality Score out of 100 without penalizing self-reported skills.
            </p>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="bg-[#111418] border border-[#1F242D] rounded-2xl p-8 sm:p-10 text-center text-white">
        <h2 className="text-2xl font-bold tracking-tight">
          Ready to audit candidate claims?
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto mt-2">
          Upload any engineering resume in PDF or DOCX format for an instant audit report.
        </p>
        <div className="mt-6">
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-white hover:bg-slate-200 text-[#090A0C] font-semibold text-xs transition-all active:scale-[0.98]"
          >
            Upload Resume Now
          </Link>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
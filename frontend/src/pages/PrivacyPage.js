import React from 'react';
import { Link } from 'react-router-dom';

function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      <div>
        <Link to="/" className="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1 mb-4">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-white tracking-tight">Privacy Policy</h1>
        <p className="text-xs text-slate-400 mt-1">Last updated: September 2026</p>
      </div>

      <div className="space-y-8 text-sm text-slate-300 leading-relaxed bg-[#111418] p-8 rounded-xl border border-[#1F242D]">
        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">1. Overview</h2>
          <p>
            ProfileAuditor provides automated technical resume auditing and authenticity scoring for engineering hiring teams and candidates. This Privacy Policy details how we handle information submitted through our platform.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">2. Information We Process</h2>
          <p>
            When you use ProfileAuditor, we process the following categories of data:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
            <li><strong className="text-white">Uploaded Resume Documents:</strong> Text, contact details, work history, skill lists, and project references contained in submitted PDF or DOCX files.</li>
            <li><strong className="text-white">Public Technical Profiles:</strong> Public repository data from GitHub (commit authorship, language breakdowns, repository stars, non-forked status) and publicly accessible LeetCode problem solving metrics.</li>
            <li><strong className="text-white">Job Descriptions:</strong> Role requirements submitted for optional role-fit matching.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">3. How We Use Information</h2>
          <p>
            Information submitted is used solely to:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
            <li>Generate real-time verification scores and ATS health diagnostic reports.</li>
            <li>Cross-reference claimed skills and projects against public open-source footprints.</li>
            <li>Enable candidate editing and formatted document exports in the live editor.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">4. Data Retention and Storage</h2>
          <p>
            Uploaded resume documents are stored in temporary processing storage solely for the duration of the audit session. We do not sell, rent, or monetize candidate resume data or candidate contact details to third-party data brokers.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">5. Third-Party API Integrations</h2>
          <p>
            Our verification engine interacts with public developer APIs including the GitHub REST API and the LeetCode GraphQL endpoint in accordance with their respective terms of service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">6. Contact</h2>
          <p>
            For questions regarding data processing or security practices, contact the ProfileAuditor engineering team at security@profileauditor.dev.
          </p>
        </section>
      </div>
    </div>
  );
}

export default PrivacyPage;

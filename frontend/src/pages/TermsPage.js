import React from 'react';
import { Link } from 'react-router-dom';

function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      <div>
        <Link to="/" className="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1 mb-4">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-white tracking-tight">Terms and Conditions</h1>
        <p className="text-xs text-slate-400 mt-1">Last updated: September 2026</p>
      </div>

      <div className="space-y-8 text-sm text-slate-300 leading-relaxed bg-[#111418] p-8 rounded-xl border border-[#1F242D]">
        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">1. Agreement to Terms</h2>
          <p>
            By accessing or using ProfileAuditor, you agree to be bound by these Terms and Conditions. If you do not agree to these terms, you may not use the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">2. Permitted Use</h2>
          <p>
            ProfileAuditor is designed for authentic engineering evaluation, technical screening, and candidate profile optimization. You agree not to:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
            <li>Submit documents containing malicious code, automated exploits, or unlawful content.</li>
            <li>Attempt to bypass rate limits or interfere with API availability.</li>
            <li>Use automated scrapers to mass-harvest reports without authorization.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">3. Accuracy of Audits and Disclaimers</h2>
          <p>
            Verification scores (Reality Score, ATS Health Score, and Role Fit) are calculated using public technical footprint heuristics and automated rule engines. Audits represent automated verification signals and should be used as one of several factors in comprehensive candidate assessments.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">4. Intellectual Property</h2>
          <p>
            You retain all rights and ownership of the resume documents and content you upload. ProfileAuditor claims no ownership over candidate documents or exported files generated through the platform.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">5. Limitation of Liability</h2>
          <p>
            ProfileAuditor provides services on an "as is" and "as available" basis without warranties of any kind, whether express or implied. Under no circumstances shall ProfileAuditor be liable for indirect, incidental, or consequential damages arising from hiring decisions or reliance on audit metrics.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">6. Modifications</h2>
          <p>
            We reserve the right to modify these terms at any time. Continued use of the platform after changes are posted constitutes acceptance of the updated terms.
          </p>
        </section>
      </div>
    </div>
  );
}

export default TermsPage;

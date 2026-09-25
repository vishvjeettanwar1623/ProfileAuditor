import React from 'react';
import { Link } from 'react-router-dom';

function CookiePolicyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      <div>
        <Link to="/" className="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1 mb-4 focus:ring-2 focus:ring-slate-400 rounded">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-white tracking-tight">Cookie Policy</h1>
        <p className="text-xs text-slate-400 mt-1">Last updated: September 2026</p>
      </div>

      <div className="space-y-8 text-sm text-slate-300 leading-relaxed bg-[#111418] p-8 rounded-xl border border-[#1F242D]">
        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">1. What Are Cookies and Local Storage?</h2>
          <p>
            Cookies and browser local storage are small text files or key-value entries placed on your device by websites you visit. They are commonly used to remember user preferences, maintain session state, and deliver a smooth user experience.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">2. How ProfileAuditor Uses Storage</h2>
          <p>
            ProfileAuditor operates under strict data minimization principles. We only store data essential to providing our software services:
          </p>
          <div className="space-y-3 pt-2">
            <div className="p-4 rounded-lg bg-[#161A20] border border-[#262C36]">
              <h3 className="font-bold text-white text-xs uppercase tracking-wider mb-1">Strictly Necessary / Functional Storage</h3>
              <ul className="list-disc pl-5 space-y-1 text-xs text-slate-300">
                <li><strong className="text-white">Session State:</strong> Remembers the active resume ID during verification pipelines.</li>
                <li><strong className="text-white">Editor Preferences:</strong> Retains your selected zoom level, typography mode, and custom role descriptions locally on your machine.</li>
                <li><strong className="text-white">Consent Preferences:</strong> Stores your cookie consent selection (`profileauditor_cookie_consent`).</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">3. Third-Party and Advertising Cookies</h2>
          <p>
            <strong className="text-white">We do not use advertising cookies, marketing pixels, or cross-site tracking beacons.</strong> We do not sell or monetize browsing behavior to third-party ad networks.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">4. Managing and Disabling Cookies</h2>
          <p>
            You can delete or block cookies and local storage through your browser settings at any time:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
            <li><strong className="text-white">Chrome:</strong> Settings &gt; Privacy and Security &gt; Cookies and other site data</li>
            <li><strong className="text-white">Firefox:</strong> Preferences &gt; Privacy &amp; Security &gt; Cookies and Site Data</li>
            <li><strong className="text-white">Safari:</strong> Preferences &gt; Privacy &gt; Manage Website Data</li>
          </ul>
          <p className="text-xs text-slate-400 mt-2">
            Note: Disabling essential local storage may reset your live editor preferences and active audit session.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">5. Contact Us</h2>
          <p>
            If you have questions regarding our use of cookies or local storage, reach out to our team at privacy@profileauditor.dev.
          </p>
        </section>
      </div>
    </div>
  );
}

export default CookiePolicyPage;

import React from 'react';
import { Link } from 'react-router-dom';

function RefundPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      <div>
        <Link to="/" className="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1 mb-4 focus:ring-2 focus:ring-slate-400 rounded">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-white tracking-tight">Refund & Billing Policy</h1>
        <p className="text-xs text-slate-400 mt-1">Last updated: September 2026</p>
      </div>

      <div className="space-y-8 text-sm text-slate-300 leading-relaxed bg-[#111418] p-8 rounded-xl border border-[#1F242D]">
        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">1. Open Access and Free Tier</h2>
          <p>
            ProfileAuditor provides free core developer resume parsing, ATS scoring, and GitHub/LeetCode public code verification for individual candidates and technical interviewers.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">2. Enterprise and Paid Subscriptions</h2>
          <p>
            For organizations utilizing high-volume batch audit APIs or dedicated team seats:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
            <li><strong className="text-white">14-Day Money-Back Guarantee:</strong> New annual or monthly organization licenses are eligible for a full refund within 14 calendar days of initial purchase if the service does not meet your technical evaluation needs.</li>
            <li><strong className="text-white">Cancellation Policy:</strong> You may cancel paid subscriptions at any time via your account dashboard. Cancellation stops automated renewal at the end of the current billing cycle.</li>
            <li><strong className="text-white">Service Downtime Credits:</strong> In the event of documented service unavailability exceeding 99.9% monthly uptime, prorated service credits are issued upon request.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">3. How to Request a Refund</h2>
          <p>
            To request a refund or billing review, submit your transaction ID and account email to billing@profileauditor.dev. Refund requests are processed within 3 to 5 business days.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">4. Contact Information</h2>
          <p>
            Billing inquiries: billing@profileauditor.dev<br />
            Business entity: ProfileAuditor Software Technologies Ltd.
          </p>
        </section>
      </div>
    </div>
  );
}

export default RefundPolicyPage;

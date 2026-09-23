import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function CookieConsentBanner() {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('profileauditor_cookie_consent');
    if (!consent) {
      setShowBanner(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('profileauditor_cookie_consent', 'accepted');
    setShowBanner(false);
  };

  const handleDecline = () => {
    localStorage.setItem('profileauditor_cookie_consent', 'essential_only');
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div
      role="region"
      aria-label="Cookie consent banner"
      className="fixed bottom-0 inset-x-0 z-50 p-4 bg-[#111418] border-t border-[#1F242D] shadow-2xl"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="text-xs text-slate-300 max-w-3xl leading-relaxed">
          <p>
            <strong className="text-white">Cookie & Privacy Notice:</strong> We use essential local storage to save your editor settings, zoom preferences, and audit session state. We do not use third-party advertising or cross-site tracking cookies. Read our{' '}
            <Link to="/cookies" className="text-slate-100 underline hover:text-white font-medium">
              Cookie Policy
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="text-slate-100 underline hover:text-white font-medium">
              Privacy Policy
            </Link>{' '}
            for full transparency.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 w-full md:w-auto">
          <button
            type="button"
            onClick={handleDecline}
            className="flex-1 md:flex-initial px-4 py-2 rounded-lg text-xs font-medium bg-[#161A20] hover:bg-[#1E232B] text-slate-300 border border-[#262C36] transition-all focus:ring-2 focus:ring-slate-400 focus:outline-none"
          >
            Essential Only
          </button>
          <button
            type="button"
            onClick={handleAccept}
            className="flex-1 md:flex-initial px-4 py-2 rounded-lg text-xs font-semibold bg-white hover:bg-slate-200 text-[#090A0C] transition-all focus:ring-2 focus:ring-white focus:outline-none shadow-sm"
          >
            Accept All
          </button>
        </div>
      </div>
    </div>
  );
}

export default CookieConsentBanner;

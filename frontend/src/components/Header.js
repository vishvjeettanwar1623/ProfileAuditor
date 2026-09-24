import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import CommandPaletteModal from './CommandPaletteModal';

function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [lastResumeId, setLastResumeId] = useState(null);

  useEffect(() => {
    const storedId = sessionStorage.getItem('profileauditor_last_resume_id');
    if (storedId) {
      setLastResumeId(storedId);
    }
  }, [location.pathname]);

  // Global keyboard shortcuts (Ctrl+K, Cmd+K, Escape)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        if (paletteOpen) setPaletteOpen(false);
        if (mobileMenuOpen) setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [paletteOpen, mobileMenuOpen]);

  const isPathActive = (path) => {
    if (path === '/') return location.pathname === '/';
    if (path === '/upload') return location.pathname === '/upload';
    if (path === '/editor') return location.pathname.startsWith('/editor');
    if (path === '/results') return location.pathname.startsWith('/results');
    return location.pathname === path;
  };

  const editorTargetUrl = lastResumeId ? `/editor/${lastResumeId}` : '/editor';

  return (
    <>
      <header className="sticky top-0 z-40 w-full px-3 sm:px-6 pt-3 pb-2 transition-all">
        {/* Floating Glass Island Container */}
        <div className="max-w-7xl mx-auto bg-[#0C0F15]/90 backdrop-blur-2xl border border-[#202735] rounded-2xl shadow-[0_10px_35px_rgba(0,0,0,0.5)] px-4 sm:px-6 py-2.5">
          <div className="flex items-center justify-between gap-3 sm:gap-4">
            
            {/* Left: Brand Identity */}
            <Link
              to="/"
              className="flex items-center gap-3 group focus:ring-2 focus:ring-white focus:outline-none rounded-xl p-1 transition-all"
              aria-label="ProfileAuditor Home"
            >
              <div className="relative w-9 h-9 rounded-xl bg-[#131720] border border-[#263042] text-white flex items-center justify-center shadow-inner group-hover:border-slate-300 group-hover:bg-[#1A202D] transition-all">
                <svg
                  className="w-4 h-4 text-white"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                {/* Micro Live Indicator */}
                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-sm bg-emerald-400 ring-2 ring-[#0C0F15]" />
              </div>

              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-sm sm:text-base tracking-tight text-white group-hover:text-slate-100 transition-colors">
                    ProfileAuditor
                  </span>
                  <span className="hidden sm:inline-block px-1.5 py-0.2 text-[9px] font-mono font-bold uppercase tracking-wider rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Engine
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono hidden md:inline leading-none">
                  Code & DSA Verification
                </span>
              </div>
            </Link>

            {/* Center: Segmented Navigation Dock */}
            <nav
              className="hidden lg:flex items-center gap-1 bg-[#121620] p-1 rounded-xl border border-[#222A38] shadow-inner shadow-black/40"
              aria-label="Main Navigation"
            >
              <Link
                to="/"
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:ring-2 focus:ring-white focus:outline-none ${
                  isPathActive('/')
                    ? 'bg-[#1C2330] text-white border border-[#2F3B4E] shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-[#161B26]'
                }`}
                aria-current={isPathActive('/') ? 'page' : undefined}
              >
                <svg className="w-3.5 h-3.5 opacity-75" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7" rx="1" />
                  <rect x="14" y="3" width="7" height="7" rx="1" />
                  <rect x="14" y="14" width="7" height="7" rx="1" />
                  <rect x="3" y="14" width="7" height="7" rx="1" />
                </svg>
                <span>Dashboard</span>
              </Link>

              <Link
                to="/upload"
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:ring-2 focus:ring-white focus:outline-none ${
                  isPathActive('/upload')
                    ? 'bg-[#1C2330] text-white border border-[#2F3B4E] shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-[#161B26]'
                }`}
                aria-current={isPathActive('/upload') ? 'page' : undefined}
              >
                <svg className="w-3.5 h-3.5 opacity-75" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Audit Resume</span>
              </Link>

              <Link
                to={editorTargetUrl}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:ring-2 focus:ring-white focus:outline-none ${
                  isPathActive('/editor')
                    ? 'bg-[#1C2330] text-white border border-[#2F3B4E] shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-[#161B26]'
                }`}
                aria-current={isPathActive('/editor') ? 'page' : undefined}
              >
                <svg className="w-3.5 h-3.5 opacity-75" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>Live ATS Editor</span>
                {lastResumeId && (
                  <span className="w-1.5 h-1.5 rounded-sm bg-emerald-400" title="Active document session" />
                )}
              </Link>

              {lastResumeId && (
                <Link
                  to={`/results/${lastResumeId}`}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:ring-2 focus:ring-white focus:outline-none ${
                    isPathActive('/results')
                      ? 'bg-[#1C2330] text-white border border-[#2F3B4E] shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-[#161B26]'
                  }`}
                  aria-current={isPathActive('/results') ? 'page' : undefined}
                >
                  <svg className="w-3.5 h-3.5 opacity-75" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>Verification Report</span>
                </Link>
              )}
            </nav>

            {/* Right: Quick Command Search & Primary Action */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Quick Jump Search Palette Button */}
              <button
                type="button"
                onClick={() => setPaletteOpen(true)}
                className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141820] hover:bg-[#1A202B] text-slate-400 hover:text-slate-200 border border-[#262E3B] text-xs transition-all focus:ring-2 focus:ring-white focus:outline-none shadow-sm"
                aria-label="Open command palette (Ctrl+K)"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="hidden xl:inline text-[11px]">Quick Jump</span>
                <kbd className="px-1.5 py-0.5 text-[9px] font-mono text-slate-400 bg-[#0E1117] border border-[#222A38] rounded">
                  Ctrl K
                </kbd>
              </button>

              {/* Active Session Badge */}
              {lastResumeId && (
                <div className="hidden xl:flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-[#121620] border border-[#222A38] text-[11px] font-mono">
                  <span className="w-2 h-2 rounded-sm bg-emerald-400 animate-pulse" />
                  <span className="text-slate-400">AUD-{lastResumeId.slice(0, 6)}</span>
                </div>
              )}

              {/* New Audit CTA */}
              <Link
                to="/upload"
                className="inline-flex items-center gap-1.5 px-3.5 sm:px-4 py-2 rounded-lg text-xs font-bold text-[#090A0C] bg-white hover:bg-slate-200 transition-all active:scale-[0.98] focus:ring-2 focus:ring-white focus:outline-none shadow-md shadow-white/10"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                <span>New Audit</span>
              </Link>

              {/* Mobile Drawer Trigger */}
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="flex lg:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-[#161B26] border border-[#222A38] focus:ring-2 focus:ring-white focus:outline-none"
                aria-expanded={mobileMenuOpen}
                aria-label="Toggle navigation menu"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden mt-2 max-w-7xl mx-auto">
            <div className="bg-[#0C0F15]/95 backdrop-blur-2xl border border-[#202735] rounded-2xl p-4 space-y-3 shadow-2xl animate-in slide-in-from-top-2">
              <button
                type="button"
                onClick={() => {
                  setMobileMenuOpen(false);
                  setPaletteOpen(true);
                }}
                className="w-full flex items-center justify-between p-2.5 rounded-lg bg-[#141820] border border-[#262E3B] text-xs text-slate-300"
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Quick Search & Jump</span>
                </div>
                <kbd className="px-1.5 py-0.5 text-[9px] font-mono bg-[#0E1117] border border-[#222A38] rounded">
                  Ctrl+K
                </kbd>
              </button>

              {lastResumeId && (
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#141820] border border-[#262E3B] text-xs">
                  <span className="text-slate-400 font-medium">Active Candidate Session</span>
                  <span className="font-mono text-emerald-400 font-semibold">AUD-{lastResumeId.slice(0, 8)}</span>
                </div>
              )}

              <div className="space-y-1">
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isPathActive('/')
                      ? 'bg-[#1C2330] text-white border border-[#2F3B4E]'
                      : 'text-slate-300 hover:bg-[#141820] hover:text-white'
                  }`}
                >
                  <span>Dashboard</span>
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>

                <Link
                  to="/upload"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isPathActive('/upload')
                      ? 'bg-[#1C2330] text-white border border-[#2F3B4E]'
                      : 'text-slate-300 hover:bg-[#141820] hover:text-white'
                  }`}
                >
                  <span>Audit Developer Resume</span>
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>

                <Link
                  to={editorTargetUrl}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isPathActive('/editor')
                      ? 'bg-[#1C2330] text-white border border-[#2F3B4E]'
                      : 'text-slate-300 hover:bg-[#141820] hover:text-white'
                  }`}
                >
                  <span>Live ATS Document Editor</span>
                  <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>

                {lastResumeId && (
                  <Link
                    to={`/results/${lastResumeId}`}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                      isPathActive('/results')
                        ? 'bg-[#1C2330] text-white border border-[#2F3B4E]'
                        : 'text-slate-300 hover:bg-[#141820] hover:text-white'
                    }`}
                  >
                    <span>Candidate Verification Report</span>
                    <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                )}
              </div>

              <div className="pt-3 border-t border-[#202735] space-y-2">
                <Link
                  to="/upload"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-white text-[#090A0C] font-bold text-xs shadow-md"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Start New Resume Audit</span>
                </Link>

                <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-slate-500 pt-1">
                  <Link to="/privacy" onClick={() => setMobileMenuOpen(false)} className="hover:text-slate-300">
                    Privacy
                  </Link>
                  <span className="text-slate-700">•</span>
                  <Link to="/terms" onClick={() => setMobileMenuOpen(false)} className="hover:text-slate-300">
                    Terms
                  </Link>
                  <span className="text-slate-700">•</span>
                  <Link to="/cookies" onClick={() => setMobileMenuOpen(false)} className="hover:text-slate-300">
                    Cookies
                  </Link>
                  <span className="text-slate-700">•</span>
                  <Link to="/refund" onClick={() => setMobileMenuOpen(false)} className="hover:text-slate-300">
                    Refunds
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Global Command Palette Modal */}
      <CommandPaletteModal isOpen={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  );
}

export default Header;
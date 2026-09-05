import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-[#090A0C]/90 backdrop-blur-md border-b border-[#1F242D]">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-white text-[#090A0C] flex items-center justify-center shadow-sm">
              <svg 
                className="w-4 h-4 text-[#090A0C]" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2.5" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <span className="font-bold text-base tracking-tight text-white">
              ProfileAuditor
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1 bg-[#111418] p-1 rounded-lg border border-[#1F242D]">
            <Link
              to="/"
              className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                isActive('/')
                  ? 'bg-[#1F242D] text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/upload"
              className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                isActive('/upload')
                  ? 'bg-[#1F242D] text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Audit Resume
            </Link>
            <Link
              to="/editor"
              className={`px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                isActive('/editor')
                  ? 'bg-[#1F242D] text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Live ATS Editor
            </Link>
          </nav>

          {/* Action button */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/upload"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-[#090A0C] bg-white hover:bg-slate-200 transition-all active:scale-[0.98]"
            >
              <span>New Audit</span>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#161A20]"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-[#1F242D] bg-[#090A0C] px-4 pt-2 pb-4 space-y-2">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/') ? 'bg-[#161A20] text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Dashboard
          </Link>
          <Link
            to="/upload"
            onClick={() => setMobileMenuOpen(false)}
            className={`block px-3 py-2 rounded-md text-sm font-medium ${
              isActive('/upload') ? 'bg-[#161A20] text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Audit Resume
          </Link>
        </div>
      )}
    </header>
  );
}

export default Header;
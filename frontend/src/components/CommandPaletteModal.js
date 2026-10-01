import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function CommandPaletteModal({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const lastResumeId = sessionStorage.getItem('profileauditor_last_resume_id');

  const allItems = [
    {
      id: 'dashboard',
      title: 'Dashboard & Overview',
      category: 'Navigation',
      path: '/',
      shortcut: 'G D',
      description: 'Main overview of candidate auditing pipelines',
    },
    {
      id: 'upload',
      title: 'Audit Developer Resume',
      category: 'Pipeline',
      path: '/upload',
      shortcut: 'G U',
      description: 'Upload PDF or DOCX resume to start verification audit',
    },
    {
      id: 'editor',
      title: 'Live ATS Document Editor',
      category: 'Pipeline',
      path: lastResumeId ? `/editor/${lastResumeId}` : '/editor',
      shortcut: 'G E',
      description: 'Exact-layout document editor with real-time ATS optimization',
    },
    ...(lastResumeId
      ? [
          {
            id: 'report',
            title: `Active Verification Report (AUD-${lastResumeId.slice(0, 6)})`,
            category: 'Active Session',
            path: `/results/${lastResumeId}`,
            shortcut: 'G R',
            description: 'View Reality Score, GitHub proofs, and LeetCode metrics',
          },
        ]
      : []),
    {
      id: 'privacy',
      title: 'Privacy Policy',
      category: 'Legal',
      path: '/privacy',
      shortcut: 'L P',
      description: 'Technical data minimization & GDPR compliance policy',
    },
    {
      id: 'terms',
      title: 'Terms of Service',
      category: 'Legal',
      path: '/terms',
      shortcut: 'L T',
      description: 'Service availability & liability limitation terms',
    },
    {
      id: 'cookies',
      title: 'Cookie Policy',
      category: 'Legal',
      path: '/cookies',
      shortcut: 'L C',
      description: 'Disclosure of strictly necessary functional local storage',
    },
    {
      id: 'refund',
      title: 'Refund Policy',
      category: 'Legal',
      path: '/refund',
      shortcut: 'L R',
      description: '14-day guarantee and cancellation information',
    },
  ];

  const filteredItems = allItems.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.description.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const handleSelect = (item) => {
    navigate(item.path);
    onClose();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filteredItems.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filteredItems.length) % (filteredItems.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredItems[selectedIndex]) {
        handleSelect(filteredItems[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Box */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Command palette quick navigation"
        className="relative w-full max-w-xl bg-[#0F131A] border border-[#262E3B] rounded-xl shadow-2xl overflow-hidden z-50 animate-in fade-in-0 zoom-in-95 duration-100"
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-[#1F2633] gap-3">
          <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or jump to page..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <kbd className="px-2 py-0.5 text-[10px] font-mono text-slate-400 bg-[#161B24] border border-[#262E3B] rounded">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredItems.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500">
              No matching commands or pages found.
            </div>
          ) : (
            filteredItems.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleSelect(item)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-all ${
                    isSelected
                      ? 'bg-[#1C222C] text-white border border-[#2E3747]'
                      : 'text-slate-300 hover:bg-[#141820] border border-transparent'
                  }`}
                >
                  <div className="flex flex-col min-w-0 pr-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-white">{item.title}</span>
                      <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-[#111418] text-slate-400 border border-[#262E3B] font-mono">
                        {item.category}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 truncate mt-0.5">
                      {item.description}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <kbd className="text-[10px] font-mono text-slate-400 bg-[#111418] px-1.5 py-0.5 rounded border border-[#222834]">
                      {item.shortcut}
                    </kbd>
                    <svg
                      className={`w-4 h-4 text-slate-400 transition-transform ${
                        isSelected ? 'translate-x-0.5 text-white' : ''
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="px-4 py-2 bg-[#0A0D12] border-t border-[#1F2633] flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-3">
            <span><kbd className="font-mono text-slate-400">↑↓</kbd> navigate</span>
            <span><kbd className="font-mono text-slate-400">↵</kbd> select</span>
          </div>
          <span>ProfileAuditor Command Palette</span>
        </div>
      </div>
    </div>
  );
}

export default CommandPaletteModal;

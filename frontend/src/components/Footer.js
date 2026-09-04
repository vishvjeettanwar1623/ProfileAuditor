import React from 'react';

function Footer() {
  return (
    <footer className="border-t border-[#1F242D] bg-[#090A0C] mt-auto py-6">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2 font-medium text-slate-400">
            <span>ProfileAuditor</span>
          </div>

          <div>
            <span>&copy; {new Date().getFullYear()} ProfileAuditor. Verified engineering audits.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
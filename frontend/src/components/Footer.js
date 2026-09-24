import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="border-t border-[#1F242D] bg-[#090A0C] mt-auto py-6">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-slate-500">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <span className="font-semibold text-slate-400">ProfileAuditor</span>
            <Link to="/privacy" className="hover:text-slate-300 transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="hover:text-slate-300 transition-colors">
              Terms & Conditions
            </Link>
            <Link to="/cookies" className="hover:text-slate-300 transition-colors">
              Cookie Policy
            </Link>
            <Link to="/refund" className="hover:text-slate-300 transition-colors">
              Refund Policy
            </Link>
          </div>

          <div className="text-center sm:text-right">
            <span>&copy; {new Date().getFullYear()} ProfileAuditor Software Technologies Ltd. All rights reserved.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
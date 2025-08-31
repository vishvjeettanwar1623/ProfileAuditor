import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-primary-500 border-b border-accent-neon/20">
      <div className="container mx-auto px-4 py-6 flex justify-between items-center">
        <Link to="/" className="flex items-center">
          <img
            src="/logo.png"
            alt="ProfileAuditor Logo"
            className="h-10 w-auto"
          />
          <span className="ml-2 text-2xl font-bold text-accent-matrix glow">ProfileAuditor</span>
        </Link>
        <nav className="hidden md:flex space-x-10">
          <Link to="/" className="text-base font-medium text-accent-neon hover:text-highlight-glow transition-colors">
            Home
          </Link>
          <Link to="/upload" className="text-base font-medium text-accent-neon hover:text-highlight-glow transition-colors">
            Upload Resume
          </Link>
        </nav>
        <div className="md:hidden">
          <button
            type="button"
            className="bg-white rounded-md p-2 inline-flex items-center justify-center text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            aria-expanded="false"
          >
            <span className="sr-only">Open menu</span>
            <svg
              className="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
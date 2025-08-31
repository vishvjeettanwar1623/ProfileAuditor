import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero section */}
      <div className="py-12 md:py-20">
        <div className="text-center">
          <h1 className="text-4xl tracking-tight font-extrabold text-primary-500 sm:text-5xl md:text-6xl">
            <span className="block text-accent-matrix">Verify Resume Claims with</span>
            <span className="block text-highlight-glow">ProfileAuditor</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-accent-neon sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Upload a resume, and our AI will verify skills and projects against GitHub, Twitter, and LinkedIn data.
            Get a Reality Score that measures how well online activity matches resume claims.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <div className="rounded-md shadow">
              <Link
                to="/upload"
                className="w-full flex items-center justify-center px-8 py-3 border border-accent-matrix text-base font-medium rounded-md text-primary-900 bg-accent-matrix hover:bg-highlight-glow transition-colors md:py-4 md:text-lg md:px-10"
              >
                Upload Resume
              </Link>
            </div>
            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
              <a
                href="#how-it-works"
                className="w-full flex items-center justify-center px-8 py-3 border border-accent-neon text-base font-medium rounded-md text-accent-neon bg-primary-500 hover:bg-primary-600 transition-colors md:py-4 md:text-lg md:px-10"
              >
                How It Works
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* How it works section */}
      <div id="how-it-works" className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-primary-600 font-semibold tracking-wide uppercase">Process</h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              How ProfileAuditor Works
            </p>
            <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
              Our AI-powered system verifies resume claims against public data to generate a Reality Score.
            </p>
          </div>

          <div className="mt-10">
            <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                    <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">Upload Resume</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  Upload a resume in PDF or DOC format. Our system will parse the text and extract skills and projects.
                </dd>
              </div>

              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                    <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">Verify Claims</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  We verify skills and projects against GitHub repositories, Twitter posts, and LinkedIn profiles.
                </dd>
              </div>

              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                    <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">Generate Score</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  We calculate a Reality Score (0-100) based on how much of the resume is verified by online activity.
                </dd>
              </div>

              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white">
                    <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">Send Invitations</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  Automatically send interview invitations to candidates with high Reality Scores.
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-primary-700">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Ready to verify resume claims?</span>
            <span className="block">Start using ProfileAuditor today.</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-primary-200">
            Upload a resume and get a Reality Score in minutes.
          </p>
          <Link
            to="/upload"
            className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-primary-50 sm:w-auto"
          >
            Get Started
          </Link>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
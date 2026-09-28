import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import CookieConsentBanner from './components/CookieConsentBanner';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import ResumeEditorPage from './pages/ResumeEditorPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import RefundPolicyPage from './pages/RefundPolicyPage';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-[#090A0C] text-slate-200">
        <Header />
        <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/editor" element={<ResumeEditorPage />} />
            <Route path="/editor/:resumeId" element={<ResumeEditorPage />} />
            <Route path="/results/:resumeId" element={<ResultsPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/terms" element={<TermsPage />} />
            <Route path="/cookies" element={<CookiePolicyPage />} />
            <Route path="/refund" element={<RefundPolicyPage />} />
          </Routes>
        </main>
        <Footer />
        <CookieConsentBanner />
      </div>
    </Router>
  );
}

export default App;
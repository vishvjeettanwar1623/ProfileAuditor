import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import ResumeEditorPage from './pages/ResumeEditorPage';

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
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
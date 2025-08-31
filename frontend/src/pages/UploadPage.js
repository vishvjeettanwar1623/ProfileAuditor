import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setError('');
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please upload a resume file');
      return;
    }
    
    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Upload resume
      const response = await axios.post(`${API_BASE_URL}/api/resume/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const resumeId = response.data.resume_id;
      
      // Navigate to results page (verification will use usernames parsed from resume if present)
      navigate(`/results/${resumeId}`);
    } catch (error) {
      console.error('Error uploading resume:', error);
      setError(error.response?.data?.detail || 'Error uploading resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Upload Your Resume
        </h1>
        <p className="mt-4 text-lg text-gray-500">
          Upload your resume file (PDF or DOCX) to begin verification.
        </p>
      </div>
      
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit}>
            {/* Resume upload */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resume (PDF or DOCX)
              </label>
              <div 
                {...getRootProps()} 
                className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'}`}
              >
                <div className="space-y-1 text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                    aria-hidden="true"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <input {...getInputProps()} />
                    <p className="pl-1">
                      {isDragActive
                        ? 'Drop the file here'
                        : file
                        ? `Selected: ${file.name}`
                        : 'Drag and drop your resume, or click to select a file'}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500">PDF or DOCX up to 10MB</p>
                </div>
              </div>
            </div>
            
            {/* Personal information and social usernames removed per requirements */}
            
            {/* Error message */}
            {error && (
              <div className="mt-4 text-sm text-red-600">
                {error}
              </div>
            )}
            
            {/* Submit button */}
            <div className="mt-6">
              <button
                type="submit"
                disabled={loading}
                className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </>
                ) : (
                  'Upload and Verify'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
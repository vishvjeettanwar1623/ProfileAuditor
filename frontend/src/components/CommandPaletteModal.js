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

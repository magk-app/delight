'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const SECTIONS = [
  { id: 'hero', label: '00 START' },
  { id: 'psychology', label: '01 PSYCH' },
  { id: 'mission', label: '02 ENGINE' },
  { id: 'squad', label: '03 SQUAD' },
  { id: 'world', label: '04 WORLD' },
  { id: 'growth', label: '05 GROWTH' },
  { id: 'manifesto', label: '06 END' },
];

export const ScrollProgress: React.FC = () => {
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    const handleScroll = () => {
      const sections = SECTIONS.map(s => document.getElementById(s.id));
      const scrollPosition = window.scrollY + window.innerHeight / 3;

      for (const section of sections) {
        if (section && section.offsetTop <= scrollPosition && (section.offsetTop + section.offsetHeight) > scrollPosition) {
          setActiveSection(section.id);
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="hidden lg:flex fixed left-8 top-1/2 -translate-y-1/2 z-50 flex-col gap-6 mix-blend-difference">
      {SECTIONS.map((section) => (
        <a
          key={section.id}
          href={`#${section.id}`}
          className="group flex items-center gap-4 cursor-pointer"
        >
          <div className="relative w-px h-8 bg-white/20 overflow-hidden">
            <motion.div
              className="w-full bg-white absolute top-0 left-0"
              initial={{ height: 0 }}
              animate={{ height: activeSection === section.id ? '100%' : '0%' }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <span className={`text-[10px] font-mono tracking-widest transition-all duration-300 ${
            activeSection === section.id ? 'text-white opacity-100 translate-x-0' : 'text-zinc-500 opacity-0 -translate-x-4 group-hover:opacity-50 group-hover:translate-x-0'
          }`}>
            {section.label}
          </span>
        </a>
      ))}
    </div>
  );
};

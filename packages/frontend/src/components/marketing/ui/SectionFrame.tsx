'use client';

import React from 'react';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';

interface SectionFrameProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
  label?: string;
}

export const SectionFrame: React.FC<SectionFrameProps> = ({ children, className, id, label }) => {
  return (
    <section id={id} className={clsx("relative w-full px-6 py-24 md:py-32 max-w-7xl mx-auto", className)}>
      {label && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="absolute left-6 top-12 md:left-0 md:top-16 text-[10px] tracking-[0.25em] text-zinc-500 uppercase font-mono"
        >
          {label}
        </motion.div>
      )}
      {children}
    </section>
  );
};

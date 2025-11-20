'use client';

import React from 'react';
import { motion } from 'framer-motion';

export const Globe: React.FC = () => {
  return (
    <div className="w-full h-full relative flex items-center justify-center perspective-1000">
      {/* Atmosphere Halo */}
      <div className="absolute w-[500px] h-[500px] md:w-[700px] md:h-[700px] bg-blue-500/20 rounded-full blur-[80px] animate-pulse-slow" />

      <motion.div
        className="relative w-[400px] h-[400px] md:w-[600px] md:h-[600px]"
        animate={{ rotateY: 360, rotateZ: 15 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        {/* Core */}
        <div className="absolute inset-0 bg-blue-900/10 rounded-full border border-blue-500/20" />

        {/* Latitudes - Glowing Rings */}
        {[...Array(6)].map((_, i) => (
          <div
            key={`lat-${i}`}
            className="absolute inset-0 border border-blue-400/30 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.2)]"
            style={{
              transform: `rotateX(${90}deg) translateZ(${(i - 2.5) * 100}px) scale(${Math.cos((i - 2.5) * 0.5)})`,
            }}
          />
        ))}

        {/* Longitudes - Vertical Arcs */}
        {[...Array(8)].map((_, i) => (
          <div
            key={`long-${i}`}
            className="absolute inset-0 border border-blue-400/20 rounded-full"
            style={{
              transform: `rotateY(${i * 45}deg)`,
            }}
          />
        ))}

        {/* Floating Data Points */}
        {[...Array(12)].map((_, i) => (
          <motion.div
            key={`dot-${i}`}
            className="absolute w-2 h-2 bg-white rounded-full shadow-[0_0_10px_white]"
            style={{
              top: '50%',
              left: '50%',
              transform: `rotateY(${i * 30}deg) rotateX(${45}deg) translateZ(300px)`
            }}
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 3, delay: i * 0.2, repeat: Infinity }}
          />
        ))}
      </motion.div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, Coffee, Sunset } from 'lucide-react';

const TIMELINE = [
  { time: 8, label: 'Morning Kickoff', desc: 'Gentle prioritization. What matters today?', icon: Sun, color: 'from-orange-500/20 to-blue-900/20' },
  { time: 14, label: 'Midday Slump', desc: 'Compassionate check-in. Need a pivot?', icon: Coffee, color: 'from-blue-500/20 to-zinc-900/20' },
  { time: 19, label: 'Evening Reflection', desc: 'Log the wins. Update the constellation.', icon: Sunset, color: 'from-purple-900/20 to-black' },
  { time: 23, label: 'Dream State', desc: 'System offline. Memory consolidation.', icon: Moon, color: 'from-black to-zinc-900' },
];

export const DailyLoop: React.FC = () => {
  const [hour, setHour] = useState(8);

  const activePhase = TIMELINE.reduce((prev, curr) => {
    return Math.abs(curr.time - hour) < Math.abs(prev.time - hour) ? curr : prev;
  });

  const Icon = activePhase.icon;

  return (
    <div className="w-full bg-black rounded-3xl overflow-hidden border border-white/5 relative h-[500px] flex flex-col">
        {/* Dynamic Background */}
        <motion.div
            key={activePhase.label}
            className={`absolute inset-0 bg-gradient-to-b ${activePhase.color} transition-colors duration-1000`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        />

        <div className="relative z-10 p-12 flex-1 flex flex-col justify-center items-center text-center space-y-6">
            <motion.div
                key={activePhase.label + "_icon"}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="p-4 rounded-full bg-white/5 border border-white/10 backdrop-blur-md"
            >
                <Icon size={32} className="text-white" />
            </motion.div>

            <div className="space-y-2 max-w-md">
                <motion.h3
                    key={activePhase.label + "_title"}
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="text-3xl font-display font-medium text-white"
                >
                    {activePhase.label}
                </motion.h3>
                <motion.p
                    key={activePhase.label + "_desc"}
                    initial={{ y: 10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="text-zinc-400"
                >
                    {activePhase.desc}
                </motion.p>
            </div>
        </div>

        {/* Scrubber */}
        <div className="relative z-20 p-8 bg-black/20 backdrop-blur-sm border-t border-white/5">
            <input
                type="range"
                min="6"
                max="24"
                step="0.1"
                value={hour}
                onChange={(e) => setHour(parseFloat(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-white hover:accent-blue-400 transition-all"
            />
            <div className="flex justify-between mt-4 text-xs text-zinc-500 font-mono uppercase tracking-widest">
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>24:00</span>
            </div>
        </div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Battery, BatteryWarning, Zap } from 'lucide-react';

export const MissionControl: React.FC = () => {
  const [energy, setEnergy] = useState(50);

  // Derived state
  const getPhase = (e: number) => {
    if (e < 30) return { label: 'Recovery', color: 'text-rose-400', bg: 'bg-rose-500', text: 'Micro-missions only. 10m max.', icon: BatteryWarning };
    if (e < 70) return { label: 'Steady', color: 'text-emerald-400', bg: 'bg-emerald-500', text: 'Standard output. Focus blocks engaged.', icon: Battery };
    return { label: 'Overdrive', color: 'text-blue-400', bg: 'bg-blue-500', text: 'Deep work protocols. Stretch goals active.', icon: Zap };
  };

  const phase = getPhase(energy);
  const Icon = phase.icon;

  return (
    <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-white leading-tight">
                From Overwhelm <br />
                <span className="text-zinc-500">To Action</span>
            </h2>
            <p className="text-zinc-400 text-lg max-w-md">
                Most tools ignore your biology. Delight reads your energy and reshapes your workload instantly.
            </p>

            <div className="pt-8 space-y-8">
                <div className="space-y-3">
                    <div className="flex justify-between text-xs uppercase tracking-widest font-mono text-zinc-500">
                        <span>Burnout</span>
                        <span>Flow</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={energy}
                        onChange={(e) => setEnergy(parseInt(e.target.value))}
                        className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-white hover:accent-zinc-200 transition-all"
                    />
                </div>
            </div>
        </div>

        <div className="relative h-[400px] w-full flex items-center justify-center">
             {/* Background Glow based on energy */}
             <motion.div
                className={`absolute inset-0 blur-[100px] opacity-20 transition-colors duration-700 ${phase.bg}`}
             />

             {/* The Card Stack */}
             <div className="relative w-64 md:w-72">
                {[1, 2, 3].map((i) => (
                    <motion.div
                        key={i}
                        className="absolute inset-0 bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl"
                        style={{
                            top: i * 12,
                            scale: 1 - (i * 0.05),
                            opacity: 1 - (i * 0.2),
                            zIndex: 10 - i
                        }}
                    />
                ))}

                {/* Active Card */}
                <motion.div
                    key={phase.label} // Force re-render anim
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="relative z-20 bg-zinc-950 border border-zinc-800 rounded-xl p-6 shadow-2xl overflow-hidden"
                >
                    <div className={`absolute top-0 left-0 w-1 h-full transition-colors duration-500 ${phase.bg}`} />

                    <div className="flex justify-between items-start mb-8">
                        <div className="space-y-1">
                            <span className={`text-xs font-bold uppercase tracking-widest transition-colors duration-300 ${phase.color}`}>
                                {phase.label} Protocol
                            </span>
                            <h3 className="text-white font-display text-xl">Daily Briefing</h3>
                        </div>
                        <Icon className={`w-5 h-5 ${phase.color}`} />
                    </div>

                    <div className="space-y-4">
                        <div className="h-px w-full bg-zinc-900" />
                        <p className="text-zinc-300 text-sm leading-relaxed">
                            {phase.text}
                        </p>
                        <div className="flex gap-2 pt-2">
                             <div className="h-1.5 flex-1 bg-zinc-900 rounded-full overflow-hidden">
                                <motion.div
                                    className={`h-full ${phase.bg}`}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${energy}%` }}
                                    transition={{ duration: 0.5 }}
                                />
                             </div>
                        </div>
                    </div>
                </motion.div>
             </div>
        </div>
    </div>
  );
};

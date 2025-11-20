'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Link, Sparkles, Crown } from 'lucide-react';

export const CollaborativeStory: React.FC = () => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStep((prev) => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-2 gap-0 border border-white/10 rounded-3xl overflow-hidden bg-black">
      {/* Left: The Concept - Swiss Design Typography */}
      <div className="p-12 lg:p-16 flex flex-col justify-between bg-zinc-900/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-32 bg-blue-500/5 rounded-full blur-[80px]" />

        <div className="relative z-10 space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] uppercase tracking-widest text-purple-400 mb-4">
                <Users size={12} />
                Multiplayer Narrative
            </div>
            <h3 className="text-4xl md:text-5xl font-display font-semibold text-white leading-none">
                Sync <br/> Your <br/> <span className="text-purple-500">Sagas.</span>
            </h3>
            <p className="text-lg text-zinc-400 leading-relaxed max-w-md">
                Don't just chat. Co-author. Delight lets you link your progress with a friend.
                When they hit the gym, your shared storyline unlocks a new chapter.
            </p>
        </div>

        <div className="relative z-10 mt-12 grid grid-cols-2 gap-4">
            <div className="p-4 border border-white/10 rounded-xl bg-black/40">
                <Crown size={20} className="text-amber-400 mb-2" />
                <div className="text-sm font-medium text-white">Party Buffs</div>
                <div className="text-xs text-zinc-500">Shared XP multiplier</div>
            </div>
            <div className="p-4 border border-white/10 rounded-xl bg-black/40">
                <Link size={20} className="text-cyan-400 mb-2" />
                <div className="text-sm font-medium text-white">Chain Reactions</div>
                <div className="text-xs text-zinc-500">Your win triggers their loot</div>
            </div>
        </div>
      </div>

      {/* Right: The Visualizer */}
      <div className="relative bg-black min-h-[500px] border-l border-white/10 flex flex-col items-center justify-center p-8">

          {/* Grid Line Background */}
          <div className="absolute inset-0" style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)',
                backgroundSize: '40px 40px'
            }} />

          <div className="relative w-full max-w-md">
            {/* Connection Beam */}
            <div className="absolute top-12 left-1/2 -translate-x-1/2 w-1 h-[200px] bg-gradient-to-b from-transparent via-purple-500/50 to-transparent z-0" />

            {/* Player Nodes */}
            <div className="flex justify-between mb-24 relative z-10">
                <motion.div
                    animate={{ y: [0, -5, 0] }}
                    transition={{ duration: 4, repeat: Infinity }}
                    className="flex flex-col items-center gap-3"
                >
                    <div className="w-16 h-16 rounded-full border-2 border-blue-500 bg-zinc-900 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                        <span className="font-display font-bold text-white">YOU</span>
                    </div>
                    <div className="px-3 py-1 bg-zinc-800 rounded-full border border-zinc-700 text-[10px] uppercase tracking-wider text-blue-300">
                        Writing Ch. 4
                    </div>
                </motion.div>

                <motion.div
                     animate={{ y: [0, -5, 0] }}
                     transition={{ duration: 4, delay: 1, repeat: Infinity }}
                     className="flex flex-col items-center gap-3"
                >
                    <div className="w-16 h-16 rounded-full border-2 border-pink-500 bg-zinc-900 flex items-center justify-center shadow-[0_0_20px_rgba(236,72,153,0.3)]">
                        <span className="font-display font-bold text-white">ALLY</span>
                    </div>
                    <div className="px-3 py-1 bg-zinc-800 rounded-full border border-zinc-700 text-[10px] uppercase tracking-wider text-pink-300">
                        Design Sprint
                    </div>
                </motion.div>
            </div>

            {/* The Shared Story Event */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={step}
                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 1.1 }}
                    transition={{ duration: 0.5 }}
                    className="relative z-20 bg-zinc-900/90 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-2xl text-center"
                >
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-widest flex items-center gap-1">
                        <Sparkles size={10} />
                        Story Event
                    </div>

                    {step === 0 && (
                        <div>
                            <h4 className="text-white font-display text-lg mb-1">The Alliance Forms</h4>
                            <p className="text-sm text-zinc-400">You and Ally have synced objectives. A shared timeline has been created.</p>
                        </div>
                    )}
                    {step === 1 && (
                        <div>
                            <h4 className="text-white font-display text-lg mb-1">Double Impact</h4>
                            <p className="text-sm text-zinc-400">Ally completed "Design Sprint". Your motivation buff increased by 15%.</p>
                        </div>
                    )}
                    {step === 2 && (
                        <div>
                            <h4 className="text-white font-display text-lg mb-1">Boss Defeated</h4>
                            <p className="text-sm text-zinc-400">Combined output reached 100%. The "Procrastination Beast" retreats.</p>
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>

            {/* Connecting lines animation */}
            <svg className="absolute top-12 left-0 w-full h-[200px] pointer-events-none z-0">
                <motion.path
                    d="M 60 40 Q 110 150 224 150"
                    fill="none"
                    stroke="rgba(59, 130, 246, 0.5)"
                    strokeWidth="2"
                    strokeDasharray="5 5"
                    animate={{ strokeDashoffset: [0, -10] }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
                <motion.path
                    d="M 380 40 Q 330 150 224 150"
                    fill="none"
                    stroke="rgba(236, 72, 153, 0.5)"
                    strokeWidth="2"
                    strokeDasharray="5 5"
                    animate={{ strokeDashoffset: [0, -10] }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
            </svg>
          </div>
      </div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Split, Clock, CheckCircle2 } from 'lucide-react';

export const FeatureDeepDive: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'breakdown' | 'timeline'>('breakdown');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24 items-start">
        {/* Controls */}
        <div className="lg:col-span-4 space-y-8 sticky top-32">
            <div>
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white mb-6">
                    Mechanics of <br/> <span className="text-blue-500">Momentum</span>.
                </h2>
                <p className="text-lg text-zinc-400 leading-relaxed">
                    Delight isn't just a tracker. It's a procedural generation engine for your life.
                    See how we turn vague ambition into concrete gameplay.
                </p>
            </div>

            <div className="flex flex-col gap-2">
                <button
                    onClick={() => setActiveTab('breakdown')}
                    className={`text-left p-4 rounded-xl border transition-all ${activeTab === 'breakdown' ? 'bg-zinc-800 border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.1)]' : 'bg-transparent border-zinc-800 hover:bg-zinc-900'}`}
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-lg ${activeTab === 'breakdown' ? 'bg-blue-500 text-white' : 'bg-zinc-800 text-zinc-500'}`}>
                            <Split size={18} />
                        </div>
                        <span className="font-display font-bold text-white">Fractal Decomposition</span>
                    </div>
                    <p className="text-xs text-zinc-500 pl-12">
                        Big goals are paralyzing. We shatter them into playable micro-missions automatically.
                    </p>
                </button>

                <button
                    onClick={() => setActiveTab('timeline')}
                    className={`text-left p-4 rounded-xl border transition-all ${activeTab === 'timeline' ? 'bg-zinc-800 border-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.1)]' : 'bg-transparent border-zinc-800 hover:bg-zinc-900'}`}
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`p-2 rounded-lg ${activeTab === 'timeline' ? 'bg-purple-500 text-white' : 'bg-zinc-800 text-zinc-500'}`}>
                            <Clock size={18} />
                        </div>
                        <span className="font-display font-bold text-white">Narrative Evolution</span>
                    </div>
                    <p className="text-xs text-zinc-500 pl-12">
                        Your story isn't static. Watch how your character arc evolves over 30 days of consistency.
                    </p>
                </button>
            </div>
        </div>

        {/* Visualization Area */}
        <div className="lg:col-span-8 bg-zinc-900/30 border border-white/5 rounded-3xl p-8 min-h-[600px] relative overflow-hidden flex items-center justify-center">
            <AnimatePresence mode="wait">
                {activeTab === 'breakdown' ? (
                    <FractalGoalDemo key="breakdown" />
                ) : (
                    <NarrativeTimelineDemo key="timeline" />
                )}
            </AnimatePresence>

            {/* Background FX */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.05)_0%,transparent_70%)] pointer-events-none" />
        </div>
    </div>
  );
};

const FractalGoalDemo = () => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            className="w-full max-w-lg space-y-4"
        >
            {/* Main Goal */}
            <motion.div
                className="p-6 bg-zinc-800/80 rounded-xl border border-white/10 backdrop-blur-sm shadow-2xl"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
            >
                <div className="text-xs uppercase tracking-widest text-zinc-500 mb-1">The Impossible Goal</div>
                <h3 className="text-2xl font-display text-white">"Launch my Indie App"</h3>
            </motion.div>

            {/* Connecting Lines */}
            <div className="h-8 w-full flex justify-center relative">
                <div className="w-px h-full bg-zinc-700" />
                <div className="absolute bottom-0 w-[80%] h-px bg-zinc-700" />
            </div>

            {/* Split Level 1 */}
            <div className="grid grid-cols-3 gap-4">
                {['Design System', 'Core Engine', 'Market Strategy'].map((item, i) => (
                    <motion.div
                        key={item}
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.2 + (i * 0.1) }}
                        className="flex flex-col items-center"
                    >
                        <div className="w-px h-4 bg-zinc-700 mb-2" />
                        <div className="w-full p-4 bg-zinc-900 rounded-lg border border-zinc-800 text-center hover:border-blue-500/50 transition-colors">
                            <span className="text-sm text-zinc-300 font-medium">{item}</span>
                        </div>

                        {/* Recursive Micro tasks for the middle one */}
                        {i === 1 && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                transition={{ delay: 1 }}
                                className="flex flex-col items-center w-full pt-2"
                            >
                                <div className="w-px h-6 bg-blue-500/30" />
                                <div className="space-y-2 w-full">
                                    {['Setup Repo', 'Auth Flow', 'DB Schema'].map((sub, j) => (
                                        <motion.div
                                            key={sub}
                                            initial={{ x: -10, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ delay: 1.2 + (j * 0.1) }}
                                            className="flex items-center gap-2 p-2 rounded bg-blue-500/10 border border-blue-500/20"
                                        >
                                            <CheckCircle2 size={12} className="text-blue-400" />
                                            <span className="text-xs text-blue-200">{sub}</span>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
};

const NarrativeTimelineDemo = () => {
    const events = [
        { day: 1, title: 'The Awakening', desc: 'You accepted the call to adventure.', status: 'completed' },
        { day: 7, title: 'First Blood', desc: 'You shipped your first prototype despite fear.', status: 'completed' },
        { day: 15, title: 'The Valley of Doubt', desc: 'Progress slowed. You persisted anyway.', status: 'active' },
        { day: 30, title: 'Ascension', desc: 'Locked.', status: 'locked' },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="w-full max-w-xl relative"
        >
            <div className="absolute left-6 top-0 bottom-0 w-px bg-zinc-800" />

            <div className="space-y-8">
                {events.map((evt, i) => (
                    <motion.div
                        key={i}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: i * 0.2 }}
                        className="relative pl-16"
                    >
                        {/* Node */}
                        <div className={`absolute left-4 -translate-x-1/2 w-4 h-4 rounded-full border-2 z-10 bg-black ${
                            evt.status === 'completed' ? 'border-purple-500 bg-purple-500' :
                            evt.status === 'active' ? 'border-white bg-black' : 'border-zinc-700 bg-black'
                        }`}>
                            {evt.status === 'active' && <div className="absolute inset-0 rounded-full bg-white animate-ping opacity-50" />}
                        </div>

                        <div className={`p-4 rounded-xl border ${
                            evt.status === 'active' ? 'bg-zinc-900 border-white/20' : 'bg-transparent border-transparent'
                        }`}>
                            <div className="flex items-center gap-3 mb-1">
                                <span className="text-xs font-mono text-zinc-500 uppercase">Day {evt.day}</span>
                                {evt.status === 'completed' && <span className="text-[10px] px-1.5 py-0.5 bg-purple-900/30 text-purple-300 rounded">Chapter Closed</span>}
                            </div>
                            <h4 className={`text-lg font-display ${evt.status === 'locked' ? 'text-zinc-600' : 'text-white'}`}>{evt.title}</h4>
                            <p className="text-sm text-zinc-500 leading-relaxed">{evt.desc}</p>
                        </div>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
};

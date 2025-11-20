'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import { WorldType, NarrativeResponse } from '@/types/marketing';
import { generateNarrative } from '@/lib/services/narrative-service';

export const NarrativeDemo: React.FC = () => {
  const [goal, setGoal] = useState("");
  const [world, setWorld] = useState<WorldType>(WorldType.CYBER);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NarrativeResponse | null>(null);

  const handleGenerate = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setResult(null);

    // Artificial delay for dramatic effect if API is too fast
    const [data] = await Promise.all([
        generateNarrative(goal, world),
        new Promise(r => setTimeout(r, 1200))
    ]);

    setResult(data);
    setLoading(false);
  };

  return (
    <div className="w-full max-w-xl glass-panel rounded-2xl p-1 overflow-hidden relative group">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

        <div className="relative bg-zinc-950/80 rounded-xl p-6 md:p-8 border border-white/5">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 uppercase tracking-wider">
                    <Sparkles size={12} className="text-blue-400" />
                    <span>Reality Engine v2.5</span>
                </div>
                <select
                    value={world}
                    onChange={(e) => setWorld(e.target.value as WorldType)}
                    className="bg-transparent text-xs text-zinc-400 border-b border-zinc-800 focus:border-blue-500 outline-none pb-1 transition-colors cursor-pointer"
                >
                    {Object.values(WorldType).map(w => (
                        <option key={w} value={w}>{w}</option>
                    ))}
                </select>
            </div>

            {/* Input Area */}
            <div className="space-y-6">
                <div className="space-y-2">
                    <label className="text-sm text-zinc-400 block font-display">Current Objective</label>
                    <div className="relative">
                        <input
                            type="text"
                            value={goal}
                            onChange={(e) => setGoal(e.target.value)}
                            placeholder="e.g. Finish my portfolio website..."
                            className="w-full bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-3 text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
                            onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                        />
                        <button
                            onClick={handleGenerate}
                            disabled={loading || !goal}
                            className="absolute right-2 top-2 p-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
                        </button>
                    </div>
                </div>

                {/* Output Area */}
                <div className="min-h-[140px]">
                    <AnimatePresence mode="wait">
                        {result ? (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="space-y-3"
                            >
                                <h3 className="text-lg font-display font-medium text-white">{result.title}</h3>
                                <p className="text-zinc-400 leading-relaxed text-sm">{result.content}</p>
                                <div className="flex gap-2 pt-2">
                                    {result.tags.map((tag, i) => (
                                        <span key={i} className="text-[10px] px-2 py-1 rounded-full border border-zinc-800 text-zinc-500 uppercase tracking-wider">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="h-full flex flex-col items-center justify-center text-zinc-700 space-y-2 py-8"
                            >
                                <div className="w-12 h-12 rounded-full border border-zinc-800 flex items-center justify-center">
                                    <div className="w-1.5 h-1.5 bg-zinc-800 rounded-full" />
                                </div>
                                <p className="text-xs font-mono">Awaiting Input</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    </div>
  );
};

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Character } from '@/types/marketing';
import { Heart, Zap, Brain, Shield } from 'lucide-react';

const CHARACTERS: Character[] = [
  {
    id: 'eliza',
    name: 'Eliza',
    role: 'Emotional Navigator',
    description: 'She helps you process the emotional friction of starting. When you are paralyzed by perfectionism, she asks the question beneath the question.',
    domain: 'health',
    sampleQuote: "You're avoiding this task because you're afraid it won't be perfect. What if we just made a 'bad draft' first?",
    avatarColor: 'bg-rose-500 text-rose-100'
  },
  {
    id: 'thorne',
    name: 'Thorne',
    role: 'Tactical Sergeant',
    description: 'He breaks ambiguity into brute force mechanics. No sympathy, just physics. Good for when you need a drill instructor.',
    domain: 'craft',
    sampleQuote: "Emotions are noise. Action is signal. Set a timer for 300 seconds. Write one sentence. Go.",
    avatarColor: 'bg-amber-600 text-amber-100'
  },
  {
    id: 'lyra',
    name: 'Lyra',
    role: 'System Architect',
    description: 'She sees the constellation, not the star. She connects today\'s boring task to your 5-year arc to give you perspective.',
    domain: 'growth',
    sampleQuote: "This feels small, but it's a foundational node for your 'Author' identity. 1% clearer means 100% closer.",
    avatarColor: 'bg-cyan-500 text-cyan-100'
  },
  {
    id: 'elara',
    name: 'Elara',
    role: 'Community Weaver',
    description: 'Reminds you that you live in a world with others. When you isolate, she nudges you to signal the tribe.',
    domain: 'connection',
    sampleQuote: "You've been in deep work for 4 hours. The tribe needs your signal. Send one update to a peer now.",
    avatarColor: 'bg-purple-500 text-purple-100'
  }
];

const SCENARIOS = [
    "I'm too tired to work.",
    "I feel like an imposter.",
    "I don't know where to start."
];

export const Companions: React.FC = () => {
  const [activeId, setActiveId] = useState<string>(CHARACTERS[0].id);
  const [scenario, setScenario] = useState<string>(SCENARIOS[0]);
  const activeChar = CHARACTERS.find(c => c.id === activeId) || CHARACTERS[0];

  const getResponse = (charId: string, scen: string) => {
      if (charId === 'thorne') return "Fatigue is a feeling, not a fact. Do 5 minutes anyway.";
      if (charId === 'eliza') return "It's okay to be tired. Your body is asking for rest, or maybe a change of pace?";
      if (charId === 'lyra') return "Energy fluctuates. The system accounts for this. Let's switch to a low-energy maintenance task.";
      if (charId === 'elara') return "Maybe you're drained from solitude. Call a friend for 5 minutes to recharge.";
      return "Let's break this down.";
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
        <div className="mb-16 grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
                <h2 className="text-4xl md:text-5xl font-display font-semibold text-white mb-6">The Squad</h2>
                <p className="text-zinc-400 text-lg leading-relaxed">
                    Delight isn't a chatbot. It's a council of specialized agents.
                    Each represents a different facet of human drive: Empathy, Discipline, Vision, and Tribe.
                    <br/><br/>
                    They don't just cheerlead. They intervene.
                </p>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-12">
            {/* Character Selection List */}
            <div className="lg:col-span-4 flex flex-col gap-3">
                <div className="text-xs uppercase tracking-widest text-zinc-500 mb-2 font-mono">Select Agent</div>
                {CHARACTERS.map((char) => (
                    <button
                        key={char.id}
                        onClick={() => setActiveId(char.id)}
                        className={`w-full text-left px-5 py-4 rounded-xl border transition-all duration-300 group relative overflow-hidden ${
                            activeId === char.id
                                ? 'bg-zinc-800/80 border-zinc-700 text-white shadow-xl'
                                : 'bg-zinc-900/30 border-transparent text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300'
                        }`}
                    >
                        <div className="relative z-10 flex items-center gap-4">
                            <div className={`w-8 h-8 rounded-full ${char.avatarColor} flex items-center justify-center text-[10px] font-bold shadow-lg`}>
                                {char.name[0]}
                            </div>
                            <div>
                                <span className="block font-display tracking-wide text-base">{char.name}</span>
                                <span className="text-[10px] uppercase tracking-widest opacity-50">{char.role}</span>
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            {/* Interactive Chat Demo */}
            <div className="lg:col-span-8 relative h-auto min-h-[500px]">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeChar.id}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.98 }}
                        transition={{ duration: 0.3 }}
                        className="h-full w-full glass-panel rounded-2xl flex flex-col border-white/10 bg-zinc-950 shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                            <div className="flex items-center gap-4">
                                <div className={`w-12 h-12 rounded-full ${activeChar.avatarColor} flex items-center justify-center shadow-lg`}>
                                    {activeChar.domain === 'health' && <Heart size={20} fill="currentColor" />}
                                    {activeChar.domain === 'craft' && <Zap size={20} fill="currentColor" />}
                                    {activeChar.domain === 'growth' && <Brain size={20} fill="currentColor" />}
                                    {activeChar.domain === 'connection' && <Shield size={20} fill="currentColor" />}
                                </div>
                                <div>
                                    <h3 className="text-xl font-display text-white">{activeChar.name}</h3>
                                    <div className="flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"/>
                                        <span className="text-xs text-zinc-500 uppercase tracking-wider">Online</span>
                                    </div>
                                </div>
                            </div>
                            <div className="hidden md:block text-right max-w-xs">
                                <p className="text-xs text-zinc-500 leading-relaxed">{activeChar.description}</p>
                            </div>
                        </div>

                        {/* Chat Body */}
                        <div className="flex-1 p-6 md:p-8 flex flex-col gap-6 overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent">

                            {/* Simulating User Message */}
                            <div className="self-end max-w-[80%]">
                                <div className="text-[10px] text-zinc-500 mb-1 text-right uppercase tracking-widest">You</div>
                                <div className="bg-zinc-800 text-zinc-200 px-5 py-3 rounded-2xl rounded-tr-sm shadow-md border border-white/5">
                                    "{scenario}"
                                </div>
                            </div>

                            {/* Agent Response */}
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 }}
                                className="self-start max-w-[85%]"
                            >
                                <div className="text-[10px] text-zinc-500 mb-1 uppercase tracking-widest">{activeChar.name}</div>
                                <div className="bg-white/10 backdrop-blur-md text-white px-6 py-4 rounded-2xl rounded-tl-sm border border-white/10 shadow-xl">
                                    <p className="text-lg leading-relaxed">
                                        "{getResponse(activeChar.id, scenario)}"
                                    </p>
                                </div>
                            </motion.div>

                        </div>

                        {/* Scenario Selector Footer */}
                        <div className="p-4 border-t border-white/5 bg-black/40">
                            <div className="text-[10px] text-zinc-600 uppercase tracking-widest mb-2 px-2">Simulate Struggle</div>
                            <div className="flex flex-wrap gap-2">
                                {SCENARIOS.map(s => (
                                    <button
                                        key={s}
                                        onClick={() => setScenario(s)}
                                        className={`text-xs px-3 py-2 rounded-lg border transition-colors ${
                                            scenario === s
                                            ? 'bg-white text-black border-white font-medium'
                                            : 'bg-transparent text-zinc-500 border-zinc-800 hover:border-zinc-600'
                                        }`}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    </div>
  );
};

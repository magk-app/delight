'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, Swords } from 'lucide-react';

export const Psychology: React.FC = () => {
  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24 items-center">
        <div className="lg:col-span-5 space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/20 bg-amber-500/10 text-[10px] uppercase tracking-widest text-amber-500 mb-4">
                <Brain size={12} />
                The Science of Story
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                Your brain is <br/> wired for <span className="text-amber-500">adversity.</span>
            </h2>
            <p className="text-lg text-zinc-400 leading-relaxed">
                Neuroscience shows that dopamine isn't released when you complete a task—it's released when you perceive progress towards a meaningful goal.
            </p>
            <p className="text-lg text-zinc-400 leading-relaxed">
                Checklists feel like chores because they lack context. Stories feel like adventures because they have stakes. Delight hacks your dopamine system by turning "sending an email" into "forging an alliance".
            </p>

            <div className="pt-8 flex flex-col gap-4">
                <div className="flex gap-4 items-start">
                    <div className="p-2 bg-zinc-900 rounded-lg border border-zinc-800 text-zinc-400">
                        <Swords size={20} />
                    </div>
                    <div>
                        <h4 className="text-white font-medium mb-1">Adversity is Fuel</h4>
                        <p className="text-sm text-zinc-500">We reframe setbacks as plot twists, preventing the shame spiral.</p>
                    </div>
                </div>
                <div className="flex gap-4 items-start">
                    <div className="p-2 bg-zinc-900 rounded-lg border border-zinc-800 text-zinc-400">
                        <Sparkles size={20} />
                    </div>
                    <div>
                        <h4 className="text-white font-medium mb-1">Identity Shifting</h4>
                        <p className="text-sm text-zinc-500">You don't "do" tasks. You "become" the character who does them.</p>
                    </div>
                </div>
            </div>
        </div>

        <div className="lg:col-span-7 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 to-purple-500/10 blur-[100px] rounded-full" />
            <div className="relative bg-zinc-950/50 backdrop-blur-xl border border-white/10 rounded-2xl p-8 md:p-12">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-4 opacity-50 blur-[1px]">
                        <h3 className="text-xs uppercase tracking-widest text-zinc-500">The Old Way (ToDo Lists)</h3>
                        <div className="space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border border-zinc-700 rounded-sm" />
                                <span className="text-zinc-400 line-through">Email Boss</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border border-zinc-700 rounded-sm" />
                                <span className="text-zinc-400">Gym (Leg day)</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border border-zinc-700 rounded-sm" />
                                <span className="text-zinc-400">Study French</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4 relative">
                         <div className="absolute -left-8 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-amber-500/50 to-transparent hidden md:block" />
                         <h3 className="text-xs uppercase tracking-widest text-amber-500">The Delight Way</h3>

                         <div className="space-y-6">
                            <div className="bg-zinc-900/80 p-4 rounded-xl border border-amber-500/20 shadow-lg">
                                <div className="text-xs text-amber-500 uppercase tracking-wider mb-1">Mission: Career</div>
                                <div className="text-white font-medium">Secure the Alliance</div>
                                <div className="text-xs text-zinc-500 mt-1">Dispatch communique to leadership.</div>
                            </div>

                            <div className="bg-zinc-900/80 p-4 rounded-xl border border-white/5">
                                <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">Mission: Vitality</div>
                                <div className="text-zinc-300">Forge the Foundation</div>
                                <div className="text-xs text-zinc-500 mt-1">Strengthen lower pillars (Legs).</div>
                            </div>
                         </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

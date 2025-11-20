'use client';

import React from 'react';
import { motion } from 'framer-motion';

export const WhyDelight: React.FC = () => {
  return (
    <section className="relative w-full py-32 md:py-48 bg-zinc-950 overflow-hidden flex flex-col items-center justify-center">
      {/* Subtle Background Texture */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
          backgroundImage: 'radial-gradient(#333 1px, transparent 1px)',
          backgroundSize: '32px 32px'
      }} />

      <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black pointer-events-none" />

      <div className="max-w-5xl mx-auto px-6 relative z-10">
        <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative"
        >
            {/* Giant Background Text */}
            <h2 className="text-[15vw] leading-[0.8] font-display font-bold text-zinc-900/50 select-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none whitespace-nowrap blur-sm">
                MANIFESTO
            </h2>

            <div className="relative text-center space-y-16">
                <div className="space-y-6">
                    <p className="text-xs font-mono text-blue-500 uppercase tracking-[0.3em]">Why We Built This</p>

                    <h3 className="text-4xl md:text-6xl lg:text-7xl font-display font-medium text-white leading-[1.1]">
                        The world wants you to be a <br/>
                        <span className="text-zinc-600">Passive Consumer.</span>
                    </h3>
                </div>

                <div className="max-w-3xl mx-auto space-y-8 text-lg md:text-2xl text-zinc-400 leading-relaxed font-light text-left md:text-center">
                    <p>
                        We believe that ambition is the most precious resource on the planet.
                        Yet, the tools we use to manage it—to-do lists, calendars, spreadsheets—are
                        designed for robots, not humans.
                    </p>
                    <p>
                        <span className="text-white font-normal">Delight is different.</span> We use the psychology of video games
                        and the structure of narrative to turn your life into something playable.
                    </p>
                    <p>
                        Because when you feel like the protagonist of a story, you don't burn out.
                        You develop character.
                    </p>
                </div>

                <div className="pt-8 flex flex-wrap justify-center gap-4 md:gap-8">
                    <div className="flex items-center gap-3 px-6 py-3 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm text-sm text-zinc-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                        Identity over Productivity
                    </div>
                    <div className="flex items-center gap-3 px-6 py-3 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm text-sm text-zinc-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                        Story over Statistics
                    </div>
                    <div className="flex items-center gap-3 px-6 py-3 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm text-sm text-zinc-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Co-op over Solo
                    </div>
                </div>

                <div className="pt-12">
                     <p className="text-3xl font-signature text-white/60">The Delight Team</p>
                </div>
            </div>
        </motion.div>
      </div>
    </section>
  );
};

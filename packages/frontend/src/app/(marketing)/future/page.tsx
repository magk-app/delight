'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  Users,
  Gamepad2,
  Mic,
  BarChart3,
  Calendar,
  Sparkles,
  Network,
  Cpu,
  Heart,
  ArrowRight,
  Circle,
  CheckCircle2
} from 'lucide-react';

const FUTURE_TRACKS = [
  {
    id: 'social',
    theme: 'Multiplayer & Guild',
    icon: Users,
    status: 'exploring',
    color: 'text-purple-400',
    borderColor: 'border-purple-500/20',
    bgColor: 'bg-purple-500/10',
    items: [
      { title: 'Shared Accountability Zones', desc: 'Private spaces where small groups track progress together and celebrate wins without judgment.' },
      { title: 'Guild Economies', desc: 'Earn guild-specific currency through mentorship and collaboration. Unlock exclusive story arcs.' },
      { title: 'Mentor Matching', desc: 'Connect experienced practitioners with eager learners. Teaching deepens understanding.' },
    ]
  },
  {
    id: 'narrative',
    theme: 'Deeper Storytelling',
    icon: Gamepad2,
    status: 'prototyping',
    color: 'text-amber-400',
    borderColor: 'border-amber-500/20',
    bgColor: 'bg-amber-500/10',
    items: [
      { title: 'Multi-Chapter Arcs', desc: 'Your progress drives 3-5 chapter narratives with planned endings, plot twists, and callbacks.' },
      { title: 'Character Relationships', desc: 'Build trust with AI companions. Unlock deeper conversations and character-specific quests.' },
      { title: 'World Zones', desc: 'Unlock new locations—Arena, Observatory, Commons—each with unique missions and characters.' },
    ]
  },
  {
    id: 'voice',
    theme: 'Voice & Multimodal',
    icon: Mic,
    status: 'long-term',
    color: 'text-cyan-400',
    borderColor: 'border-cyan-500/20',
    bgColor: 'bg-cyan-500/10',
    items: [
      { title: 'Voice-First Briefings', desc: 'Start your day hands-free. Ask about priorities while making coffee or during commutes.' },
      { title: 'Emotional Tone Detection', desc: 'The companion adjusts based on how you sound—detecting stress, excitement, or fatigue.' },
      { title: 'Visual Evidence', desc: 'Capture photos of your work. Build a visual portfolio of your journey over time.' },
    ]
  },
  {
    id: 'analytics',
    theme: 'Deep Analytics',
    icon: BarChart3,
    status: 'exploring',
    color: 'text-blue-400',
    borderColor: 'border-blue-500/20',
    bgColor: 'bg-blue-500/10',
    items: [
      { title: 'Consistency Deep Dives', desc: 'Understand your patterns—when are you most productive? What triggers slumps?' },
      { title: 'Weekly Cinematic Recaps', desc: 'Auto-generated highlight reels showing your week: missions completed and growth achieved.' },
      { title: 'Trajectory Predictions', desc: 'Based on current momentum, see projected completion dates. Adjust intensity to hit targets.' },
    ]
  },
  {
    id: 'integration',
    theme: 'Tool Integrations',
    icon: Calendar,
    status: 'exploring',
    color: 'text-emerald-400',
    borderColor: 'border-emerald-500/20',
    bgColor: 'bg-emerald-500/10',
    items: [
      { title: 'Calendar Sync', desc: 'Let Delight see your calendar to suggest missions around meetings and respect deep work blocks.' },
      { title: 'GitHub/GitLab', desc: 'Automatically track coding missions via commits. Watch your constellation grow as you ship.' },
      { title: 'Creative Tools', desc: 'Track writing in Google Docs, designs in Figma. Your creative output drives narrative.' },
    ]
  },
  {
    id: 'agents',
    theme: 'Autonomous Agents',
    icon: Cpu,
    status: 'long-term',
    color: 'text-rose-400',
    borderColor: 'border-rose-500/20',
    bgColor: 'bg-rose-500/10',
    items: [
      { title: 'Research Agents', desc: 'Ask Delight to research topics and synthesize findings while you focus on execution.' },
      { title: 'Logistics Orchestration', desc: 'Schedule appointments, book travel, coordinate meetings. Reclaim your cognitive bandwidth.' },
      { title: 'Multi-Agent Collaboration', desc: 'Different AI characters specialize in domains and coordinate behind the scenes.' },
    ]
  },
];

const STATUS_META = {
  exploring: { label: 'Exploring', desc: 'Research, feedback, sketching prototypes', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  prototyping: { label: 'Prototyping', desc: 'Building early versions for pilot users', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  'long-term': { label: 'Long-term', desc: 'Ambitious ideas on the horizon', color: 'text-zinc-500 bg-zinc-800/50 border-zinc-700' },
};

export default function FuturePage() {
  const [activeTrack, setActiveTrack] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-black text-zinc-200">
      {/* Hero */}
      <section className="relative pt-48 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 via-black to-black" />
        <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-12 text-center"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] uppercase tracking-widest text-blue-400">
              <Sparkles size={12} />
              The Roadmap
            </div>

            <h1 className="text-6xl md:text-8xl font-display font-bold text-white leading-[0.9] tracking-tighter">
              The Future <br />
              <span className="text-zinc-600">of Delight.</span>
            </h1>

            <p className="text-2xl text-zinc-400 max-w-3xl mx-auto leading-relaxed">
              Where we're headed. What we're exploring. <br className="hidden md:block" />
              Ideas that could reshape ambitious people's relationship with their goals.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Intro */}
      <section className="py-16 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <p className="text-xl text-zinc-400 leading-relaxed text-center">
            Delight's MVP focuses on proving a humane single-player loop: remembered context, adaptive missions,
            visible progress, and compassionate outreach. <span className="text-white">But our vision extends far beyond that foundation</span>.
            Below are features we're exploring—grouped by theme, with rough statuses. Nothing here is promised.
          </p>
        </div>
      </section>

      {/* Roadmap Tracks */}
      <section className="py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="space-y-16">
            {FUTURE_TRACKS.map((track, idx) => {
              const Icon = track.icon;
              const isActive = activeTrack === track.id;

              return (
                <motion.div
                  key={track.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  onMouseEnter={() => setActiveTrack(track.id)}
                  onMouseLeave={() => setActiveTrack(null)}
                  className={`relative group ${isActive ? 'scale-[1.02]' : ''} transition-transform duration-300`}
                >
                  {/* Track Header */}
                  <div className="flex items-start gap-6 mb-8">
                    <div className={`p-4 rounded-xl ${track.bgColor} border ${track.borderColor} transition-all ${isActive ? 'scale-110' : ''}`}>
                      <Icon size={28} className={track.color} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h2 className="text-3xl font-display font-bold text-white">{track.theme}</h2>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border ${STATUS_META[track.status as keyof typeof STATUS_META].color}`}>
                          {STATUS_META[track.status as keyof typeof STATUS_META].label}
                        </span>
                      </div>
                      <p className="text-sm text-zinc-500">{STATUS_META[track.status as keyof typeof STATUS_META].desc}</p>
                    </div>
                  </div>

                  {/* Feature Cards */}
                  <div className="grid md:grid-cols-3 gap-6">
                    {track.items.map((item, itemIdx) => (
                      <motion.div
                        key={itemIdx}
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: idx * 0.1 + itemIdx * 0.05 }}
                        className={`bg-zinc-900/50 border ${track.borderColor} rounded-xl p-6 hover:bg-zinc-900/80 transition-all ${isActive ? 'border-opacity-100' : 'border-opacity-20'}`}
                      >
                        <h3 className="font-display font-bold text-white mb-3 text-lg">{item.title}</h3>
                        <p className="text-sm text-zinc-400 leading-relaxed">{item.desc}</p>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Status Legend */}
      <section className="py-16 bg-zinc-900/30 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h3 className="text-2xl font-display font-bold text-white mb-8 text-center">
            What these statuses mean
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            {Object.entries(STATUS_META).map(([key, meta]) => (
              <div key={key} className="bg-black/50 border border-white/5 rounded-xl p-6">
                <div className={`inline-flex px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border ${meta.color} mb-4`}>
                  {meta.label}
                </div>
                <p className="text-sm text-zinc-400 leading-relaxed">{meta.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold text-white">
              Help shape what <br />
              <span className="text-blue-500">gets built next.</span>
            </h2>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              The features that ship will be the ones that resonate most with early users.
              If something here excites you—we want to hear from you.
            </p>
          </motion.div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
            <Link
              href="/waitlist"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-black rounded-full font-medium hover:bg-zinc-200 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Join the Waitlist <ArrowRight size={16} />
            </Link>
            <Link
              href="/why"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white rounded-full font-medium hover:bg-white/10 transition-all"
            >
              Read the Manifesto
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

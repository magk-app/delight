'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Sparkles, Shield, Zap, Heart } from 'lucide-react';

export default function WhyPage() {
  return (
    <div className="min-h-screen bg-black text-zinc-200">
      {/* Hero Section */}
      <section className="relative pt-48 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-purple-900/10 via-black to-black" />
        <div className="absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-900/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-12 text-center"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] uppercase tracking-widest text-purple-400">
              <Sparkles size={12} />
              The Manifesto
            </div>

            <h1 className="text-6xl md:text-8xl font-display font-bold text-white leading-[0.9] tracking-tighter">
              Why Delight <br />
              <span className="text-zinc-600">Exists.</span>
            </h1>

            <p className="text-2xl text-zinc-400 max-w-3xl mx-auto leading-relaxed">
              A declaration for ambitious people who know what to do <br className="hidden md:block" />
              but can't seem to start.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Thesis Statements */}
      <section className="py-24 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <div className="space-y-32">
            {/* Statement 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-8 top-0 text-8xl font-display text-zinc-900 font-bold">01</div>
              <div className="relative space-y-6">
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                  Ambition is not the problem. <br />
                  <span className="text-amber-500">Emotional friction is.</span>
                </h2>
                <div className="space-y-6 text-lg text-zinc-400 leading-relaxed border-l border-white/10 pl-8">
                  <p>
                    You're ambitious. You set audacious goals. You know exactly what needs to be done.
                    But after lunch, or after a break, <span className="text-white">starting feels impossible</span>. Five minutes into focused work,
                    you're checking another tab.
                  </p>
                  <p>
                    This isn't laziness. It's not a character flaw. It's <span className="text-white font-medium">emotional friction</span>—the cognitive and
                    affective resistance that emerges when stress, overwhelm, and context switching collide with
                    complex goals.
                  </p>
                  <blockquote className="text-xl italic text-zinc-300 border-l-4 border-amber-500 pl-6 py-2">
                    "Your brain can't tell the difference between a difficult presentation and a physical danger."
                  </blockquote>
                  <p>
                    Traditional productivity tools don't address this. They focus on structure—lists, timers,
                    Kanban boards—but ignore the emotional state that determines whether you can even engage
                    with that structure.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Statement 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-8 top-0 text-8xl font-display text-zinc-900 font-bold">02</div>
              <div className="relative space-y-6">
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                  Tools that ignore your state <br />
                  <span className="text-blue-500">keep failing you.</span>
                </h2>
                <div className="space-y-6 text-lg text-zinc-400 leading-relaxed border-l border-white/10 pl-8">
                  <p>
                    DIY productivity systems demand constant maintenance exactly when you have the least bandwidth.
                    They're built for the version of you who has energy to spare. <span className="text-white">When life gets chaotic, they collapse</span>.
                  </p>
                  <p>
                    Generic AI assistants provide surface-level advice without understanding your unique context.
                    They reset every conversation, forcing you to re-explain your situation repeatedly.
                  </p>
                  <p>
                    Professional coaching is effective but expensive—and <span className="text-white font-medium">unavailable during the exact moments of
                    hesitation</span> when you need support most. That 3pm slump where you're staring at your screen?
                    Your coach isn't there.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Statement 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-8 top-0 text-8xl font-display text-zinc-900 font-bold">03</div>
              <div className="relative space-y-6">
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                  A companion that <br />
                  <span className="text-cyan-500">remembers.</span>
                </h2>
                <div className="space-y-6 text-lg text-zinc-400 leading-relaxed border-l border-white/10 pl-8">
                  <p>
                    Delight is designed to be what those other tools aren't: a companion that remembers. Not just
                    your tasks, but <span className="text-white font-medium">your journey. Your values. Your fears. Your patterns</span>.
                  </p>
                  <p>
                    When you open Delight after a difficult week, it doesn't greet you with a generic "What can I do for you today?"
                    It says: <span className="text-cyan-400 italic">"You've been quiet. Last time we talked, you were stressed about the presentation.
                    How did it go?"</span>
                  </p>

                  <div className="grid md:grid-cols-3 gap-4 my-8">
                    <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-xl">
                      <div className="text-xs text-zinc-500 uppercase tracking-widest mb-2">Personal</div>
                      <div className="text-sm text-white">Long-term context</div>
                    </div>
                    <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-xl">
                      <div className="text-xs text-zinc-500 uppercase tracking-widest mb-2">Project</div>
                      <div className="text-sm text-white">Goal evolution</div>
                    </div>
                    <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-xl">
                      <div className="text-xs text-zinc-500 uppercase tracking-widest mb-2">Task</div>
                      <div className="text-sm text-white">Mission details</div>
                    </div>
                  </div>

                  <blockquote className="text-xl italic text-zinc-300 border-l-4 border-cyan-500 pl-6 py-2">
                    "Trust isn't built in a single conversation. It's built when someone remembers what you told them last time."
                  </blockquote>
                </div>
              </div>
            </motion.div>

            {/* Statement 4 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-8 top-0 text-8xl font-display text-zinc-900 font-bold">04</div>
              <div className="relative space-y-6">
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                  A world, not <br />
                  <span className="text-purple-500">another list.</span>
                </h2>
                <div className="space-y-6 text-lg text-zinc-400 leading-relaxed border-l border-white/10 pl-8">
                  <p>
                    Productivity shouldn't feel like paperwork. For many ambitious people—especially those with ADHD tendencies or creative
                    mindsets—<span className="text-white">lists feel lifeless</span>. They don't inspire. They don't create meaning.
                  </p>
                  <p>
                    This is why Delight includes a narrative layer. Your work unfolds in a living world that
                    responds to your real-world progress. <span className="text-white font-medium">Complete missions, build relationships, unlock new zones</span>.
                  </p>
                  <p>
                    This isn't superficial gamification. When your actual work drives a story that surprises you,
                    when characters you've grown to care about acknowledge your effort—<span className="text-white">that creates genuine motivation</span>.
                    It turns "I should work on this" into "I want to see what happens next."
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Statement 5 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -left-8 top-0 text-8xl font-display text-zinc-900 font-bold">05</div>
              <div className="relative space-y-6">
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white leading-tight">
                  Privacy, cost, <br />
                  <span className="text-emerald-500">and trust.</span>
                </h2>
                <div className="space-y-6 text-lg text-zinc-400 leading-relaxed border-l border-white/10 pl-8">
                  <p>
                    When you share your emotional state, your goals, and your struggles with a tool, you're
                    extending <span className="text-white font-medium">enormous trust</span>. We don't take that lightly.
                  </p>

                  <div className="grid md:grid-cols-3 gap-4 my-8">
                    <div className="p-6 bg-zinc-900/50 border border-emerald-500/20 rounded-xl">
                      <Shield size={24} className="text-emerald-500 mb-3" />
                      <div className="text-sm font-medium text-white mb-2">Privacy First</div>
                      <div className="text-xs text-zinc-500">Opt-in tracking. Export anytime. You own your data.</div>
                    </div>
                    <div className="p-6 bg-zinc-900/50 border border-blue-500/20 rounded-xl">
                      <Zap size={24} className="text-blue-500 mb-3" />
                      <div className="text-sm font-medium text-white mb-2">Cost Efficient</div>
                      <div className="text-xs text-zinc-500">&lt;$0.10/user/day target. Accessible pricing.</div>
                    </div>
                    <div className="p-6 bg-zinc-900/50 border border-purple-500/20 rounded-xl">
                      <Heart size={24} className="text-purple-500 mb-3" />
                      <div className="text-sm font-medium text-white mb-2">Trust-Centered</div>
                      <div className="text-xs text-zinc-500">Your autonomy stays front and center. Always.</div>
                    </div>
                  </div>

                  <p>
                    Trust is the only defensible moat for a companion. If we betray that trust—through dark patterns,
                    surveillance, or exploitative pricing—we lose everything that makes Delight valuable.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="py-32 border-t border-white/5 bg-gradient-to-b from-black to-zinc-900">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold text-white">
              If this resonates, <br />
              <span className="text-blue-500">you're who we're building for.</span>
            </h2>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              We're in early development. The core loop is taking shape. The memory system works.
              But we need people willing to trust us with their goals and give honest feedback.
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
              href="/"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white rounded-full font-medium hover:bg-white/10 transition-all"
            >
              ← Explore the System
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

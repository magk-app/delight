'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Sparkles, Users, Mail, CheckCircle2, Zap, Heart, Shield } from 'lucide-react';

export default function WaitlistPage() {
  return (
    <div className="min-h-screen bg-black text-zinc-200">
      {/* Hero Section */}
      <section className="relative pt-48 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-900/10 via-black to-black" />
        <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-emerald-900/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-5xl mx-auto px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-12 text-center"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] uppercase tracking-widest text-emerald-400">
              <Sparkles size={12} />
              Join the Simulation
            </div>

            <h1 className="text-6xl md:text-8xl font-display font-bold text-white leading-[0.9] tracking-tighter">
              Enter <br />
              <span className="text-zinc-600">Early Access.</span>
            </h1>

            <p className="text-2xl text-zinc-400 max-w-3xl mx-auto leading-relaxed">
              Be among the first to experience an AI companion that <br className="hidden md:block" />
              transforms ambition into narrative momentum.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            {/* Left: Benefits & Profile */}
            <div className="space-y-12">
              {/* Benefits */}
              <div>
                <h2 className="text-3xl font-display font-bold text-white mb-8">
                  What You'll Receive
                </h2>
                <div className="space-y-6">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="flex gap-4 group"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Users className="w-7 h-7 text-emerald-400" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-white mb-2 text-lg">
                        Early Beta Access
                      </h3>
                      <p className="text-sm text-zinc-400 leading-relaxed">
                        Join pilot cohorts before public launch. Shape the product with your lived experience,
                        not abstract personas. Your journey informs our roadmap.
                      </p>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex gap-4 group"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Mail className="w-7 h-7 text-blue-400" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-white mb-2 text-lg">
                        Thoughtful Updates
                      </h3>
                      <p className="text-sm text-zinc-400 leading-relaxed">
                        No daily spam. No sales pressure. 1-2 meaningful emails per month when we hit milestones.
                        Honest communication about progress, setbacks, and learnings.
                      </p>
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 }}
                    className="flex gap-4 group"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Zap className="w-7 h-7 text-purple-400" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-white mb-2 text-lg">
                        Shape Direction
                      </h3>
                      <p className="text-sm text-zinc-400 leading-relaxed">
                        Your feedback directly influences features, priorities, and design. The roadmap items
                        that ship will be the ones that resonate with early users like you.
                      </p>
                    </div>
                  </motion.div>
                </div>
              </div>

              {/* Ideal User Profile */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="bg-zinc-900/50 border border-white/5 rounded-2xl p-8"
              >
                <h3 className="text-xl font-display font-bold text-white mb-6">
                  You're the ideal fit if...
                </h3>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-zinc-300 leading-relaxed">
                      You routinely set <span className="text-white font-medium">ambitious goals</span> but struggle
                      with emotional friction and consistency
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-zinc-300 leading-relaxed">
                      You're a <span className="text-white font-medium">founder, student, or creator</span> juggling
                      multiple complex priorities simultaneously
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-zinc-300 leading-relaxed">
                      You're willing to give <span className="text-white font-medium">honest, critical feedback</span>—
                      even when it stings
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-zinc-300 leading-relaxed">
                      You believe productivity tools should <span className="text-white font-medium">understand emotion</span>,
                      not ignore it
                    </span>
                  </li>
                </ul>
              </motion.div>

              {/* Trust Indicators */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-black/50 border border-white/5 rounded-xl text-center">
                  <Shield size={20} className="text-emerald-500 mx-auto mb-2" />
                  <div className="text-xs text-zinc-500 uppercase tracking-widest">Privacy</div>
                  <div className="text-sm text-white font-medium">First</div>
                </div>
                <div className="p-4 bg-black/50 border border-white/5 rounded-xl text-center">
                  <Heart size={20} className="text-purple-500 mx-auto mb-2" />
                  <div className="text-xs text-zinc-500 uppercase tracking-widest">Free Beta</div>
                  <div className="text-sm text-white font-medium">Access</div>
                </div>
                <div className="p-4 bg-black/50 border border-white/5 rounded-xl text-center">
                  <Zap size={20} className="text-blue-500 mx-auto mb-2" />
                  <div className="text-xs text-zinc-500 uppercase tracking-widest">Q1 2026</div>
                  <div className="text-sm text-white font-medium">Launch</div>
                </div>
              </div>
            </div>

            {/* Right: Form Embed */}
            <div className="lg:sticky lg:top-32">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="bg-zinc-900/80 backdrop-blur-xl border-2 border-emerald-500/20 rounded-3xl p-8 shadow-2xl"
              >
                <div className="mb-6">
                  <h3 className="text-2xl font-display font-bold text-white mb-2">
                    Reserve Your Spot
                  </h3>
                  <p className="text-sm text-zinc-400">
                    Takes less than 60 seconds. We respect your inbox.
                  </p>
                </div>

                {/* Google Form Embed */}
                <div className="rounded-2xl overflow-hidden border border-white/10 shadow-inner">
                  <iframe
                    src="https://docs.google.com/forms/d/e/1FAIpQLSek-5i4Kdd6iRTKEhTVD3pjI0AAtnZ9_cGajk6oFeEXlb998g/viewform?embedded=true"
                    width="100%"
                    height="800"
                    frameBorder="0"
                    marginHeight={0}
                    marginWidth={0}
                    className="w-full bg-white"
                  >
                    Loading…
                  </iframe>
                </div>

                <div className="mt-6">
                  <p className="text-xs text-zinc-500 text-center">
                    Can't see the form?{" "}
                    <a
                      href="https://docs.google.com/forms/d/e/1FAIpQLSek-5i4Kdd6iRTKEhTVD3pjI0AAtnZ9_cGajk6oFeEXlb998g/viewform"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-emerald-400 hover:text-emerald-300 transition-colors underline"
                    >
                      Open in new tab →
                    </a>
                  </p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-zinc-900/30 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-display font-bold text-white mb-12 text-center">
            Common Questions
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-black/50 border border-white/5 rounded-xl p-6"
            >
              <h3 className="font-display font-bold text-white mb-3">
                When will the beta start?
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                We're targeting early pilot cohorts in <span className="text-white">Q1 2026</span>.
                Exact timing depends on core loop stability and memory system performance.
                Waitlist members get 2+ weeks notice before their cohort starts.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-black/50 border border-white/5 rounded-xl p-6"
            >
              <h3 className="font-display font-bold text-white mb-3">
                How often will you email me?
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Very rarely. Expect <span className="text-white">1-2 emails per month</span> at most,
                and only when there's something meaningful—beta access opening, major features, or
                specific feedback requests. Unsubscribe anytime.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="bg-black/50 border border-white/5 rounded-xl p-6"
            >
              <h3 className="font-display font-bold text-white mb-3">
                Will early access be free?
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Yes. <span className="text-white">Pilot cohort members get free access</span> during
                the beta period. We're not asking you to pay for an unfinished product—we're asking
                you to invest time giving feedback. That's valuable enough.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="bg-black/50 border border-white/5 rounded-xl p-6"
            >
              <h3 className="font-display font-bold text-white mb-3">
                What if Delight doesn't work for me?
              </h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                <span className="text-white">That's important data.</span> If the core loop doesn't
                resonate, if the narrative feels gimmicky, if the AI misunderstands you—we want to know.
                Critical feedback is more valuable than polite praise.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="py-32 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-6 text-center space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold text-white">
              Want to learn more <br />
              <span className="text-emerald-500">before joining?</span>
            </h2>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Explore the system, read the philosophy, or see what we're building next.
            </p>
          </motion.div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white rounded-full font-medium hover:bg-white/10 transition-all"
            >
              ← Explore the System
            </Link>
            <Link
              href="/why"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white rounded-full font-medium hover:bg-white/10 transition-all"
            >
              Read the Manifesto
            </Link>
            <Link
              href="/future"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/20 text-white rounded-full font-medium hover:bg-white/10 transition-all"
            >
              See the Future <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

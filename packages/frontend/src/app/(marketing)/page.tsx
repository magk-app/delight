"use client";

import React from "react";
import { motion } from "framer-motion";
import { SectionFrame } from "@/components/marketing/ui/SectionFrame";
import { ScrollProgress } from "@/components/marketing/ui/ScrollProgress";
import { NarrativeDemo } from "@/components/marketing/NarrativeDemo";
import { MissionControl } from "@/components/marketing/MissionControl";
import { Companions } from "@/components/marketing/Companions";
import { Constellation } from "@/components/marketing/Constellation";
import { DailyLoop } from "@/components/marketing/DailyLoop";
import { WorldMap } from "@/components/marketing/WorldMap";
import { Psychology } from "@/components/marketing/Psychology";
import { FeatureDeepDive } from "@/components/marketing/FeatureDeepDive";
import { WhyDelight } from "@/components/marketing/WhyDelight";
import { CollaborativeStory } from "@/components/marketing/CollaborativeStory";
import { Twitter, Github, MoveUpRight, Play, Disc } from "lucide-react";
import Link from "next/link";

export default function MarketingHome() {
  return (
    <div className="min-h-screen bg-black text-zinc-200 selection:bg-blue-500/30 font-sans relative overflow-x-hidden">
      <ScrollProgress />

      {/* 01 HERO */}
      <main
        id="hero"
        className="pt-32 pb-24 md:pt-48 md:pb-32 relative overflow-hidden min-h-screen flex items-center"
      >
        <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />

        <SectionFrame className="grid grid-cols-1 lg:grid-cols-12 gap-12 md:gap-24 items-center">
          <div className="lg:col-span-7 space-y-12 relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] uppercase tracking-widest text-blue-300 mb-4">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              System v2.5 Online
            </div>

            <motion.h1
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="text-6xl sm:text-7xl md:text-9xl font-display font-semibold text-white leading-[0.85] tracking-tighter"
            >
              Ambition <br />
              <span className="text-zinc-600">Simulated.</span>
            </motion.h1>

            <div className="flex flex-col md:flex-row gap-8 md:items-start border-l border-white/10 pl-6 md:pl-8">
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.8 }}
                className="text-xl text-zinc-400 max-w-md leading-relaxed"
              >
                Turn your chaotic life goals into a cinematic, playable world.
                Delight wraps your daily tasks in narrative, psychology, and
                companion AI.
              </motion.p>

              <div className="flex gap-4">
                <button className="flex items-center justify-center w-14 h-14 rounded-full border border-white/20 hover:bg-white hover:text-black transition-all hover:scale-110 duration-300">
                  <Play size={18} fill="currentColor" />
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 relative z-20">
            <NarrativeDemo />
          </div>
        </SectionFrame>
      </main>

      {/* 02 PSYCHOLOGY */}
      <SectionFrame
        id="psychology"
        label="01 — The Science"
        className="min-h-screen flex items-center border-t border-white/5"
      >
        <Psychology />
      </SectionFrame>

      {/* 03 MECHANICS */}
      <SectionFrame
        id="mission"
        label="02 — Core Engine"
        className="min-h-screen flex flex-col justify-center border-t border-white/5 bg-zinc-900/10"
      >
        <div className="space-y-32">
          <FeatureDeepDive />
          <MissionControl />
        </div>
      </SectionFrame>

      {/* 04 SQUAD */}
      <SectionFrame
        id="squad"
        label="03 — The Squad"
        className="min-h-screen flex items-center border-t border-white/5"
      >
        <Companions />
      </SectionFrame>

      {/* 05 SOCIAL / WORLD */}
      <SectionFrame
        id="world"
        label="04 — Multiplayer"
        className="min-h-screen flex flex-col justify-center gap-32 border-t border-white/5 bg-zinc-900/10 py-32"
      >
        <WorldMap />
        <CollaborativeStory />
      </SectionFrame>

      {/* 06 GROWTH */}
      <SectionFrame
        id="growth"
        label="05 — Growth Engine"
        className="min-h-screen flex items-center border-t border-white/5"
      >
        <div className="space-y-32 w-full">
          <Constellation />
          <DailyLoop />
        </div>
      </SectionFrame>

      {/* 07 MANIFESTO */}
      <section id="manifesto">
        <WhyDelight />
      </section>

      {/* Footer */}
      <footer className="bg-black pt-24 pb-12 relative z-20">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-24">
          <div className="space-y-6">
            <h3 className="text-2xl font-display font-bold text-white">
              Delight.
            </h3>
            <p className="text-zinc-500 text-sm leading-relaxed">
              San Francisco, CA <br />
              Simulating since 2024.
            </p>
          </div>

          <div className="col-span-1 md:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">
                Platform
              </h4>
              <ul className="space-y-4 text-sm text-zinc-500">
                <li className="hover:text-white cursor-pointer transition-colors">
                  Narrative Engine
                </li>
                <li className="hover:text-white cursor-pointer transition-colors">
                  Psychology
                </li>
                <li className="hover:text-white cursor-pointer transition-colors">
                  Pricing
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">
                Guild
              </h4>
              <ul className="space-y-4 text-sm text-zinc-500">
                <li className="hover:text-white cursor-pointer transition-colors">
                  Discord
                </li>
                <li className="hover:text-white cursor-pointer transition-colors">
                  Twitter
                </li>
                <li className="hover:text-white cursor-pointer transition-colors">
                  <Link href="/why">Manifesto</Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">
                System
              </h4>
              <div className="flex items-center gap-2 text-emerald-500 text-sm font-mono">
                <Disc size={14} className="animate-spin-slow" />
                <span>Operational</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 border-t border-white/10 pt-8 flex justify-between items-center">
          <p className="text-[10px] text-zinc-700 uppercase tracking-widest">
            © 2025 Delight Systems Inc.
          </p>
          <div className="flex gap-6">
            <Twitter
              size={16}
              className="text-zinc-700 hover:text-white transition-colors cursor-pointer"
            />
            <Github
              size={16}
              className="text-zinc-700 hover:text-white transition-colors cursor-pointer"
            />
          </div>
        </div>
      </footer>
    </div>
  );
}

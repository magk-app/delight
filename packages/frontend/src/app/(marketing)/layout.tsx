'use client';

import React from 'react';
import Link from 'next/link';
import { Twitter, Github, MoveUpRight, Disc } from 'lucide-react';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black text-zinc-200 selection:bg-blue-500/30 font-sans relative overflow-x-hidden">
      {/* Fixed Navigation (Swiss Style) */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-6 flex justify-between items-center mix-blend-difference pointer-events-none">
        <Link href="/" className="flex items-center gap-2 pointer-events-auto group">
             <div className="w-4 h-4 bg-white rounded-sm group-hover:scale-110 transition-transform" />
             <div className="text-lg font-display font-bold tracking-tight text-white">Delight.</div>
        </Link>
        <Link
          href="/waitlist"
          className="pointer-events-auto text-xs bg-white text-black px-6 py-3 rounded-full font-medium hover:bg-zinc-200 transition-colors flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)] transform hover:scale-105 duration-300"
        >
          Enter Simulation <MoveUpRight size={12} />
        </Link>
      </nav>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="bg-black pt-24 pb-12 relative z-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-24">
            <div className="space-y-6">
                <h3 className="text-2xl font-display font-bold text-white">Delight.</h3>
                <p className="text-zinc-500 text-sm leading-relaxed">
                    San Francisco, CA <br/>
                    Simulating since 2024.
                </p>
            </div>

            <div className="col-span-1 md:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-8">
                <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">Platform</h4>
                    <ul className="space-y-4 text-sm text-zinc-500">
                        <li className="hover:text-white cursor-pointer transition-colors">
                          <Link href="/#psychology">Narrative Engine</Link>
                        </li>
                        <li className="hover:text-white cursor-pointer transition-colors">
                          <Link href="/#squad">The Squad</Link>
                        </li>
                        <li className="hover:text-white cursor-pointer transition-colors">
                          <Link href="/#world">Multiplayer</Link>
                        </li>
                    </ul>
                </div>
                <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">Guild</h4>
                    <ul className="space-y-4 text-sm text-zinc-500">
                        <li className="hover:text-white cursor-pointer transition-colors">Discord</li>
                        <li className="hover:text-white cursor-pointer transition-colors">Twitter</li>
                        <li className="hover:text-white cursor-pointer transition-colors">
                          <Link href="/why">Manifesto</Link>
                        </li>
                    </ul>
                </div>
                <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-widest mb-6">System</h4>
                    <div className="flex items-center gap-2 text-emerald-500 text-sm font-mono">
                        <Disc size={14} className="animate-spin-slow" />
                        <span>Operational</span>
                    </div>
                </div>
            </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 border-t border-white/10 pt-8 flex justify-between items-center">
            <p className="text-[10px] text-zinc-700 uppercase tracking-widest">© 2025 Delight Systems Inc.</p>
            <div className="flex gap-6">
                <Twitter size={16} className="text-zinc-700 hover:text-white transition-colors cursor-pointer" />
                <Github size={16} className="text-zinc-700 hover:text-white transition-colors cursor-pointer" />
            </div>
        </div>
      </footer>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Book, Sword, Coffee, Tent, Wifi, Radio } from 'lucide-react';

interface Zone {
  id: string;
  name: string;
  desc: string;
  count: number;
  icon: React.ElementType;
  x: number;
  y: number;
  color: string;
}

const ZONES: Zone[] = [
  { id: 'library', name: 'The Great Archive', desc: 'Deep Work • Silence Enforced', count: 432, icon: Book, x: 25, y: 35, color: 'text-cyan-400' },
  { id: 'arena', name: 'The Proving Grounds', desc: 'High Intensity • PvP Sprints', count: 156, icon: Sword, x: 70, y: 25, color: 'text-rose-400' },
  { id: 'hearth', name: 'The Hearth', desc: 'Social Lounge • Recovery', count: 89, icon: Coffee, x: 45, y: 65, color: 'text-amber-400' },
  { id: 'wilds', name: 'The Unknown', desc: 'Exploration • Quest Finding', count: 210, icon: Tent, x: 75, y: 70, color: 'text-emerald-400' },
];

export const WorldMap: React.FC = () => {
  const [activeZone, setActiveZone] = useState<string | null>(null);

  return (
    <div className="w-full flex flex-col gap-8">
        {/* Header / HUD */}
        <div className="flex flex-col md:flex-row justify-between items-end border-b border-white/10 pb-8">
            <div>
                <div className="flex items-center gap-2 text-blue-500 text-xs uppercase tracking-widest mb-2">
                    <Radio size={14} className="animate-pulse" />
                    Live Satellite Feed
                </div>
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white">
                    The Open World
                </h2>
            </div>
            <div className="flex items-center gap-6 text-zinc-500 font-mono text-xs">
                <div>
                    <span className="block text-white text-lg">1,842</span>
                    ONLINE
                </div>
                <div>
                    <span className="block text-white text-lg">4</span>
                    SECTORS
                </div>
                <div>
                    <span className="block text-emerald-400 text-lg">STABLE</span>
                    NETWORK
                </div>
            </div>
        </div>

        {/* Map Visualizer */}
        <div className="relative w-full aspect-[16/9] md:h-[650px] bg-[#030303] rounded-3xl border border-zinc-800 overflow-hidden shadow-2xl group">

            {/* Grid Background */}
            <div className="absolute inset-0 opacity-20" style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                backgroundSize: '80px 80px'
            }} />

            {/* Atmospheric Fog */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#000_120%)] pointer-events-none" />
            <motion.div
                animate={{ opacity: [0.3, 0.5, 0.3] }}
                transition={{ duration: 8, repeat: Infinity }}
                className="absolute top-[20%] left-[10%] w-96 h-96 bg-cyan-900/10 blur-[120px] rounded-full pointer-events-none"
            />
            <motion.div
                animate={{ opacity: [0.3, 0.5, 0.3] }}
                transition={{ duration: 8, delay: 4, repeat: Infinity }}
                className="absolute bottom-[10%] right-[10%] w-96 h-96 bg-purple-900/10 blur-[120px] rounded-full pointer-events-none"
            />

            {/* Connection Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
                <line x1="25%" y1="35%" x2="45%" y2="65%" stroke="white" strokeDasharray="5 5" />
                <line x1="45%" y1="65%" x2="75%" y2="70%" stroke="white" strokeDasharray="5 5" />
                <line x1="45%" y1="65%" x2="70%" y2="25%" stroke="white" strokeDasharray="5 5" />
            </svg>

            {/* Zones */}
            {ZONES.map((zone) => {
                const isActive = activeZone === zone.id;
                const Icon = zone.icon;

                return (
                    <div
                        key={zone.id}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-20"
                        style={{ left: `${zone.x}%`, top: `${zone.y}%` }}
                        onMouseEnter={() => setActiveZone(zone.id)}
                        onMouseLeave={() => setActiveZone(null)}
                    >
                        {/* Zone Marker */}
                        <motion.div
                             whileHover={{ scale: 1.1 }}
                             className={`relative w-20 h-20 rounded-full bg-zinc-950/80 border backdrop-blur-md flex items-center justify-center transition-all duration-500 ${isActive ? 'border-white shadow-[0_0_30px_rgba(255,255,255,0.3)]' : 'border-white/10'}`}
                        >
                            <Icon className={`w-8 h-8 ${zone.color}`} />

                            {/* Orbiting particles */}
                            {isActive && (
                                <motion.div
                                    className="absolute inset-[-10px] rounded-full border border-white/20 border-dashed"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 10, ease: "linear", repeat: Infinity }}
                                />
                            )}
                        </motion.div>

                         {/* Label */}
                         <div className={`mt-4 text-center transition-all duration-300 ${isActive ? 'opacity-100 translate-y-0' : 'opacity-60 translate-y-2'}`}>
                             <div className="text-base font-display font-bold text-white tracking-wide drop-shadow-md">{zone.name}</div>
                             <div className="text-[10px] text-zinc-400 uppercase tracking-widest flex items-center justify-center gap-2 mt-1">
                                <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-zinc-600'}`} />
                                {zone.count} Agents
                             </div>
                         </div>

                         {/* Tooltip Card */}
                         <AnimatePresence>
                             {isActive && (
                                 <motion.div
                                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="absolute bottom-full mb-6 left-1/2 -translate-x-1/2 w-64 bg-zinc-950 border border-white/20 p-5 rounded-xl pointer-events-none z-30 shadow-2xl"
                                 >
                                     <div className="text-xs font-bold text-white uppercase tracking-widest mb-2 border-b border-white/10 pb-2">{zone.name}</div>
                                     <p className="text-xs text-zinc-400 leading-relaxed mb-3">{zone.desc}</p>
                                     <div className="flex items-center gap-2 text-[10px] text-zinc-500">
                                         <Wifi size={10} /> Signal Strength: 100%
                                     </div>
                                 </motion.div>
                             )}
                         </AnimatePresence>
                    </div>
                );
            })}

            {/* Moving Dots (Users) - More of them, faster */}
            {[...Array(20)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-white rounded-full"
                    initial={{
                        x: Math.random() * 1000,
                        y: Math.random() * 600,
                        opacity: 0
                    }}
                    animate={{
                        x: [null, Math.random() * 1000],
                        y: [null, Math.random() * 600],
                        opacity: [0, 0.8, 0]
                    }}
                    transition={{
                        duration: 15 + Math.random() * 20,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                />
            ))}

            {/* Location UI Overlay */}
            <div className="absolute bottom-6 right-6 text-right pointer-events-none">
                <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">Current Sector</div>
                <div className="text-xl font-display font-bold text-white">NEO-TOKYO</div>
                <div className="text-xs text-zinc-600 font-mono">35.6762° N, 139.6503° E</div>
            </div>
        </div>
    </div>
  );
};

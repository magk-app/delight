'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';

// Each attribute is a "Branch" of the star system
interface Attribute {
  id: string;
  label: string;
  value: number;
  color: string;
  angle: number; // 0 to 360
}

export const Constellation: React.FC = () => {
  const [attributes, setAttributes] = useState<Attribute[]>([
    { id: 'growth', label: 'Intellect', value: 30, color: '#3b82f6', angle: 270 }, // Top
    { id: 'connection', label: 'Empathy', value: 40, color: '#a855f7', angle: 0 },   // Right
    { id: 'health', label: 'Vitality', value: 50, color: '#10b981', angle: 90 },   // Bottom
    { id: 'craft', label: 'Discipline', value: 60, color: '#f59e0b', angle: 180 },  // Left
  ]);

  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const handleLevelUp = (id: string) => {
    setAttributes(prev => prev.map(attr => {
      if (attr.id === id) {
        return { ...attr, value: Math.min(100, attr.value + 10) };
      }
      return attr;
    }));
  };

  // Calculate node position based on angle and distance (value)
  const getPosition = (angle: number, distance: number) => {
    const rad = (angle * Math.PI) / 180;
    // Base radius 150, max offset 120
    const cx = 200;
    const cy = 200;
    const r = (distance / 100) * 140;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad)
    };
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full">

        {/* Swiss Asymmetry: Description on left (4 cols) */}
        <div className="lg:col-span-4 flex flex-col justify-between h-full space-y-12">
            <div>
                <h2 className="text-4xl md:text-5xl font-display font-bold text-white mb-6 leading-[0.9]">
                    Your <br/> Expanding <br/> Universe.
                </h2>
                <p className="text-zinc-400 text-lg leading-relaxed">
                    Static profiles are dead. In Delight, your attributes are a living star system.
                    As you complete missions, your constellation physically expands, unlocking new capabilities in the network.
                </p>
            </div>

            <div className="space-y-4 border-t border-white/10 pt-8">
                <div className="text-xs uppercase tracking-widest text-zinc-500 mb-4">Evolution Controls</div>
                {attributes.map(attr => (
                    <button
                        key={attr.id}
                        onClick={() => handleLevelUp(attr.id)}
                        onMouseEnter={() => setHoveredNode(attr.id)}
                        onMouseLeave={() => setHoveredNode(null)}
                        className="group flex items-center justify-between w-full p-3 rounded-lg bg-zinc-900/40 border border-white/5 hover:border-white/20 hover:bg-zinc-800/40 transition-all"
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: attr.color }} />
                            <span className="font-mono text-sm text-zinc-300 uppercase tracking-wider">{attr.label}</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="h-1 w-16 bg-zinc-800 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full"
                                    style={{ backgroundColor: attr.color }}
                                    animate={{ width: `${attr.value}%` }}
                                />
                            </div>
                            <Plus size={14} className="text-zinc-500 group-hover:text-white transition-colors" />
                        </div>
                    </button>
                ))}
            </div>
        </div>

        {/* Visualization: The Star Map (8 cols) */}
        <div className="lg:col-span-8 relative aspect-square md:aspect-auto md:h-[600px] bg-black rounded-3xl border border-white/5 overflow-hidden flex items-center justify-center group">

            {/* Background Space Dust */}
            <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.1)_0%,transparent_60%)]" />
            <div className="absolute inset-0" style={{
                backgroundImage: 'radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px)',
                backgroundSize: '40px 40px',
                opacity: 0.1
            }} />

            <div className="relative w-[400px] h-[400px]">
                <svg width="400" height="400" className="overflow-visible">
                    {/* Core */}
                    <circle cx="200" cy="200" r="8" fill="white" className="animate-pulse-slow" />
                    <circle cx="200" cy="200" r="200" stroke="white" strokeWidth="1" strokeDasharray="4 4" className="opacity-5" />
                    <circle cx="200" cy="200" r="100" stroke="white" strokeWidth="1" strokeDasharray="4 4" className="opacity-10" />

                    {attributes.map((attr) => {
                        const endPos = getPosition(attr.angle, attr.value);
                        // Calculate milestone nodes along the path
                        const milestones = [0.3, 0.6, 0.9].map(p => ({
                            pos: getPosition(attr.angle, attr.value * p),
                            active: true
                        }));

                        return (
                            <g key={attr.id}>
                                {/* The main line connection */}
                                <motion.line
                                    x1="200"
                                    y1="200"
                                    animate={{ x2: endPos.x, y2: endPos.y }}
                                    stroke={attr.color}
                                    strokeWidth={hoveredNode === attr.id ? 3 : 1}
                                    className="transition-all duration-500 opacity-40"
                                />

                                {/* Milestone Nodes (The "Growing" part) */}
                                {milestones.map((m, idx) => (
                                    <motion.circle
                                        key={idx}
                                        cx={m.pos.x}
                                        cy={m.pos.y}
                                        r={hoveredNode === attr.id ? 4 : 2}
                                        fill={attr.color}
                                        initial={{ scale: 0 }}
                                        animate={{
                                            cx: m.pos.x,
                                            cy: m.pos.y,
                                            scale: 1,
                                            opacity: hoveredNode === attr.id ? 1 : 0.5
                                        }}
                                    />
                                ))}

                                {/* The Head Star */}
                                <motion.g
                                    animate={{ x: endPos.x, y: endPos.y }}
                                >
                                    <circle r="6" fill={attr.color} className="blur-[2px]" />
                                    <circle r="3" fill="white" />
                                    {/* Label floating near the star */}
                                    <text
                                        x="15"
                                        y="5"
                                        fill="white"
                                        className="text-[10px] font-mono uppercase tracking-widest opacity-50"
                                        style={{ textAnchor: 'start' }}
                                    >
                                        {attr.value}%
                                    </text>
                                </motion.g>
                            </g>
                        );
                    })}
                </svg>
            </div>

            {/* Decorative corner UI */}
            <div className="absolute top-6 right-6 text-right">
                <div className="text-[10px] text-zinc-500 uppercase tracking-widest">Total Mass</div>
                <div className="text-2xl font-display text-white">
                    {attributes.reduce((acc, curr) => acc + curr.value, 0)}.<span className="text-zinc-600">00</span>
                </div>
            </div>
        </div>
    </div>
  );
};

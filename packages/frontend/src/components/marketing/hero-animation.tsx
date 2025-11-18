"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export function HeroAnimation() {
  const [currentPhase, setCurrentPhase] = useState(0);
  const [narrativeText, setNarrativeText] = useState("");
  const [progress, setProgress] = useState(0);

  const narrativePhases = [
    "Day 5: You open Delight, feeling overwhelmed by your project backlog...",
    "Eliza greets you: 'Let's turn that anxiety into action. What matters most today?'",
    "Breaking down your presentation into three focused missions...",
  ];

  const missions = [
    { id: 1, title: "Research key points", time: "20 min", points: 15 },
    { id: 2, title: "Create outline", time: "30 min", points: 25 },
    { id: 3, title: "Design slides", time: "45 min", points: 40 },
  ];

  // Typewriter effect for narrative
  useEffect(() => {
    if (currentPhase >= narrativePhases.length) {
      // Restart animation
      const timer = setTimeout(() => {
        setCurrentPhase(0);
        setNarrativeText("");
        setProgress(0);
      }, 3000);
      return () => clearTimeout(timer);
    }

    const targetText = narrativePhases[currentPhase];
    let charIndex = 0;

    const typeInterval = setInterval(() => {
      if (charIndex < targetText.length) {
        setNarrativeText(targetText.slice(0, charIndex + 1));
        charIndex++;
      } else {
        clearInterval(typeInterval);
        // Move to next phase after completion
        setTimeout(() => {
          setCurrentPhase((prev) => prev + 1);
          setProgress((prev) => Math.min(prev + 33, 100));
        }, 1000);
      }
    }, 30);

    return () => clearInterval(typeInterval);
  }, [currentPhase]);

  return (
    <div className="space-y-6">
      {/* Narrative Typewriter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-secondary/10 border border-secondary/20 rounded-xl p-6 min-h-[120px] flex items-center"
      >
        <p className="text-sm text-foreground/90 font-medium leading-relaxed">
          {narrativeText}
          <motion.span
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 0.8, repeat: Infinity }}
            className="inline-block w-0.5 h-4 bg-secondary ml-1 align-middle"
          />
        </p>
      </motion.div>

      {/* Progress Ring */}
      <div className="flex items-center justify-between">
        <div className="relative">
          <svg className="w-24 h-24 transform -rotate-90">
            {/* Background circle */}
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="hsl(var(--muted))"
              strokeWidth="6"
              fill="none"
            />
            {/* Progress circle */}
            <motion.circle
              cx="48"
              cy="48"
              r="40"
              stroke="hsl(var(--primary))"
              strokeWidth="6"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 40}`}
              strokeDashoffset={`${2 * Math.PI * 40 * (1 - progress / 100)}`}
              initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 40 * (1 - progress / 100) }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg font-semibold text-foreground">{Math.round(progress)}%</span>
          </div>
        </div>

        <div className="flex-1 ml-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Today's Investment</span>
              <span className="text-primary font-medium">3 missions</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-success"
                initial={{ width: "0%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mission Breakdown */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {currentPhase >= 2 &&
            missions.map((mission, index) => (
              <motion.div
                key={mission.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.2 }}
                className="bg-card border border-border rounded-lg p-4 flex items-center justify-between hover:border-primary/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-semibold">{mission.id}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{mission.title}</p>
                    <p className="text-xs text-muted-foreground">{mission.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Progress</p>
                  <p className="text-sm font-semibold text-primary">+{mission.points} XP</p>
                </div>
              </motion.div>
            ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

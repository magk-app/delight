/**
 * Memory Notifications Component
 *
 * Shows real-time notifications when memories are being created/updated
 * - Appears as a side panel during chat
 * - Shows loading state while processing
 * - Displays created memories with animations
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Sparkles,
  Check,
  Loader2,
  Tag,
  Link2,
} from 'lucide-react';

interface Memory {
  id: string;
  content: string;
  memory_type: string;
  categories?: string[];
}

interface MemoryNotificationsProps {
  isProcessing: boolean;
  recentMemories: Memory[];
}

export function MemoryNotifications({
  isProcessing,
  recentMemories,
}: MemoryNotificationsProps) {
  if (!isProcessing && recentMemories.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="fixed right-4 top-24 w-80 max-h-[calc(100vh-200px)] overflow-hidden z-50"
    >
      <div className="bg-card/95 backdrop-blur-xl border border-border rounded-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-border bg-gradient-to-r from-primary/10 to-secondary/10">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            <h3 className="text-sm font-semibold text-white">Memory Processing</h3>
            {isProcessing && (
              <Loader2 className="w-4 h-4 text-primary animate-spin ml-auto" />
            )}
          </div>
        </div>

        {/* Content */}
        <div className="max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
          {/* Processing Indicator */}
          <AnimatePresence>
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="p-4 border-b border-border"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-primary/20 rounded-lg">
                    <Sparkles className="w-4 h-4 text-primary animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-primary/90">
                      Extracting facts...
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Analyzing your message and creating memories
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Recent Memories */}
          <div className="p-3 space-y-2">
            <AnimatePresence>
              {recentMemories.map((memory, index) => (
                <motion.div
                  key={memory.id}
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-3 bg-card/50 border border-success/20 rounded-lg"
                >
                  <div className="flex items-start gap-2">
                    <div className="p-1.5 bg-success/20 rounded">
                      <Check className="w-3.5 h-3.5 text-success" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-foreground/80 leading-relaxed">
                        {memory.content}
                      </p>

                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary/90 rounded-full font-medium">
                          {memory.memory_type}
                        </span>

                        {memory.categories && memory.categories.length > 0 && (
                          <div className="flex items-center gap-1">
                            <Tag className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">
                              {memory.categories.slice(0, 2).join(', ')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {recentMemories.length === 0 && !isProcessing && (
              <div className="text-center py-8">
                <Brain className="w-8 h-8 text-muted-foreground/50 mx-auto mb-2" />
                <p className="text-xs text-muted-foreground">No recent memories</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer Stats */}
        {recentMemories.length > 0 && (
          <div className="p-3 border-t border-border bg-card/50">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">
                {recentMemories.length} {recentMemories.length === 1 ? 'memory' : 'memories'} created
              </span>
              <span className="text-success font-medium">Active</span>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

/**
 * Edit Memory Modal Component
 *
 * Modal dialog for editing memory content
 * - Textarea for content editing
 * - Save and cancel buttons
 * - Dark theme glassmorphism design
 */

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Loader2 } from 'lucide-react';
import { Memory } from '@/lib/api/experimental-client';

interface EditMemoryModalProps {
  memory: Memory;
  onClose: () => void;
  onSave: (memoryId: string, content: string) => Promise<void>;
}

export function EditMemoryModal({ memory, onClose, onSave }: EditMemoryModalProps) {
  const [content, setContent] = useState(memory.content);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!content.trim()) {
      alert('Memory content cannot be empty');
      return;
    }

    setIsSaving(true);
    try {
      await onSave(memory.id, content);
    } catch (error) {
      // Error already handled by parent
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSave();
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-2xl mx-4 bg-slate-800/95 backdrop-blur-xl border border-slate-700/50 rounded-xl shadow-2xl overflow-hidden"
          onKeyDown={handleKeyDown}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50 bg-gradient-to-r from-purple-500/10 to-indigo-500/10">
            <h3 className="text-lg font-semibold text-white">Edit Memory</h3>
            <button
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all"
              disabled={isSaving}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="space-y-4">
              {/* Memory Type Badge */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                  Type:
                </span>
                <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {memory.memory_type}
                </span>
              </div>

              {/* Content Editor */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Content
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none"
                  rows={6}
                  placeholder="Enter memory content..."
                  disabled={isSaving}
                  autoFocus
                />
                <p className="mt-2 text-xs text-slate-500">
                  Press <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400">Esc</kbd> to cancel or{' '}
                  <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400">Cmd/Ctrl + Enter</kbd> to save
                </p>
              </div>

              {/* Categories (if available) */}
              {memory.metadata?.categories && memory.metadata.categories.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wide block mb-2">
                    Categories
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {memory.metadata.categories.map((category: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 rounded-md"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-700/50 bg-slate-900/30">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-all"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 rounded-lg transition-all shadow-lg shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSaving || !content.trim()}
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

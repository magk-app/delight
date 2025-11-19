/**
 * User Switcher Component
 *
 * Allows switching between different test users for development/testing
 * - Shows current user ID
 * - List of recent users
 * - Create new user button
 * - Clear current user button
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  ChevronDown,
  Plus,
  Trash2,
  Check,
  Copy,
} from 'lucide-react';

interface UserSwitcherProps {
  currentUserId: string;
  onUserChange: () => void;
}

export function UserSwitcher({ currentUserId, onUserChange }: UserSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [recentUsers, setRecentUsers] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load recent users from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const recent = JSON.parse(localStorage.getItem('recent_users') || '[]');
      setRecentUsers(recent);

      // Add current user to recent if not already there
      if (!recent.includes(currentUserId)) {
        const updated = [currentUserId, ...recent].slice(0, 5);
        localStorage.setItem('recent_users', JSON.stringify(updated));
        setRecentUsers(updated);
      }
    }
  }, [currentUserId]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const switchToUser = (userId: string) => {
    localStorage.setItem('experimental_user_id', userId);

    // Update recent users
    const updated = [userId, ...recentUsers.filter(id => id !== userId)].slice(0, 5);
    localStorage.setItem('recent_users', JSON.stringify(updated));
    setRecentUsers(updated);

    setIsOpen(false);
    onUserChange(); // Trigger page reload
  };

  const createNewUser = () => {
    const newId = crypto.randomUUID();
    switchToUser(newId);
  };

  const copyUserId = () => {
    navigator.clipboard.writeText(currentUserId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const clearCurrentUser = () => {
    if (confirm('Clear current user and create a new one?')) {
      createNewUser();
    }
  };

  return (
    <div className="relative z-[9999]" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-300 hover:text-white hover:border-purple-500/50 transition-all relative z-[9999]"
      >
        <User className="w-4 h-4" />
        <span className="text-xs font-mono">{currentUserId.slice(0, 8)}...</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed right-4 top-20 w-80 bg-slate-800/95 backdrop-blur-xl border border-slate-700/50 rounded-xl shadow-2xl z-[99999] overflow-hidden"
          >
            {/* Current User Section */}
            <div className="p-4 border-b border-slate-700/50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                  Current User
                </span>
                <button
                  onClick={copyUserId}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-slate-700/50 hover:bg-slate-700 rounded text-slate-300 hover:text-white transition-all"
                  title="Copy user ID"
                >
                  {copied ? (
                    <>
                      <Check className="w-3 h-3" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <div className="flex items-center gap-2 p-2 bg-slate-900/50 rounded-lg border border-purple-500/20">
                <User className="w-4 h-4 text-purple-400" />
                <span className="font-mono text-xs text-white flex-1 break-all">
                  {currentUserId}
                </span>
              </div>
            </div>

            {/* Recent Users Section */}
            {recentUsers.length > 1 && (
              <div className="p-4 border-b border-slate-700/50">
                <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">
                  Recent Users
                </div>
                <div className="space-y-1 max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                  {recentUsers
                    .filter(userId => userId !== currentUserId)
                    .map(userId => (
                      <button
                        key={userId}
                        onClick={() => switchToUser(userId)}
                        className="w-full text-left px-3 py-2 text-xs font-mono text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all flex items-center gap-2"
                      >
                        <User className="w-3 h-3 text-slate-500" />
                        <span className="flex-1 truncate">{userId}</span>
                      </button>
                    ))}
                </div>
              </div>
            )}

            {/* Actions Section */}
            <div className="p-4 space-y-2">
              <button
                onClick={createNewUser}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg font-medium text-sm transition-all shadow-lg shadow-purple-500/20"
              >
                <Plus className="w-4 h-4" />
                <span>New User</span>
              </button>

              <button
                onClick={clearCurrentUser}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded-lg font-medium text-sm transition-all border border-red-500/20"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear & Reset</span>
              </button>
            </div>

            {/* Info */}
            <div className="px-4 pb-3">
              <p className="text-xs text-slate-500">
                Switching users will reload the page with a different user ID. Memories are tied to each user.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

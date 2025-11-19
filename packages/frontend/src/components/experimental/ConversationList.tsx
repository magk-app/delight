/**
 * Conversation List Sidebar
 *
 * Displays list of all conversations for the current user
 * - Shows conversation titles with timestamps
 * - Highlights active conversation
 * - Delete conversations
 * - Create new conversation
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Plus,
  Trash2,
  Clock,
  ChevronRight,
  Archive,
} from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  message_count: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

interface ConversationListProps {
  userId: string;
  currentConversationId: string | null;
  onConversationSelect: (conversationId: string) => void;
  onNewConversation: () => void;
  refreshTrigger?: number; // Add refresh trigger
}

export function ConversationList({
  userId,
  currentConversationId,
  onConversationSelect,
  onNewConversation,
  refreshTrigger,
}: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConversations();
  }, [userId, refreshTrigger]); // Also refresh when refreshTrigger changes

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);

      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
      const data = await experimentalAPI.getConversations(userId, false);

      setConversations(data);
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
      setError(err.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (conversationId: string) => {
    if (!confirm('Delete this conversation? This cannot be undone.')) return;

    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
      await experimentalAPI.deleteConversation(conversationId);

      // Remove from list
      setConversations(prev => prev.filter(c => c.id !== conversationId));

      // If deleted current conversation, create new one
      if (conversationId === currentConversationId) {
        onNewConversation();
      }
    } catch (err: any) {
      console.error('Failed to delete conversation:', err);
      alert('Failed to delete conversation');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="h-full flex flex-col bg-slate-900/50 border-r border-slate-700/50">
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-400" />
            <h2 className="text-sm font-semibold text-white">Conversations</h2>
          </div>
          <span className="text-xs text-slate-500">{conversations.length}</span>
        </div>

        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg font-medium text-sm transition-all shadow-lg shadow-purple-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent p-2">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-slate-400 text-sm">Loading...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-red-400 text-sm">{error}</div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <MessageSquare className="w-12 h-12 text-slate-600 mb-3" />
            <p className="text-slate-400 text-sm">No conversations yet</p>
            <p className="text-slate-500 text-xs mt-1">Start chatting to create your first conversation</p>
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            <div className="space-y-1">
              {conversations.map(conversation => (
                <motion.div
                  key={conversation.id}
                  initial={{ opacity: 0, x: -10, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: -20, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="group relative overflow-hidden"
                >
                  <button
                    onClick={() => onConversationSelect(conversation.id)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      conversation.id === currentConversationId
                        ? 'bg-purple-500/20 border border-purple-500/30'
                        : 'hover:bg-slate-800/50 border border-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-sm font-medium truncate ${
                          conversation.id === currentConversationId
                            ? 'text-purple-300'
                            : 'text-slate-300 group-hover:text-white'
                        }`}>
                          {conversation.title}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-slate-500">
                            {conversation.message_count} messages
                          </span>
                          <span className="text-xs text-slate-600">•</span>
                          <span className="text-xs text-slate-500 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(conversation.updated_at)}
                          </span>
                        </div>
                      </div>

                      {conversation.id === currentConversationId && (
                        <ChevronRight className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>

                  {/* Delete button on hover */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conversation.id);
                    }}
                    className="absolute top-3 right-3 p-1.5 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-md opacity-0 group-hover:opacity-100 transition-all z-10"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-400" />
                  </button>
                </motion.div>
              ))}
            </div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

/**
 * Chat Interface Component (Modernized)
 *
 * Modern, minimalistic chat interface with:
 * - Lucide React icons (no emojis)
 * - Dark theme with glassmorphism
 * - Framer Motion animations
 * - Async memory processing indicator
 * - Progress bars for relevance scores
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Bot,
  AlertCircle,
  Send,
  Brain,
  Sparkles,
  Loader2,
  Database,
} from 'lucide-react';
import { SearchResult, Memory } from '@/lib/api/experimental-client';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  memories_retrieved?: SearchResult[];
  memories_created?: Memory[];
  loading?: boolean;
  processing_memories?: boolean; // For async memory processing
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'system',
      content: "Welcome! I'm your AI companion with memory. Start chatting and I'll remember our conversations.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    // Add loading message
    const loadingId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true,
      },
    ]);

    try {
      // Import the API client
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');

      // Prepare conversation history
      const conversationHistory = messages
        .filter(m => m.role !== 'system')
        .map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp.toISOString(),
        }));

      // Call the chat API
      const response = await experimentalAPI.sendChatMessage({
        message: userMessage.content,
        conversation_history: conversationHistory,
      });

      // Create assistant message from response
      const assistantMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        memories_retrieved: response.memories_retrieved.map(m => ({
          id: m.id,
          content: m.content,
          memory_type: m.memory_type,
          score: m.score || 0,
          metadata: { categories: m.categories || [] },
        })),
        memories_created: response.memories_created.map(m => ({
          id: m.id,
          content: m.content,
          memory_type: m.memory_type,
          user_id: 'current-user',
          metadata: { categories: m.categories || [] },
          created_at: new Date().toISOString(),
        })),
      };

      setMessages((prev) => prev.filter((m) => m.id !== loadingId).concat(assistantMessage));
    } catch (error) {
      console.error('Chat error:', error);

      // Show error message
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to connect to backend'}\n\nMake sure the experimental backend server is running on port 8001:\ncd packages/backend && poetry run python experiments/web/dashboard_server.py`,
        timestamp: new Date(),
      };

      setMessages((prev) => prev.filter((m) => m.id !== loadingId).concat(errorMessage));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl shadow-2xl overflow-hidden border border-slate-700/50">
      {/* Header with glassmorphism */}
      <div className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">AI Companion</h2>
            <p className="text-sm text-slate-400">
              Powered by memory-augmented intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area with custom scrollbar */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        <AnimatePresence mode="popLayout">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            >
              {/* Message Bubble */}
              <div
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                } mb-3`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/20'
                      : message.role === 'system'
                      ? 'bg-slate-800/50 backdrop-blur-sm text-slate-300 border border-slate-700/50'
                      : 'bg-slate-800/80 backdrop-blur-sm text-slate-100 border border-slate-700/50 shadow-lg'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className={`mt-0.5 ${message.role === 'user' ? 'text-white' : 'text-slate-400'}`}>
                      {message.role === 'user' ? (
                        <User className="w-5 h-5" />
                      ) : message.role === 'system' ? (
                        <AlertCircle className="w-5 h-5" />
                      ) : (
                        <Bot className="w-5 h-5" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      {message.loading ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                          <span className="text-sm text-slate-400">Thinking...</span>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">
                          {message.content}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Retrieved Memories */}
              {message.memories_retrieved && message.memories_retrieved.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ delay: 0.2 }}
                  className="ml-14 mt-3 space-y-2"
                >
                  <div className="flex items-center gap-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
                    <Brain className="w-3.5 h-3.5" />
                    <span>Context Retrieved ({message.memories_retrieved.length})</span>
                  </div>
                  <div className="space-y-2">
                    {message.memories_retrieved.map((memory, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * idx }}
                        className="group relative bg-slate-800/60 backdrop-blur-sm border border-purple-500/20 rounded-lg px-4 py-3 hover:border-purple-500/40 transition-all"
                      >
                        <div className="flex items-start gap-3">
                          {/* Relevance Score with Progress Bar */}
                          <div className="flex flex-col items-center gap-1 min-w-[48px]">
                            <span className="text-xs font-mono font-semibold text-purple-400">
                              {(memory.score * 100).toFixed(0)}%
                            </span>
                            <div className="w-full h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${memory.score * 100}%` }}
                                transition={{ duration: 0.6, delay: 0.2 * idx }}
                                className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
                              />
                            </div>
                          </div>

                          {/* Memory Content */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-slate-300 leading-relaxed">
                              {memory.content}
                            </p>
                            {memory.metadata?.categories && memory.metadata.categories.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 mt-2">
                                {memory.metadata.categories.slice(0, 3).map((cat, i) => (
                                  <span
                                    key={i}
                                    className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded-md"
                                  >
                                    {cat}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Created Memories */}
              {message.memories_created && message.memories_created.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ delay: 0.4 }}
                  className="ml-14 mt-3 space-y-2"
                >
                  <div className="flex items-center gap-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Knowledge Added ({message.memories_created.length})</span>
                  </div>
                  <div className="space-y-2">
                    {message.memories_created.map((memory, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * idx }}
                        className="bg-slate-800/60 backdrop-blur-sm border border-cyan-500/20 rounded-lg px-4 py-3 hover:border-cyan-500/40 transition-all"
                      >
                        <div className="flex items-start gap-2">
                          <Database className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-slate-300 leading-relaxed">
                            {memory.content}
                          </p>
                        </div>
                        {memory.metadata?.categories && memory.metadata.categories.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-2 ml-6">
                            {memory.metadata.categories.slice(0, 3).map((cat, i) => (
                              <span
                                key={i}
                                className="text-xs px-2 py-0.5 bg-cyan-500/20 text-cyan-300 rounded-md"
                              >
                                {cat}
                              </span>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Async Memory Processing Indicator */}
              {message.processing_memories && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="ml-14 mt-3"
                >
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Processing memories in background...</span>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800/50 backdrop-blur-xl border-t border-slate-700/50 px-6 py-4">
        <div className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isProcessing}
            className="flex-1 px-5 py-3 bg-slate-900/50 border border-slate-700/50 rounded-xl
                     text-slate-100 placeholder-slate-500
                     focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all"
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isProcessing}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium rounded-xl
                     hover:from-purple-500 hover:to-indigo-500
                     focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:ring-offset-2 focus:ring-offset-slate-900
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200
                     shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30
                     flex items-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span className="hidden sm:inline">Sending...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-3 flex items-center gap-2">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>I&apos;ll remember facts from our conversation and use them in future responses</span>
        </p>
      </div>
    </div>
  );
}

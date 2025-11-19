/**
 * Chat Interface Component
 *
 * Provides a chat interface similar to the CLI chatbot but in a web UI
 * - Chat with AI agent
 * - View retrieved memories
 * - See new memories created
 * - Real-time updates
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { SearchResult, Memory } from '@/lib/api/experimental-client';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  memories_retrieved?: SearchResult[];
  memories_created?: Memory[];
  loading?: boolean;
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
        content: 'Thinking...',
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
        content: `⚠️ Error: ${error instanceof Error ? error.message : 'Failed to connect to backend'}

Make sure the experimental backend server is running on port 8001:
cd packages/backend && poetry run python experiments/web/dashboard_server.py`,
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
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-xl font-semibold text-gray-800">Chat with AI Companion</h2>
        <p className="text-sm text-gray-600 mt-1">
          I can remember our conversations and use that context to help you
        </p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Message Bubble */}
            <div
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              } mb-2`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : message.role === 'system'
                    ? 'bg-gray-100 text-gray-800 border border-gray-200'
                    : 'bg-gray-50 text-gray-800 border border-gray-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg">
                    {message.role === 'user'
                      ? '👤'
                      : message.role === 'system'
                      ? 'ℹ️'
                      : '🤖'}
                  </span>
                  <div className="flex-1">
                    {message.loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Retrieved Memories */}
            {message.memories_retrieved && message.memories_retrieved.length > 0 && (
              <div className="ml-12 mt-2 space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  🧠 Memories Used ({message.memories_retrieved.length})
                </p>
                <div className="space-y-1">
                  {message.memories_retrieved.map((memory, idx) => (
                    <div
                      key={idx}
                      className="text-sm bg-purple-50 border border-purple-200 rounded px-3 py-2"
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-green-600 font-medium text-xs mt-0.5">
                          {memory.score.toFixed(2)}
                        </span>
                        <span className="text-gray-700">{memory.content}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Created Memories */}
            {message.memories_created && message.memories_created.length > 0 && (
              <div className="ml-12 mt-2 space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  ✨ New Memories Created ({message.memories_created.length})
                </p>
                <div className="space-y-1">
                  {message.memories_created.map((memory, idx) => (
                    <div
                      key={idx}
                      className="text-sm bg-cyan-50 border border-cyan-200 rounded px-3 py-2"
                    >
                      <span className="text-gray-700">{memory.content}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 px-6 py-4">
        <div className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send)"
            disabled={isProcessing}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isProcessing}
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? (
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              'Send'
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 Tip: I&apos;ll remember facts from our conversation and use them in future responses
        </p>
      </div>
    </div>
  );
}

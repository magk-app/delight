/**
 * Chat Interface with Sidebar
 *
 * Comprehensive chat interface with:
 * - Conversation list sidebar on the left
 * - Real-time memory notifications on the right
 * - Modern, futuristic, minimalistic design
 * - No emojis, only Lucide icons
 * - Warm glassmorphism effects
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Bot,
  Send,
  Brain,
  Sparkles,
  Loader2,
  MessageSquarePlus,
} from 'lucide-react';
import { SearchResult, Memory } from '@/lib/api/experimental-client';
import { ConversationList } from './ConversationList';
import { MemoryNotifications } from './MemoryNotifications';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  memories_retrieved?: SearchResult[];
  memories_created?: Memory[];
  loading?: boolean;
}

export function ChatInterfaceWithSidebar({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'system',
      content: "Welcome to your AI-powered second brain. I remember everything we discuss.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessingMemories, setIsProcessingMemories] = useState(false);
  const [recentMemories, setRecentMemories] = useState<Memory[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
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

  // Load or create conversation on mount
  useEffect(() => {
    loadOrCreateConversation();
  }, [userId]);

  const loadOrCreateConversation = async () => {
    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');

      // Check if there's a conversation ID in localStorage for this user
      const storageKey = `conversation_${userId}`;
      const storedConversationId = localStorage.getItem(storageKey);

      if (storedConversationId) {
        // Try to load existing conversation
        try {
          const conversation = await experimentalAPI.getConversation(storedConversationId);

          if (conversation.messages && conversation.messages.length > 0) {
            // Load messages from database
            const loadedMessages: Message[] = [
              {
                id: '0',
                role: 'system',
                content: "Conversation restored. Ready to continue.",
                timestamp: new Date(),
              },
              ...conversation.messages.map(msg => ({
                id: msg.id,
                role: msg.role,
                content: msg.content,
                timestamp: new Date(msg.created_at),
                memories_retrieved: msg.metadata?.memories_retrieved,
                memories_created: msg.metadata?.memories_created,
              }))
            ];

            setMessages(loadedMessages);
            setConversationId(conversation.id);
            return;
          }
        } catch (error) {
          console.warn('Failed to load conversation, creating new one:', error);
        }
      }

      // Create new conversation
      const newConversation = await experimentalAPI.createConversation(
        userId,
        `Chat ${new Date().toLocaleDateString()}`
      );
      setConversationId(newConversation.id);
      localStorage.setItem(storageKey, newConversation.id);
    } catch (error) {
      console.error('Failed to initialize conversation:', error);
    }
  };

  const handleConversationSelect = async (newConversationId: string) => {
    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
      const conversation = await experimentalAPI.getConversation(newConversationId);

      const loadedMessages: Message[] = [
        {
          id: '0',
          role: 'system',
          content: "Conversation loaded.",
          timestamp: new Date(),
        },
        ...conversation.messages.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at),
          memories_retrieved: msg.metadata?.memories_retrieved,
          memories_created: msg.metadata?.memories_created,
        }))
      ];

      setMessages(loadedMessages);
      setConversationId(newConversationId);
      localStorage.setItem(`conversation_${userId}`, newConversationId);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleNewConversation = async () => {
    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');
      const newConversation = await experimentalAPI.createConversation(
        userId,
        `Chat ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`
      );

      setConversationId(newConversation.id);
      localStorage.setItem(`conversation_${userId}`, newConversation.id);
      setMessages([
        {
          id: '0',
          role: 'system',
          content: "New conversation started.",
          timestamp: new Date(),
        },
      ]);
      setRefreshKey(prev => prev + 1); // Trigger conversation list refresh
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !conversationId) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      loading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      const { default: experimentalAPI } = await import('@/lib/api/experimental-client');

      // Send message to backend
      const response = await experimentalAPI.sendChatMessage({
        message: userMessage.content,
        user_id: userId,
        conversation_history: messages
          .filter(m => m.role !== 'system' && !m.loading)
          .map(m => ({ role: m.role, content: m.content, timestamp: m.timestamp.toISOString() }))
      });

      // Update messages with response
      setMessages(prev =>
        prev.filter(m => m.id !== loadingMessage.id).concat([
          {
            id: `assistant-${Date.now()}`,
            role: 'assistant',
            content: response.response,
            timestamp: new Date(response.timestamp),
            memories_retrieved: response.memories_retrieved,
            memories_created: response.memories_created,
          },
        ])
      );

      // Show memory processing notification
      if (response.memories_created && response.memories_created.length > 0) {
        setIsProcessingMemories(true);
        setRecentMemories(response.memories_created);

        // Hide notification after 5 seconds
        setTimeout(() => {
          setIsProcessingMemories(false);
          setTimeout(() => setRecentMemories([]), 300);
        }, 5000);
      }

      // Save both messages to database
      try {
        await experimentalAPI.saveMessage(conversationId, userId, 'user', userMessage.content);
        await experimentalAPI.saveMessage(
          conversationId,
          userId,
          'assistant',
          response.response,
          {
            memories_retrieved: response.memories_retrieved,
            memories_created: response.memories_created,
          }
        );
      } catch (saveError) {
        console.error('Failed to save messages:', saveError);
      }
    } catch (error: any) {
      console.error('Failed to send message:', error);

      // Show error message
      setMessages(prev =>
        prev.filter(m => m.id !== loadingMessage.id).concat([
          {
            id: `error-${Date.now()}`,
            role: 'system',
            content: `Error: ${error.message || 'Failed to send message. Please try again.'}`,
            timestamp: new Date(),
          },
        ])
      );
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
    <div className="flex h-[calc(100vh-16rem)] gap-4">
      {/* Left Sidebar - Conversation List */}
      <div className="w-80 flex-shrink-0">
        <ConversationList
          key={refreshKey}
          userId={userId}
          currentConversationId={conversationId}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-700/50 overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-slate-700/50 bg-gradient-to-r from-purple-500/10 to-indigo-500/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-lg">
                <Brain className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">AI Second Brain</h3>
                <p className="text-xs text-slate-400">Memory-augmented chat</p>
              </div>
            </div>

            <button
              onClick={handleNewConversation}
              className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-purple-300 hover:text-purple-200 transition-all text-sm"
            >
              <MessageSquarePlus className="w-4 h-4" />
              <span>New Chat</span>
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-slate-700/50 bg-slate-900/50">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isProcessing}
              className="flex-1 px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isProcessing}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-700 text-white rounded-lg font-medium transition-all disabled:cursor-not-allowed shadow-lg shadow-purple-500/20 disabled:shadow-none flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Right Side - Memory Notifications */}
      <AnimatePresence>
        {(isProcessingMemories || recentMemories.length > 0) && (
          <div className="w-80 flex-shrink-0">
            <MemoryNotifications
              isProcessing={false}
              recentMemories={recentMemories}
            />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// Chat Message Component
// ============================================================================

function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center"
      >
        <div className="px-4 py-2 bg-slate-800/30 border border-slate-700/30 rounded-lg text-slate-400 text-sm">
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
        isUser
          ? 'bg-gradient-to-br from-purple-500 to-indigo-600'
          : 'bg-gradient-to-br from-slate-700 to-slate-600'
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[70%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        {message.loading ? (
          <div className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
            <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
          </div>
        ) : (
          <>
            <div className={`px-4 py-3 rounded-lg ${
              isUser
                ? 'bg-gradient-to-r from-purple-600/20 to-indigo-600/20 border border-purple-500/30'
                : 'bg-slate-800/50 border border-slate-700/50'
            }`}>
              <p className="text-sm text-white leading-relaxed">{message.content}</p>
            </div>

            {/* Memory Indicators */}
            {!isUser && (message.memories_retrieved || message.memories_created) && (
              <div className="flex items-center gap-2 px-2">
                {message.memories_retrieved && message.memories_retrieved.length > 0 && (
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    <Brain className="w-3 h-3" />
                    <span>{message.memories_retrieved.length} recalled</span>
                  </div>
                )}
                {message.memories_created && message.memories_created.length > 0 && (
                  <div className="flex items-center gap-1 text-xs text-green-500">
                    <Sparkles className="w-3 h-3" />
                    <span>{message.memories_created.length} saved</span>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        <span className="text-xs text-slate-600 px-2">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
    </motion.div>
  );
}

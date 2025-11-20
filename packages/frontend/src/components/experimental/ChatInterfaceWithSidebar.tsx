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

"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Bot,
  Send,
  Brain,
  Sparkles,
  Loader2,
  MessageSquarePlus,
  Menu,
  X,
} from "lucide-react";
import { SearchResult, Memory } from "@/lib/api/experimental-client";
import { ConversationList } from "./ConversationList";
import { MemoryNotifications } from "./MemoryNotifications";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  memories_retrieved?: SearchResult[];
  memories_created?: Memory[];
  loading?: boolean;
}

export function ChatInterfaceWithSidebar({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0",
      role: "system",
      content:
        "Welcome to your AI-powered second brain. I remember everything we discuss.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessingMemories, setIsProcessingMemories] = useState(false);
  const [recentMemories, setRecentMemories] = useState<Memory[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const hasInitialized = useRef(false); // Prevent duplicate initialization

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const loadOrCreateConversation = useCallback(async () => {
    // Guard against concurrent calls
    if (isCreatingConversation) {
      console.log("⏳ Already creating/loading conversation, skipping...");
      return;
    }

    try {
      setIsCreatingConversation(true);
      const { default: experimentalAPI } = await import(
        "@/lib/api/experimental-client"
      );

      // Check if there's a conversation ID in localStorage for this user
      const storageKey = `conversation_${userId}`;
      const storedConversationId = localStorage.getItem(storageKey);

      console.log(
        `🔍 Checking for existing conversation: ${storedConversationId}`
      );

      if (storedConversationId) {
        // Try to load existing conversation
        try {
          const conversation = await experimentalAPI.getConversation(
            storedConversationId
          );

          console.log(
            `✅ Loaded conversation ${conversation.id} with ${conversation.message_count} messages`
          );

          if (conversation.messages && conversation.messages.length > 0) {
            // Load messages from database
            const loadedMessages: Message[] = [
              {
                id: "0",
                role: "system",
                content: "Conversation restored. Ready to continue.",
                timestamp: new Date(),
              },
              ...conversation.messages.map((msg) => ({
                id: msg.id,
                role: msg.role,
                content: msg.content,
                timestamp: new Date(msg.created_at),
                memories_retrieved: msg.metadata?.memories_retrieved,
                memories_created: msg.metadata?.memories_created,
              })),
            ];

            setMessages(loadedMessages);
            setConversationId(conversation.id);
            return;
          }

          // Conversation exists but has no messages - use it
          setConversationId(conversation.id);
          console.log(
            `✅ Using existing empty conversation ${conversation.id}`
          );
          return;
        } catch (error) {
          console.warn(
            "⚠️ Failed to load stored conversation, will create new one:",
            error
          );
          // Clear invalid conversation ID from storage
          localStorage.removeItem(storageKey);
        }
      }

      // Create new conversation only if we don't have one
      console.log("➕ Creating new conversation...");
      const newConversation = await experimentalAPI.createConversation(
        userId,
        `Chat ${new Date().toLocaleDateString()}`
      );
      setConversationId(newConversation.id);
      localStorage.setItem(storageKey, newConversation.id);
      setRefreshKey((prev) => prev + 1); // Trigger conversation list refresh
      console.log(`✅ Created new conversation ${newConversation.id}`);
    } catch (error) {
      console.error("❌ Failed to initialize conversation:", error);
    } finally {
      setIsCreatingConversation(false);
    }
  }, [userId, isCreatingConversation]);

  // Load or create conversation on mount (with duplicate prevention)
  useEffect(() => {
    // Only initialize once per userId
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      loadOrCreateConversation();
    }

    // Cleanup on unmount or userId change
    return () => {
      if (hasInitialized.current) {
        hasInitialized.current = false;
      }
    };
  }, [userId, loadOrCreateConversation]);

  const handleConversationSelect = async (newConversationId: string) => {
    try {
      const { default: experimentalAPI } = await import(
        "@/lib/api/experimental-client"
      );
      const conversation = await experimentalAPI.getConversation(
        newConversationId
      );

      const loadedMessages: Message[] = [
        {
          id: "0",
          role: "system",
          content: "Conversation loaded.",
          timestamp: new Date(),
        },
        ...(conversation.messages || []).map((msg) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at),
          memories_retrieved: msg.metadata?.memories_retrieved,
          memories_created: msg.metadata?.memories_created,
        })),
      ];

      setMessages(loadedMessages);
      setConversationId(newConversationId);
      localStorage.setItem(`conversation_${userId}`, newConversationId);
    } catch (error) {
      console.error("Failed to load conversation:", error);
    }
  };

  // Poll for newly created memories (created in background)
  const pollForNewMemories = async (userId: string) => {
    let pollCount = 0;
    const maxPolls = 10; // Poll for 20 seconds (10 polls * 2 seconds) - increased from 5
    let lastMemoryIds = new Set<string>(); // Track memory IDs instead of count

    const poll = async () => {
      try {
        const { default: experimentalAPI } = await import(
          "@/lib/api/experimental-client"
        );
        const memories = await experimentalAPI.getMemories({
          user_id: userId,
          limit: 20,
        });

        // Find truly new memories by comparing IDs
        const newMemories = memories.filter((m) => !lastMemoryIds.has(m.id));

        if (newMemories.length > 0) {
          console.log(
            `📥 Detected ${newMemories.length} new memories, adding incrementally...`
          );

          // Add memories one at a time with animation delay
          for (let i = 0; i < newMemories.length; i++) {
            const mem = newMemories[i];
            setTimeout(() => {
              setRecentMemories((prev) => {
                // Avoid duplicates
                if (prev.find((m) => m.id === mem.id)) return prev;
                console.log(
                  `✨ Adding memory: ${mem.content.substring(0, 50)}...`
                );
                return [mem, ...prev]; // Add to beginning for newest-first display
              });
            }, i * 500); // 500ms delay between each memory for smooth animation
          }

          // Update tracking set
          memories.forEach((m) => lastMemoryIds.add(m.id));

          // Calculate notification duration based on number of memories
          // Base: 5 seconds, +2 seconds per memory, max 15 seconds
          const notificationDuration = Math.min(
            5000 + newMemories.length * 2000,
            15000
          );

          // Stop processing indicator after all memories are added
          setTimeout(() => {
            setIsProcessingMemories(false);
          }, newMemories.length * 500);

          // Hide notification after appropriate duration
          setTimeout(() => {
            setRecentMemories([]);
          }, notificationDuration);

          // Continue polling in case more memories are created
          pollCount++;
          if (pollCount < maxPolls) {
            setTimeout(poll, 2000);
          }
        } else {
          // No new memories yet, continue polling
          pollCount++;
          if (pollCount < maxPolls) {
            setTimeout(poll, 2000);
          } else {
            // Stop polling after max attempts
            console.log("⏹️ Stopped polling for memories (timeout)");
            setIsProcessingMemories(false);
          }
        }
      } catch (error) {
        console.error("Error polling for memories:", error);
        setIsProcessingMemories(false);
      }
    };

    // Get initial memory IDs
    try {
      const { default: experimentalAPI } = await import(
        "@/lib/api/experimental-client"
      );
      const initialMemories = await experimentalAPI.getMemories({
        user_id: userId,
        limit: 20,
      });
      initialMemories.forEach((m) => lastMemoryIds.add(m.id));
      console.log(`📊 Initial memory count: ${initialMemories.length}`);
    } catch (error) {
      console.error("Error getting initial memories:", error);
    }

    // Start polling after 1.5 seconds (give background task time to start)
    setTimeout(poll, 1500);
  };

  const handleNewConversation = async () => {
    // Guard against concurrent creation
    if (isCreatingConversation) {
      console.log("⏳ Already creating conversation, skipping...");
      return;
    }

    try {
      setIsCreatingConversation(true);
      console.log("➕ Creating new conversation (manual)...");

      const { default: experimentalAPI } = await import(
        "@/lib/api/experimental-client"
      );
      const newConversation = await experimentalAPI.createConversation(
        userId,
        `Chat ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`
      );

      console.log(`✅ Created new conversation ${newConversation.id}`);

      setConversationId(newConversation.id);
      localStorage.setItem(`conversation_${userId}`, newConversation.id);
      setMessages([
        {
          id: "0",
          role: "system",
          content: "New conversation started.",
          timestamp: new Date(),
        },
      ]);
      setRefreshKey((prev) => prev + 1); // Trigger conversation list refresh
    } catch (error) {
      console.error("❌ Failed to create conversation:", error);
      alert("Failed to create new conversation. Please try again.");
    } finally {
      setIsCreatingConversation(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !conversationId) return;

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      loading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInput("");
    setIsProcessing(true);

    try {
      const { default: experimentalAPI } = await import(
        "@/lib/api/experimental-client"
      );

      // Send message to backend
      const response = await experimentalAPI.sendChatMessage({
        message: userMessage.content,
        user_id: userId,
        conversation_history: messages
          .filter((m) => m.role !== "system" && !m.loading)
          .map((m) => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp.toISOString(),
          })),
      });

      // Update messages with response
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== loadingMessage.id)
          .concat([
            {
              id: `assistant-${Date.now()}`,
              role: "assistant",
              content: response.response,
              timestamp: new Date(response.timestamp),
              memories_retrieved: response.memories_retrieved.map((m) => ({
                id: m.id,
                content: m.content,
                memory_type: m.memory_type,
                score: m.score || 0,
                metadata: { categories: m.categories || [] },
              })),
              memories_created: response.memories_created.map((m) => ({
                id: m.id,
                content: m.content,
                memory_type: m.memory_type,
                user_id: "current-user",
                metadata: { categories: m.categories || [] },
                created_at: new Date().toISOString(),
              })),
            },
          ])
      );

      // Show memory processing notification
      if (response.memories_created && response.memories_created.length > 0) {
        console.log(
          `📥 Received ${response.memories_created.length} memories in response, adding incrementally...`
        );
        setIsProcessingMemories(true);

        // Add memories one at a time for transparency
        response.memories_created.forEach((mem, index) => {
          setTimeout(() => {
            setRecentMemories((prev) => {
              // Avoid duplicates
              if (prev.find((m) => m.id === mem.id)) return prev;
              console.log(
                `✨ Adding memory ${index + 1}/${
                  response.memories_created.length
                }: ${mem.content.substring(0, 50)}...`
              );
              const fullMemory = {
                id: mem.id,
                content: mem.content,
                memory_type: mem.memory_type,
                user_id: "current-user",
                metadata: { categories: mem.categories || [] },
                created_at: new Date().toISOString(),
              };
              return [fullMemory, ...prev]; // Add to beginning for newest-first display
            });
          }, index * 500); // 500ms delay between each memory
        });

        // Stop processing indicator after all memories are added
        const addDuration = response.memories_created.length * 500;
        setTimeout(() => {
          setIsProcessingMemories(false);
        }, addDuration);

        // Calculate notification duration: base 5s + 2s per memory, max 15s
        const notificationDuration = Math.min(
          5000 + response.memories_created.length * 2000,
          15000
        );
        setTimeout(() => {
          setRecentMemories([]);
        }, addDuration + notificationDuration);
      } else {
        // Memories are created in background - poll for them
        console.log(
          "📋 Memories being created in background, starting polling..."
        );
        setIsProcessingMemories(true);
        pollForNewMemories(userId);
      }

      // Save both messages to database
      try {
        await experimentalAPI.saveMessage(
          conversationId,
          userId,
          "user",
          userMessage.content
        );
        await experimentalAPI.saveMessage(
          conversationId,
          userId,
          "assistant",
          response.response,
          {
            memories_retrieved: response.memories_retrieved.map((m) => ({
              id: m.id,
              content: m.content,
              memory_type: m.memory_type,
              score: m.score || 0,
              metadata: { categories: m.categories || [] },
            })),
            memories_created: response.memories_created.map((m) => ({
              id: m.id,
              content: m.content,
              memory_type: m.memory_type,
              user_id: "current-user",
              metadata: { categories: m.categories || [] },
              created_at: new Date().toISOString(),
            })),
          }
        );
      } catch (saveError) {
        console.error("Failed to save messages:", saveError);
      }
    } catch (error: any) {
      console.error("Failed to send message:", error);

      // Show error message
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== loadingMessage.id)
          .concat([
            {
              id: `error-${Date.now()}`,
              role: "system",
              content: `Error: ${
                error.message || "Failed to send message. Please try again."
              }`,
              timestamp: new Date(),
            },
          ])
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] sm:h-[calc(100vh-16rem)] gap-2 sm:gap-4 relative">
      {/* Mobile Sidebar Overlay */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black/50 z-40 sm:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Left Sidebar - Conversation List */}
      <div
        className={`${
          showSidebar ? "translate-x-0" : "-translate-x-full"
        } sm:translate-x-0 fixed sm:static left-0 top-0 bottom-0 z-50 sm:z-auto w-80 flex-shrink-0 transition-transform duration-300 sm:transition-none`}
      >
        <div className="h-full bg-slate-900/95 sm:bg-slate-900/50 backdrop-blur-xl sm:backdrop-blur-none">
          <ConversationList
            userId={userId}
            currentConversationId={conversationId}
            onConversationSelect={(id) => {
              handleConversationSelect(id);
              setShowSidebar(false);
            }}
            onNewConversation={() => {
              handleNewConversation();
              setShowSidebar(false);
            }}
            refreshTrigger={refreshKey}
          />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-700/50 overflow-hidden min-w-0">
        {/* Chat Header */}
        <div className="p-3 sm:p-4 border-b border-slate-700/50 bg-gradient-to-r from-purple-500/10 to-indigo-500/10">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="sm:hidden p-1.5 hover:bg-slate-800/50 rounded-lg transition-all"
              >
                <Menu className="w-5 h-5 text-slate-300" />
              </button>
              <div className="p-1.5 sm:p-2 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-lg">
                <Brain className="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" />
              </div>
              <div className="min-w-0">
                <h3 className="text-xs sm:text-sm font-semibold text-white truncate">
                  AI Second Brain
                </h3>
                <p className="text-[10px] sm:text-xs text-slate-400 hidden sm:block">
                  Memory-augmented chat
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowMemoryPanel(!showMemoryPanel)}
                className="sm:hidden p-1.5 hover:bg-slate-800/50 rounded-lg transition-all relative"
              >
                <Brain className="w-5 h-5 text-purple-400" />
                {(isProcessingMemories || recentMemories.length > 0) && (
                  <span className="absolute top-0 right-0 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                )}
              </button>
              <button
                onClick={handleNewConversation}
                className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-purple-300 hover:text-purple-200 transition-all text-xs sm:text-sm"
              >
                <MessageSquarePlus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">New Chat</span>
                <span className="sm:hidden">New</span>
              </button>
            </div>
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
        <div className="p-2 sm:p-4 border-t border-slate-700/50 bg-slate-900/50">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isProcessing}
              className="flex-1 px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base bg-slate-800/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isProcessing}
              className="px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-700 text-white rounded-lg font-medium transition-all disabled:cursor-not-allowed shadow-lg shadow-purple-500/20 disabled:shadow-none flex items-center gap-1.5 sm:gap-2 text-sm sm:text-base"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Right Side - Memory Notifications (Desktop) */}
      <AnimatePresence>
        {(isProcessingMemories || recentMemories.length > 0) && (
          <>
            {/* Desktop */}
            <div className="hidden sm:block w-80 flex-shrink-0">
              <MemoryNotifications
                isProcessing={isProcessingMemories}
                recentMemories={recentMemories}
              />
            </div>
            {/* Mobile - Overlay */}
            {showMemoryPanel && (
              <>
                <div
                  className="sm:hidden fixed inset-0 bg-black/50 z-40"
                  onClick={() => setShowMemoryPanel(false)}
                />
                <div className="sm:hidden fixed right-0 top-0 bottom-0 w-80 z-50">
                  <MemoryNotifications
                    isProcessing={isProcessingMemories}
                    recentMemories={recentMemories}
                  />
                </div>
              </>
            )}
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// Chat Message Component
// ============================================================================

function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

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
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isUser
            ? "bg-gradient-to-br from-purple-500 to-indigo-600"
            : "bg-gradient-to-br from-slate-700 to-slate-600"
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`flex-1 max-w-[85%] sm:max-w-[70%] ${
          isUser ? "items-end" : "items-start"
        } flex flex-col gap-1`}
      >
        {message.loading ? (
          <div className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg">
            <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
          </div>
        ) : (
          <>
            <div
              className={`px-3 sm:px-4 py-2 sm:py-3 rounded-lg ${
                isUser
                  ? "bg-gradient-to-r from-purple-600/20 to-indigo-600/20 border border-purple-500/30"
                  : "bg-slate-800/50 border border-slate-700/50"
              }`}
            >
              <p className="text-xs sm:text-sm text-white leading-relaxed break-words">
                {message.content}
              </p>
            </div>

            {/* Memory Indicators */}
            {!isUser &&
              (message.memories_retrieved || message.memories_created) && (
                <div className="flex items-center gap-2 px-2">
                  {message.memories_retrieved &&
                    message.memories_retrieved.length > 0 && (
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Brain className="w-3 h-3" />
                        <span>
                          {message.memories_retrieved.length} recalled
                        </span>
                      </div>
                    )}
                  {message.memories_created &&
                    message.memories_created.length > 0 && (
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

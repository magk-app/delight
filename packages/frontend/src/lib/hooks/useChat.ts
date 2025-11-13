/**
 * useChat Hook - SSE-based chat with Eliza
 *
 * Manages chat state, message history, and real-time SSE streaming.
 * Integrates with Clerk authentication for secure API calls.
 */

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";

/**
 * Message interface for chat history
 */
export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

/**
 * useChat Hook
 *
 * Provides chat functionality with SSE streaming from backend.
 *
 * @returns Chat state and functions
 */
export function useChat() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  /**
   * Load conversation history on mount
   */
  useEffect(() => {
    loadHistory();
    // Cleanup event source on unmount
    return () => {
      eventSourceRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /**
   * Load conversation history from API
   */
  async function loadHistory() {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        }/api/v1/companion/history`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load history");
      }

      const data = await response.json();

      // Load latest conversation
      if (data.conversations && data.conversations.length > 0) {
        const latest = data.conversations[0];
        setConversationId(latest.id);
        setMessages(
          latest.messages.map((m: any) => ({
            ...m,
            timestamp: new Date(m.timestamp),
          }))
        );
      }
    } catch (err) {
      console.error("Error loading history:", err);
      // Don't set error state here - empty history is okay for new users
    }
  }

  /**
   * Send message to Eliza
   *
   * @param content - Message content
   */
  async function sendMessage(content: string) {
    if (!content.trim()) return;

    // Optimistic update - add user message immediately
    const userMessage: Message = {
      role: "user",
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      // Send message to API
      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        }/api/v1/companion/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            message: content,
            conversation_id: conversationId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      const newConversationId = data.conversation_id;
      setConversationId(newConversationId);

      // Start SSE stream
      await streamResponse(newConversationId, token);
    } catch (err) {
      console.error("Error sending message:", err);
      setError("Failed to send message. Please try again.");
      setIsLoading(false);

      // Remove optimistic user message on error
      setMessages((prev) => prev.slice(0, -1));
    }
  }

  /**
   * Stream Eliza's response via SSE
   *
   * @param convId - Conversation ID
   * @param token - Auth token
   */
  async function streamResponse(convId: string, token: string) {
    // Close existing connection
    eventSourceRef.current?.close();

    // Create new SSE connection
    // Note: EventSource doesn't support custom headers, so we pass token as query param
    const eventSource = new EventSource(
      `${
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      }/api/v1/companion/stream/${convId}?token=${token}`
    );
    eventSourceRef.current = eventSource;

    let assistantMessage = "";

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "token") {
          assistantMessage += data.content;

          // Update message in real-time
          setMessages((prev) => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage?.role === "assistant") {
              // Update existing assistant message
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMessage,
                  content: assistantMessage,
                },
              ];
            } else {
              // Add new assistant message
              return [
                ...prev,
                {
                  role: "assistant",
                  content: assistantMessage,
                  timestamp: new Date(),
                },
              ];
            }
          });
        } else if (data.type === "complete") {
          setIsLoading(false);
          eventSource.close();
        } else if (data.type === "error") {
          setError(data.message || "An error occurred");
          setIsLoading(false);
          eventSource.close();
        }
      } catch (err) {
        console.error("Error parsing SSE event:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      setError("Connection lost. Please try again.");
      setIsLoading(false);
      eventSource.close();
    };
  }

  return {
    messages,
    isLoading,
    sendMessage,
    error,
  };
}

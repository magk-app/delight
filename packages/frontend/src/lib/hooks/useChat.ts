"use client";

import { useAuth } from "@clerk/nextjs";
import { useCallback, useEffect, useRef, useState } from "react";

export type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

type StreamEvent =
  | { type: "token"; content: string }
  | { type: "complete" }
  | { type: "error"; message?: string };

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "";

function resolveApiUrl(path: string): string {
  if (!path.startsWith("/")) {
    throw new Error(`API path must start with '/': received ${path}`);
  }

  if (API_BASE_URL) {
    return `${API_BASE_URL}${path}`;
  }

  if (typeof window !== "undefined") {
    return `${window.location.origin}${path}`;
  }

  return path;
}

export function useChat() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const assistantTimestampRef = useRef<number | null>(null);

  const closeEventSource = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      assistantTimestampRef.current = null;
    }
  }, []);

  useEffect(() => closeEventSource, [closeEventSource]);

  const loadHistory = useCallback(async () => {
    if (!isLoaded) {
      return;
    }

    if (!isSignedIn) {
      setMessages([]);
      setConversationId(null);
      return;
    }

    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Missing authentication token");
      }

      const response = await fetch(resolveApiUrl("/api/v1/companion/history"), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load history: ${response.status}`);
      }

      const data = await response.json();
      const latestConversation = data?.conversations?.[0];

      if (!latestConversation) {
        setMessages([]);
        setConversationId(null);
        return;
      }

      setConversationId(latestConversation.id);
      setMessages(
        (latestConversation.messages ?? []).map((message: any) => ({
          role: message.role === "assistant" ? "assistant" : "user",
          content: message.content ?? "",
          timestamp: new Date(message.timestamp),
        }))
      );
    } catch (historyError) {
      console.error("Failed to load conversation history", historyError);
      setError("Unable to load previous messages. Please try again later.");
    }
  }, [getToken, isLoaded, isSignedIn]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const streamResponse = useCallback(
    (convId: string, token: string) => {
      closeEventSource();

      const streamUrl = `${resolveApiUrl(
        `/api/v1/companion/stream/${convId}`
      )}?token=${encodeURIComponent(token)}`;
      const eventSource = new EventSource(streamUrl);

      eventSourceRef.current = eventSource;
      let assistantBuffer = "";

      eventSource.onmessage = (event) => {
        try {
          const payload: StreamEvent = JSON.parse(event.data);

          if (payload.type === "token") {
            assistantBuffer += payload.content;
            setMessages((previous) => {
              const lastMessage = previous[previous.length - 1];

              if (
                lastMessage?.role === "assistant" &&
                assistantTimestampRef.current ===
                  lastMessage.timestamp.getTime()
              ) {
                return [
                  ...previous.slice(0, -1),
                  {
                    ...lastMessage,
                    content: assistantBuffer,
                  },
                ];
              }

              const timestamp = new Date();
              assistantTimestampRef.current = timestamp.getTime();

              return [
                ...previous,
                {
                  role: "assistant",
                  content: assistantBuffer,
                  timestamp,
                },
              ];
            });
          } else if (payload.type === "complete") {
            setIsLoading(false);
            closeEventSource();
          } else if (payload.type === "error") {
            setError(
              payload.message ??
                "Something went wrong while streaming the response."
            );
            setIsLoading(false);
            closeEventSource();
          }
        } catch (parseError) {
          console.error("Failed to parse streaming event", parseError);
        }
      };

      eventSource.onerror = () => {
        setError("Connection lost. Please try sending your message again.");
        setIsLoading(false);
        closeEventSource();
      };
    },
    [closeEventSource]
  );

  const sendMessage = useCallback(
    async (content: string) => {
      const trimmed = content.trim();
      if (!trimmed) {
        return;
      }

      if (!isLoaded || !isSignedIn) {
        setError("You need to be signed in to chat.");
        return;
      }

      const userMessage: Message = {
        role: "user",
        content: trimmed,
        timestamp: new Date(),
      };

      setMessages((previous) => [...previous, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const token = await getToken();
        if (!token) {
          throw new Error("Missing authentication token");
        }

        const response = await fetch(resolveApiUrl("/api/v1/companion/chat"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            message: trimmed,
            conversation_id: conversationId,
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to send message: ${response.status}`);
        }

        const data = await response.json();
        const nextConversationId = data?.conversation_id;

        if (nextConversationId) {
          setConversationId(nextConversationId);
          streamResponse(nextConversationId, token);
        } else {
          throw new Error("Missing conversation identifier in response");
        }
      } catch (sendError) {
        console.error("Failed to send message", sendError);
        setError("Failed to send message. Please try again.");
        setIsLoading(false);
      }
    },
    [conversationId, getToken, isLoaded, isSignedIn, streamResponse]
  );

  return {
    messages,
    isLoading,
    error,
    sendMessage,
  };
}

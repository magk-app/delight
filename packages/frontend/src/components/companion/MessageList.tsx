/**
 * MessageList Component
 *
 * Displays list of messages with auto-scroll to latest message.
 * Handles empty state and loading indicator.
 */

'use client';

import { useEffect, useRef } from 'react';
import { Message } from './Message';
import { LoadingIndicator } from './LoadingIndicator';
import { Message as MessageType } from '@/lib/hooks/useChat';

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
}

/**
 * MessageList Component
 *
 * Scrolls automatically to show latest messages as they arrive.
 */
export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scroll-smooth"
      data-testid="message-list"
    >
      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center px-6">
          <div className="h-16 w-16 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-2xl font-bold mb-4">
            E
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">
            Chat with Eliza
          </h2>
          <p className="text-gray-600 max-w-md">
            Hi! I'm Eliza, your AI companion. I'm here to help you transform
            your goals into reality. What's on your mind?
          </p>
        </div>
      )}

      {/* Messages */}
      {messages.map((message, index) => (
        <Message
          key={`${message.timestamp.getTime()}-${index}`}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}

      {/* Loading Indicator */}
      {isLoading && <LoadingIndicator />}

      {/* Auto-scroll anchor */}
      <div ref={bottomRef} />
    </div>
  );
}

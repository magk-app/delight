/**
 * MessageInput Component
 *
 * Text input for sending messages to Eliza.
 * Features:
 * - Auto-resize textarea
 * - Enter to send, Shift+Enter for new line
 * - Disabled during loading
 * - Accessible keyboard navigation
 * - Mobile-friendly touch targets (>44px)
 */

'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

/**
 * MessageInput Component
 *
 * Provides text input with auto-resize and keyboard shortcuts.
 */
export function MessageInput({ onSend, disabled = false }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  /**
   * Handle send message
   */
  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  /**
   * Handle keyboard shortcuts
   * - Enter: Send message
   * - Shift+Enter: New line
   * - Escape: Clear input
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === 'Escape') {
      setMessage('');
      textareaRef.current?.blur();
    }
  };

  return (
    <div
      className="border-t border-gray-200 bg-white px-4 py-4 md:px-6"
      data-testid="message-input-container"
    >
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message Eliza..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-2xl border border-gray-300 px-4 py-3 pr-12 text-[15px] leading-relaxed focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-opacity-20 disabled:bg-gray-100 disabled:cursor-not-allowed transition-all"
            style={{ maxHeight: '200px' }}
            aria-label="Chat message input"
            data-testid="chat-input"
          />

          {/* Character count (optional, show only when approaching limit) */}
          {message.length > 4500 && (
            <span className="absolute bottom-3 right-14 text-xs text-gray-400">
              {5000 - message.length}
            </span>
          )}
        </div>

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          className="flex-shrink-0 h-12 w-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 text-white flex items-center justify-center hover:from-purple-600 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg active:scale-95"
          aria-label="Send message"
          data-testid="send-button"
        >
          {/* Send Icon (Arrow Up) */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-5 h-5"
          >
            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
          </svg>
        </button>
      </div>

      {/* Keyboard Hint */}
      <div className="text-xs text-gray-400 text-center mt-2">
        <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-[11px] font-mono">
          Enter
        </kbd>{' '}
        to send •{' '}
        <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-[11px] font-mono">
          Shift + Enter
        </kbd>{' '}
        for new line
      </div>
    </div>
  );
}

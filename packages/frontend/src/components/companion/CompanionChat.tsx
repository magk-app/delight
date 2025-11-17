/**
 * CompanionChat Component
 *
 * Main chat interface with Eliza.
 * Integrates MessageList, MessageInput, and useChat hook.
 */

'use client';

import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '@/lib/hooks/useChat';

/**
 * CompanionChat Component
 *
 * Full-screen chat interface (following UX spec: full-screen, not sidebar).
 */
export function CompanionChat() {
  const { messages, isLoading, sendMessage, error } = useChat();

  return (
    <div
      className="flex flex-col h-full bg-gradient-to-b from-gray-50 to-white"
      data-testid="chat-container"
    >
      {/* Error Banner */}
      {error && (
        <div
          className="bg-red-50 border-b border-red-200 px-6 py-3 text-red-700 text-sm flex items-center justify-between"
          role="alert"
        >
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="w-5 h-5"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z"
                clipRule="evenodd"
              />
            </svg>
            <span>{error}</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="text-red-600 hover:text-red-800 underline text-sm font-medium"
          >
            Reload
          </button>
        </div>
      )}

      {/* Message List */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Message Input */}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}

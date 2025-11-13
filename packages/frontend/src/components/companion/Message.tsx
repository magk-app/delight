/**
 * Message Component
 *
 * Displays a single chat message with animations and styling.
 * Follows UX spec: Eliza messages use purple theme, user messages use warm gold.
 */

'use client';

import { motion } from 'framer-motion';
import { Message as MessageType } from '@/lib/hooks/useChat';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

/**
 * Format timestamp to readable format
 */
function formatTime(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

/**
 * Message Component
 *
 * Displays user or assistant message with smooth fade-in animation.
 */
export function Message({ role, content, timestamp }: MessageProps) {
  const isUser = role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
      data-testid={`message-${role}`}
    >
      <div
        className={`flex max-w-[80%] md:max-w-[70%] gap-3 ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        {/* Avatar */}
        {!isUser && (
          <motion.div
            className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
            animate={{ scale: [1, 1.02, 1] }}
            transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
            aria-label="Eliza"
          >
            E
          </motion.div>
        )}

        {/* Message Bubble */}
        <div className="flex flex-col gap-1">
          <div
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? 'bg-gradient-to-br from-amber-400 to-amber-500 text-white'
                : 'bg-gray-100 text-gray-900'
            } shadow-sm`}
          >
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
              {content}
            </p>
          </div>

          {/* Timestamp */}
          <span
            className={`text-xs text-gray-500 px-2 ${
              isUser ? 'text-right' : 'text-left'
            }`}
          >
            {formatTime(timestamp)}
          </span>
        </div>

        {/* User Avatar (optional, can add initial or icon) */}
        {isUser && (
          <div
            className="h-8 w-8 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
            aria-label="You"
          >
            Y
          </div>
        )}
      </div>
    </motion.div>
  );
}

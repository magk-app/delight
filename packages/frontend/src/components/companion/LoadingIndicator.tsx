/**
 * LoadingIndicator Component
 *
 * Displays animated typing dots with breathing effect.
 * Uses Eliza's purple theme from UX spec.
 */

'use client';

import { motion } from 'framer-motion';

/**
 * LoadingIndicator - Typing dots animation
 *
 * Shows Eliza is thinking/responding with smooth breathing animation
 */
export function LoadingIndicator() {
  return (
    <div
      className="flex items-center gap-2 px-4 py-3"
      data-testid="loading-indicator"
      aria-live="polite"
      aria-label="Eliza is typing"
    >
      {/* Eliza Avatar Circle */}
      <motion.div
        className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-sm font-semibold"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
      >
        E
      </motion.div>

      {/* Typing Dots */}
      <motion.div
        className="flex gap-1"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
      >
        <motion.span
          className="h-2 w-2 rounded-full bg-purple-400"
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{
            repeat: Infinity,
            duration: 1.5,
            ease: 'easeInOut',
            delay: 0,
          }}
        />
        <motion.span
          className="h-2 w-2 rounded-full bg-purple-400"
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{
            repeat: Infinity,
            duration: 1.5,
            ease: 'easeInOut',
            delay: 0.2,
          }}
        />
        <motion.span
          className="h-2 w-2 rounded-full bg-purple-400"
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{
            repeat: Infinity,
            duration: 1.5,
            ease: 'easeInOut',
            delay: 0.4,
          }}
        />
      </motion.div>

      <span className="text-sm text-gray-500">Eliza is thinking...</span>
    </div>
  );
}

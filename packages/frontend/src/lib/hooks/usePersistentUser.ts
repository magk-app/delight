/**
 * Persistent User Hook
 *
 * Manages a persistent user ID across sessions using localStorage
 * This ensures memories are tied to the same user even after page refresh
 *
 * Future: Can be replaced with Clerk user ID when auth is implemented
 */

'use client';

import { useState, useEffect } from 'react';

const USER_ID_KEY = 'experimental_user_id';

export function usePersistentUser() {
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    // Get or create persistent user ID
    let stored = localStorage.getItem(USER_ID_KEY);

    if (!stored) {
      // Generate new UUID
      stored = crypto.randomUUID();
      localStorage.setItem(USER_ID_KEY, stored);
    }

    setUserId(stored);
    setIsLoading(false);
  }, []);

  const clearUser = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(USER_ID_KEY);
      const newId = crypto.randomUUID();
      localStorage.setItem(USER_ID_KEY, newId);
      setUserId(newId);
    }
  };

  return { userId, isLoading, clearUser };
}

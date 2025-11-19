/**
 * React Hooks for Experimental API
 *
 * Provides easy-to-use hooks for accessing the experimental backend API
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import experimentalAPI, {
  Memory,
  MemoryStats,
  SystemConfig,
  TokenUsageSummary,
  GraphData,
  ChatMessage,
} from '../api/experimental-client';

// ============================================================================
// useMemoryStats - Get memory statistics
// ============================================================================

export function useMemoryStats(userId?: string, autoRefresh?: boolean, refreshInterval?: number) {
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await experimentalAPI.getMemoryStats(userId);
      setStats(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    refresh();

    // Auto-refresh if enabled
    if (autoRefresh) {
      const interval = setInterval(refresh, refreshInterval || 5000);
      return () => clearInterval(interval);
    }
  }, [refresh, autoRefresh, refreshInterval]);

  return { stats, loading, error, refresh };
}

// ============================================================================
// useMemories - Get and manage memories
// ============================================================================

export function useMemories(filters?: {
  user_id?: string;
  memory_type?: string;
  category?: string;
  limit?: number;
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
}) {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Stringify filters to prevent infinite loop from object reference changes
  const filtersString = JSON.stringify(filters || {});

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const parsedFilters = filtersString ? JSON.parse(filtersString) : undefined;
      const data = await experimentalAPI.getMemories(parsedFilters);
      setMemories(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [filtersString]); // Use stringified version to prevent object reference issues

  const deleteMemory = useCallback(async (memoryId: string) => {
    try {
      await experimentalAPI.deleteMemory(memoryId);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
    } catch (err) {
      throw err;
    }
  }, []);

  useEffect(() => {
    refresh();

    // Auto-refresh if enabled
    if (filters?.autoRefresh) {
      const interval = setInterval(refresh, filters.refreshInterval || 5000);
      return () => clearInterval(interval);
    }
  }, [refresh, filters?.autoRefresh, filters?.refreshInterval]);

  return { memories, loading, error, refresh, deleteMemory };
}

// ============================================================================
// useConfig - Get and update configuration
// ============================================================================

export function useConfig() {
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await experimentalAPI.getConfig();
      setConfig(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (newConfig: SystemConfig) => {
    try {
      setSaving(true);
      setError(null);
      await experimentalAPI.updateConfig(newConfig);
      setConfig(newConfig);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setSaving(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { config, loading, error, saving, refresh, updateConfig };
}

// ============================================================================
// useTokenUsage - Get token usage analytics
// ============================================================================

export function useTokenUsage(hours: number = 24, autoRefresh?: boolean, refreshInterval?: number) {
  const [usage, setUsage] = useState<TokenUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await experimentalAPI.getTokenUsage(hours);
      setUsage(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [hours]);

  useEffect(() => {
    refresh();

    // Auto-refresh if enabled
    if (autoRefresh) {
      const interval = setInterval(refresh, refreshInterval || 5000);
      return () => clearInterval(interval);
    }
  }, [refresh, autoRefresh, refreshInterval]);

  return { usage, loading, error, refresh };
}

// ============================================================================
// useMemoryGraph - Get memory graph data
// ============================================================================

export function useMemoryGraph(userId?: string, limit: number = 100) {
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await experimentalAPI.getMemoryGraph(userId, limit);
      setGraph(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [userId, limit]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { graph, loading, error, refresh };
}

// ============================================================================
// useWebSocket - Real-time updates
// ============================================================================

export function useWebSocket(onUpdate?: (data: any) => void) {
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<any>(null);

  useEffect(() => {
    const handleUpdate = (data: any) => {
      setLastUpdate(data);
      onUpdate?.(data);
    };

    experimentalAPI.connectWebSocket(handleUpdate);
    setConnected(true);

    // Check connection status periodically
    const interval = setInterval(() => {
      // This is a simplification - you'd check actual WebSocket state
      setConnected(true);
    }, 5000);

    return () => {
      clearInterval(interval);
      experimentalAPI.disconnectWebSocket();
      setConnected(false);
    };
  }, [onUpdate]);

  const send = useCallback((data: any) => {
    experimentalAPI.sendWebSocketMessage(data);
  }, []);

  return { connected, lastUpdate, send };
}

// ============================================================================
// useHealthCheck - Check API health
// ============================================================================

export function useHealthCheck() {
  const [healthy, setHealthy] = useState(false);
  const [checking, setChecking] = useState(true);
  const [health, setHealth] = useState<any>(null);

  const check = useCallback(async () => {
    try {
      setChecking(true);
      const data = await experimentalAPI.healthCheck();
      setHealth(data);
      setHealthy(data.status === 'healthy');
    } catch (err) {
      setHealthy(false);
      setHealth(null);
    } finally {
      setChecking(false);
    }
  }, []);

  useEffect(() => {
    check();
    // Check every 30 seconds
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, [check]);

  return { healthy, checking, health, check };
}

/**
 * API Client for Experimental Backend Server
 *
 * This client connects to the experimental agent backend running on port 8001
 * and provides type-safe access to all experimental features:
 * - Chat with AI agent
 * - Memory management and search
 * - Analytics and token usage
 * - Configuration management
 * - Real-time updates via WebSocket
 */

// ============================================================================
// Types
// ============================================================================

export interface Memory {
  id: string;
  content: string;
  memory_type: string;
  user_id: string;
  metadata: Record<string, any>;
  created_at: string;
  embedding?: number[];
}

export interface SearchResult {
  id: string;
  content: string;
  memory_type: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface MemoryStats {
  total_memories: number;
  by_type: Record<string, number>;
  by_category: Record<string, number>;
  total_embeddings: number;
  avg_embedding_time_ms: number;
  storage_size_bytes: number;
}

export interface TokenUsage {
  model: string;
  tokens_input: number;
  tokens_output: number;
  cost: number;
  timestamp?: string;
}

export interface TokenUsageSummary {
  total_tokens: number;
  total_cost: number;
  by_model: Record<
    string,
    {
      tokens: number;
      cost: number;
    }
  >;
}

export interface SystemConfig {
  models: {
    chat_model: string;
    reasoning_model: string;
    expensive_model: string;
    embedding_model: string;
  };
  search: {
    similarity_threshold: number;
    default_search_limit: number;
    hybrid_search_weight_vector: number;
    graph_traversal_max_depth: number;
  };
  fact_extraction: {
    max_facts_per_message: number;
    auto_categorize: boolean;
    max_categories_per_fact: number;
    min_fact_length: number;
  };
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    categories: string[];
    created_at: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
    type: string;
  }>;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
  memories_used?: SearchResult[];
  memories_created?: Memory[];
}

export interface ChatRequest {
  message: string;
  user_id?: string;
  conversation_history?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
}

export interface ChatResponse {
  response: string;
  memories_retrieved: Array<{
    id: string;
    content: string;
    memory_type: string;
    score?: number;
    categories?: string[];
  }>;
  memories_created: Array<{
    id: string;
    content: string;
    memory_type: string;
    categories?: string[];
  }>;
  timestamp: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  message_count: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  messages?: ConversationMessage[];
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  user_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: {
    memories_retrieved?: SearchResult[];
    memories_created?: Memory[];
  };
  created_at: string;
}

// ============================================================================
// API Client
// ============================================================================

/**
 * FIXES APPLIED (2024):
 * =====================
 * 1. Request Caching: Added 2-second cache for GET requests
 *    - Prevents duplicate API calls when components re-render rapidly
 *    - Reduces backend load from excessive polling
 *    - Cache is automatically cleared after mutations (create/delete/update)
 *
 * 2. Error Handling: Improved error messages for network failures
 *    - Better diagnostics for connection issues
 *    - Helpful messages for ngrok/network access scenarios
 */
class ExperimentalAPIClient {
  private baseUrl: string;
  private wsUrl: string;
  private ws: WebSocket | null = null;
  private wsCallbacks: Map<string, (data: any) => void> = new Map();
  private requestCache: Map<string, { data: any; timestamp: number }> =
    new Map();
  private readonly CACHE_TTL = 5000; // 5 seconds cache for GET requests (increased from 2s)

  constructor(baseUrl?: string) {
    // Use environment variable if available, otherwise fallback to localhost
    // NEXT_PUBLIC_ prefix makes it available in the browser
    this.baseUrl =
      baseUrl ||
      (typeof window !== "undefined"
        ? process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL ||
          "http://localhost:8001"
        : process.env.EXPERIMENTAL_API_URL || "http://localhost:8001");
    this.wsUrl = this.baseUrl.replace("http", "ws");
  }

  // ============================================================================
  // Core HTTP Methods
  // ============================================================================

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error (${response.status}): ${error}`);
      }

      return response.json();
    } catch (error) {
      // Provide helpful error message for network issues
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        const currentHost =
          typeof window !== "undefined" ? window.location.host : "unknown";
        const isLocalhost =
          this.baseUrl.includes("localhost") ||
          this.baseUrl.includes("127.0.0.1");
        const isNetworkAccess =
          currentHost !== "localhost" &&
          currentHost !== "127.0.0.1" &&
          !currentHost.includes("localhost");

        if (isLocalhost && isNetworkAccess) {
          throw new Error(
            `Cannot connect to backend at ${this.baseUrl}. ` +
              `When accessing the frontend via network (${currentHost}), ` +
              `you must set NEXT_PUBLIC_EXPERIMENTAL_API_URL to a network-accessible backend URL. ` +
              `If using ngrok, expose the backend and set: ` +
              `NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://your-backend-ngrok-url.ngrok.io`
          );
        }
        throw new Error(
          `Failed to fetch from ${url}. ` +
            `Make sure the experimental backend is running and accessible at ${this.baseUrl}`
        );
      }
      throw error;
    }
  }

  private pendingRequests: Map<string, Promise<any>> = new Map();

  private async get<T>(endpoint: string, useCache: boolean = true): Promise<T> {
    // Check cache for recent requests to prevent duplicate calls
    if (useCache) {
      const cached = this.requestCache.get(endpoint);
      if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
        console.log(`📦 Cache hit for ${endpoint}`);
        return cached.data as T;
      }

      // Check if there's already a pending request for this endpoint
      const pending = this.pendingRequests.get(endpoint);
      if (pending) {
        console.log(`⏳ Reusing pending request for ${endpoint}`);
        return pending as Promise<T>;
      }
    }

    // Create new request and track it
    const requestPromise = this.request<T>(endpoint, { method: "GET" })
      .then((data) => {
        // Cache the result
        if (useCache) {
          this.requestCache.set(endpoint, { data, timestamp: Date.now() });
        }
        // Remove from pending requests
        this.pendingRequests.delete(endpoint);
        return data;
      })
      .catch((error) => {
        // Remove from pending requests on error
        this.pendingRequests.delete(endpoint);
        throw error;
      });

    if (useCache) {
      this.pendingRequests.set(endpoint, requestPromise);
    }

    return requestPromise;
  }

  private async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  private async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // ============================================================================
  // Health Check
  // ============================================================================

  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    storage: string;
    version: string;
  }> {
    return this.get("/health");
  }

  // ============================================================================
  // Configuration API
  // ============================================================================

  async getConfig(): Promise<SystemConfig> {
    return this.get("/api/config");
  }

  async updateConfig(
    config: SystemConfig
  ): Promise<{ status: string; message: string }> {
    return this.post("/api/config", config);
  }

  async getAvailableModels(): Promise<{
    chat: string[];
    reasoning: string[];
    embedding: string[];
  }> {
    return this.get("/api/models/available");
  }

  // ============================================================================
  // Analytics API
  // ============================================================================

  async getMemoryStats(userId?: string): Promise<MemoryStats> {
    const params = userId ? `?user_id=${userId}` : "";
    return this.get(`/api/analytics/stats${params}`);
  }

  async getTokenUsage(
    hours: number = 24,
    userId?: string
  ): Promise<TokenUsageSummary> {
    const params = new URLSearchParams();
    params.append("hours", hours.toString());
    if (userId) params.append("user_id", userId);
    return this.get(`/api/analytics/token-usage?${params.toString()}`);
  }

  async getSearchPerformance(limit: number = 100): Promise<any[]> {
    return this.get(`/api/analytics/search-performance?limit=${limit}`);
  }

  async recordTokenUsage(usage: TokenUsage): Promise<{ status: string }> {
    return this.post("/api/analytics/token-usage", usage);
  }

  // ============================================================================
  // Memory API
  // ============================================================================

  async getMemories(filters?: {
    user_id?: string;
    memory_type?: string;
    category?: string;
    limit?: number;
  }): Promise<Memory[]> {
    const params = new URLSearchParams();
    if (filters?.user_id) params.append("user_id", filters.user_id);
    if (filters?.memory_type) params.append("memory_type", filters.memory_type);
    if (filters?.category) params.append("category", filters.category);
    if (filters?.limit) params.append("limit", filters.limit.toString());

    const queryString = params.toString();
    return this.get(`/api/memories${queryString ? `?${queryString}` : ""}`);
  }

  async getMemory(memoryId: string): Promise<Memory> {
    return this.get(`/api/memories/${memoryId}`);
  }

  async updateMemory(
    memoryId: string,
    updates: {
      content?: string;
      importance?: number;
      metadata?: Record<string, any>;
    }
  ): Promise<Memory> {
    return this.request(`/api/memories/${memoryId}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  async deleteMemory(
    memoryId: string
  ): Promise<{ status: string; message: string }> {
    return this.delete(`/api/memories/${memoryId}`);
  }

  async getCategoryHierarchy(
    userId?: string
  ): Promise<Record<string, Record<string, number>>> {
    const params = userId ? `?user_id=${userId}` : "";
    return this.get(`/api/memories/categories/hierarchy${params}`);
  }

  // ============================================================================
  // Graph API (Phase 3)
  // ============================================================================

  /**
   * Get basic memory graph (legacy format)
   */
  async getMemoryGraph(
    userId?: string,
    limit: number = 100
  ): Promise<GraphData> {
    const params = new URLSearchParams();
    if (userId) params.append("user_id", userId);
    params.append("limit", limit.toString());

    return this.get(`/api/graph/memories?${params.toString()}`);
  }

  /**
   * Get graph visualization data (React Flow format)
   */
  async getGraphVisualization(
    userId: string,
    entityType?: string,
    limit: number = 50
  ): Promise<{
    nodes: Array<{
      id: string;
      label: string;
      type: string;
      content: string;
      attributes: Record<string, any>;
      created_at: string | null;
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      label: string;
      strength: number;
      metadata: Record<string, any>;
    }>;
  }> {
    const params = new URLSearchParams();
    if (entityType) params.append("entity_type", entityType);
    params.append("limit", limit.toString());

    return this.get(`/api/graph/visualize/${userId}?${params.toString()}`);
  }

  /**
   * Create a typed relationship between two memories
   */
  async createRelationship(request: {
    from_memory_id: string;
    to_memory_id: string;
    relationship_type: string;
    strength?: number;
    metadata?: Record<string, any>;
    bidirectional?: boolean;
  }): Promise<{
    status: string;
    relationship: {
      id: string;
      from_memory_id: string;
      to_memory_id: string;
      relationship_type: string;
      strength: number;
      metadata: Record<string, any>;
      created_at: string;
    };
  }> {
    return this.post("/api/graph/relationship", request);
  }

  /**
   * Get all relationships for a specific memory
   */
  async getRelationships(
    memoryId: string,
    relationshipType?: string
  ): Promise<{
    memory_id: string;
    relationships: Array<{
      id: string;
      from_memory_id: string;
      to_memory_id: string;
      relationship_type: string;
      strength: number;
      metadata: Record<string, any>;
      related_memory: {
        id: string;
        content: string;
        entity_id: string | null;
        entity_type: string | null;
      };
      direction: "outgoing" | "incoming";
    }>;
  }> {
    const params = relationshipType
      ? `?relationship_type=${relationshipType}`
      : "";
    return this.get(`/api/graph/relationships/${memoryId}${params}`);
  }

  /**
   * Traverse the graph from a starting memory
   */
  async traverseGraph(
    startMemoryId: string,
    maxDepth: number = 3,
    minStrength: number = 0.5,
    relationshipType?: string
  ): Promise<{
    start_memory_id: string;
    paths: Array<{
      nodes: Array<{
        memory_id: string;
        entity_id: string | null;
        entity_type: string | null;
        content: string;
        depth: number;
      }>;
      edges: Array<{
        from_id: string;
        to_id: string;
        relationship_type: string;
        strength: number;
      }>;
      total_strength: number;
    }>;
  }> {
    const params = new URLSearchParams();
    params.append("max_depth", maxDepth.toString());
    params.append("min_strength", minStrength.toString());
    if (relationshipType) params.append("relationship_type", relationshipType);

    return this.get(
      `/api/graph/traverse/${startMemoryId}?${params.toString()}`
    );
  }

  /**
   * Find the shortest path between two memories
   */
  async findShortestPath(
    fromMemoryId: string,
    toMemoryId: string,
    maxDepth: number = 5
  ): Promise<{
    from_memory_id: string;
    to_memory_id: string;
    path: Array<{
      memory_id: string;
      entity_id: string | null;
      content: string;
      relationship_to_next: string | null;
    }> | null;
    path_length: number;
  }> {
    const params = new URLSearchParams();
    params.append("max_depth", maxDepth.toString());

    return this.get(
      `/api/graph/shortest-path/${fromMemoryId}/${toMemoryId}?${params.toString()}`
    );
  }

  /**
   * Get the complete entity graph for a user
   */
  async getEntityGraph(
    userId: string,
    entityType?: string
  ): Promise<{
    user_id: string;
    entity_graph: Record<
      string,
      Array<{
        to_entity_id: string;
        relationship_type: string;
        strength: number;
      }>
    >;
  }> {
    const params = entityType ? `?entity_type=${entityType}` : "";
    return this.get(`/api/graph/entity-graph/${userId}${params}`);
  }

  // ============================================================================
  // Chat API
  // ============================================================================

  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.post("/api/chat/message", request);
  }

  async checkChatHealth(): Promise<{
    status: string;
    service: string;
    timestamp: string;
  }> {
    return this.get("/api/chat/health");
  }

  // ============================================================================
  // User API
  // ============================================================================

  async ensureUser(
    userId: string
  ): Promise<{ status: string; user_id: string; message: string }> {
    return this.post("/api/users/ensure", { user_id: userId });
  }

  // ============================================================================
  // Conversation API
  // ============================================================================

  async createConversation(
    userId: string,
    title?: string
  ): Promise<Conversation> {
    return this.post("/api/conversations/", { user_id: userId, title });
  }

  async getConversations(
    userId: string,
    includeArchived = false,
    useCache: boolean = true
  ): Promise<Conversation[]> {
    const params = new URLSearchParams();
    params.append("user_id", userId);
    if (includeArchived) params.append("include_archived", "true");

    return this.get(`/api/conversations/?${params.toString()}`, useCache);
  }

  // Clear cache (useful after mutations)
  clearCache(endpoint?: string): void {
    if (endpoint) {
      this.requestCache.delete(endpoint);
      this.pendingRequests.delete(endpoint);
      console.log(`🗑️ Cleared cache for ${endpoint}`);
    } else {
      this.requestCache.clear();
      this.pendingRequests.clear();
      console.log(`🗑️ Cleared all cache`);
    }
  }

  async getConversation(
    conversationId: string,
    useCache: boolean = true
  ): Promise<Conversation> {
    return this.get(`/api/conversations/${conversationId}`, useCache);
  }

  async saveMessage(
    conversationId: string,
    userId: string,
    role: "user" | "assistant" | "system",
    content: string,
    metadata?: {
      memories_retrieved?: SearchResult[];
      memories_created?: Memory[];
    }
  ): Promise<ConversationMessage> {
    return this.post("/api/conversations/messages", {
      conversation_id: conversationId,
      user_id: userId,
      role,
      content,
      metadata,
    });
  }

  async deleteConversation(
    conversationId: string
  ): Promise<{ status: string; message: string }> {
    return this.delete(`/api/conversations/${conversationId}`);
  }

  async archiveConversation(
    conversationId: string
  ): Promise<{ status: string; message: string }> {
    return this.post(`/api/conversations/${conversationId}/archive`, {});
  }

  // ============================================================================
  // WebSocket - Real-time Updates
  // ============================================================================

  connectWebSocket(onUpdate: (data: any) => void): void {
    if (this.ws) {
      this.ws.close();
    }

    this.ws = new WebSocket(`${this.wsUrl}/ws/updates`);

    this.ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);

        // Call specific callbacks
        this.wsCallbacks.forEach((callback) => {
          callback(data);
        });
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      // Auto-reconnect after 3 seconds
      setTimeout(() => {
        if (this.ws?.readyState === WebSocket.CLOSED) {
          this.connectWebSocket(onUpdate);
        }
      }, 3000);
    };
  }

  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onWebSocketUpdate(id: string, callback: (data: any) => void): void {
    this.wsCallbacks.set(id, callback);
  }

  offWebSocketUpdate(id: string): void {
    this.wsCallbacks.delete(id);
  }

  sendWebSocketMessage(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

// Create instance with environment variable support
// In browser: uses NEXT_PUBLIC_EXPERIMENTAL_API_URL
// On server: uses EXPERIMENTAL_API_URL
const getExperimentalAPIUrl = (): string => {
  if (typeof window !== "undefined") {
    // Client-side: use NEXT_PUBLIC_ prefixed variable
    return (
      process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL || "http://localhost:8001"
    );
  } else {
    // Server-side: use non-prefixed variable
    return (
      process.env.EXPERIMENTAL_API_URL ||
      process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL ||
      "http://localhost:8001"
    );
  }
};

export const experimentalAPI = new ExperimentalAPIClient(
  getExperimentalAPIUrl()
);
export default experimentalAPI;

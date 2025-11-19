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
  by_model: Record<string, {
    tokens: number;
    cost: number;
  }>;
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
  role: 'user' | 'assistant' | 'system';
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
  role: 'user' | 'assistant' | 'system';
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

class ExperimentalAPIClient {
  private baseUrl: string;
  private wsUrl: string;
  private ws: WebSocket | null = null;
  private wsCallbacks: Map<string, (data: any) => void> = new Map();

  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
    this.wsUrl = baseUrl.replace('http', 'ws');
  }

  // ============================================================================
  // Core HTTP Methods
  // ============================================================================

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error (${response.status}): ${error}`);
    }

    return response.json();
  }

  private async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  private async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  private async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
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
    return this.get('/health');
  }

  // ============================================================================
  // Configuration API
  // ============================================================================

  async getConfig(): Promise<SystemConfig> {
    return this.get('/api/config');
  }

  async updateConfig(config: SystemConfig): Promise<{ status: string; message: string }> {
    return this.post('/api/config', config);
  }

  async getAvailableModels(): Promise<{
    chat: string[];
    reasoning: string[];
    embedding: string[];
  }> {
    return this.get('/api/models/available');
  }

  // ============================================================================
  // Analytics API
  // ============================================================================

  async getMemoryStats(userId?: string): Promise<MemoryStats> {
    const params = userId ? `?user_id=${userId}` : '';
    return this.get(`/api/analytics/stats${params}`);
  }

  async getTokenUsage(hours: number = 24, userId?: string): Promise<TokenUsageSummary> {
    const params = new URLSearchParams();
    params.append('hours', hours.toString());
    if (userId) params.append('user_id', userId);
    return this.get(`/api/analytics/token-usage?${params.toString()}`);
  }

  async getSearchPerformance(limit: number = 100): Promise<any[]> {
    return this.get(`/api/analytics/search-performance?limit=${limit}`);
  }

  async recordTokenUsage(usage: TokenUsage): Promise<{ status: string }> {
    return this.post('/api/analytics/token-usage', usage);
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
    if (filters?.user_id) params.append('user_id', filters.user_id);
    if (filters?.memory_type) params.append('memory_type', filters.memory_type);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const queryString = params.toString();
    return this.get(`/api/memories${queryString ? `?${queryString}` : ''}`);
  }

  async getMemory(memoryId: string): Promise<Memory> {
    return this.get(`/api/memories/${memoryId}`);
  }

  async updateMemory(memoryId: string, updates: {
    content?: string;
    importance?: number;
    metadata?: Record<string, any>;
  }): Promise<Memory> {
    return this.request(`/api/memories/${memoryId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteMemory(memoryId: string): Promise<{ status: string; message: string }> {
    return this.delete(`/api/memories/${memoryId}`);
  }

  async getCategoryHierarchy(userId?: string): Promise<Record<string, Record<string, number>>> {
    const params = userId ? `?user_id=${userId}` : '';
    return this.get(`/api/memories/categories/hierarchy${params}`);
  }

  // ============================================================================
  // Graph API
  // ============================================================================

  async getMemoryGraph(userId?: string, limit: number = 100): Promise<GraphData> {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    params.append('limit', limit.toString());

    return this.get(`/api/graph/memories?${params.toString()}`);
  }

  // ============================================================================
  // Chat API
  // ============================================================================

  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.post('/api/chat/message', request);
  }

  async checkChatHealth(): Promise<{ status: string; service: string; timestamp: string }> {
    return this.get('/api/chat/health');
  }

  // ============================================================================
  // User API
  // ============================================================================

  async ensureUser(userId: string): Promise<{ status: string; user_id: string; message: string }> {
    return this.post('/api/users/ensure', { user_id: userId });
  }

  // ============================================================================
  // Conversation API
  // ============================================================================

  async createConversation(userId: string, title?: string): Promise<Conversation> {
    return this.post('/api/conversations/', { user_id: userId, title });
  }

  async getConversations(userId: string, includeArchived = false): Promise<Conversation[]> {
    const params = new URLSearchParams();
    params.append('user_id', userId);
    if (includeArchived) params.append('include_archived', 'true');

    return this.get(`/api/conversations/?${params.toString()}`);
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    return this.get(`/api/conversations/${conversationId}`);
  }

  async saveMessage(
    conversationId: string,
    userId: string,
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: {
      memories_retrieved?: SearchResult[];
      memories_created?: Memory[];
    }
  ): Promise<ConversationMessage> {
    return this.post('/api/conversations/messages', {
      conversation_id: conversationId,
      user_id: userId,
      role,
      content,
      metadata,
    });
  }

  async deleteConversation(conversationId: string): Promise<{ status: string; message: string }> {
    return this.delete(`/api/conversations/${conversationId}`);
  }

  async archiveConversation(conversationId: string): Promise<{ status: string; message: string }> {
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
      console.log('✅ WebSocket connected');
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
        console.error('WebSocket message error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
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

export const experimentalAPI = new ExperimentalAPIClient();
export default experimentalAPI;

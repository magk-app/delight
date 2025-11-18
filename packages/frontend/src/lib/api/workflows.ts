/**
 * API client for workflow operations
 * Handles all HTTP requests to the workflow backend endpoints
 */

import type {
  Workflow,
  WorkflowDetail,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowListResponse,
  WorkflowNode,
  WorkflowNodeCreate,
  WorkflowNodeUpdate,
  WorkflowEdge,
  WorkflowEdgeCreate,
  WorkflowExecution,
  WorkflowExecutionCreate,
  WorkflowExecutionDetail,
  WorkflowExecutionListResponse,
  WorkflowPlanRequest,
  WorkflowPlanResponse,
  WorkflowStatus,
} from '@/lib/types/workflow';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class WorkflowAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'WorkflowAPIError';
  }
}

/**
 * Get authentication token from Clerk
 * This should be called from within React components/hooks where Clerk is available
 */
async function getAuthToken(): Promise<string> {
  // Check if we're in a browser environment and Clerk is loaded
  if (typeof window !== 'undefined' && (window as any).Clerk) {
    try {
      const clerk = (window as any).Clerk;
      const session = await clerk.session;
      if (session) {
        return await session.getToken();
      }
    } catch (error) {
      console.warn('Failed to get Clerk token:', error);
    }
  }
  return '';
}

/**
 * Make authenticated API request
 *
 * For better auth integration, consider using this from within React components
 * where you can access useAuth() hook and pass the token explicitly.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  authToken?: string
): Promise<T> {
  // Use provided token or try to get from Clerk
  const token = authToken || await getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new WorkflowAPIError(
      errorData.detail || `API request failed: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// ============================================================================
// Workflow CRUD Operations
// ============================================================================

export async function createWorkflow(
  data: WorkflowCreate
): Promise<WorkflowDetail> {
  return apiRequest<WorkflowDetail>('/workflows', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function listWorkflows(params?: {
  status?: WorkflowStatus;
  page?: number;
  page_size?: number;
}): Promise<WorkflowListResponse> {
  const queryParams = new URLSearchParams();

  if (params?.status) queryParams.append('status', params.status);
  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.page_size)
    queryParams.append('page_size', params.page_size.toString());

  const query = queryParams.toString();
  const endpoint = query ? `/workflows?${query}` : '/workflows';

  return apiRequest<WorkflowListResponse>(endpoint);
}

export async function getWorkflow(workflowId: string): Promise<WorkflowDetail> {
  return apiRequest<WorkflowDetail>(`/workflows/${workflowId}`);
}

export async function updateWorkflow(
  workflowId: string,
  data: WorkflowUpdate
): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${workflowId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteWorkflow(workflowId: string): Promise<void> {
  return apiRequest<void>(`/workflows/${workflowId}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// Node Management
// ============================================================================

export async function addNode(
  workflowId: string,
  data: WorkflowNodeCreate
): Promise<WorkflowNode> {
  return apiRequest<WorkflowNode>(`/workflows/${workflowId}/nodes`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateNode(
  nodeId: string,
  data: WorkflowNodeUpdate
): Promise<WorkflowNode> {
  return apiRequest<WorkflowNode>(`/workflows/nodes/${nodeId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ============================================================================
// Edge Management
// ============================================================================

export async function addEdge(
  workflowId: string,
  data: WorkflowEdgeCreate
): Promise<WorkflowEdge> {
  return apiRequest<WorkflowEdge>(`/workflows/${workflowId}/edges`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteEdge(edgeId: string): Promise<void> {
  return apiRequest<void>(`/workflows/edges/${edgeId}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// LLM Plan Generation
// ============================================================================

export async function generateWorkflowPlan(
  request: WorkflowPlanRequest
): Promise<WorkflowPlanResponse> {
  return apiRequest<WorkflowPlanResponse>('/workflows/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function approveWorkflow(workflowId: string): Promise<Workflow> {
  return apiRequest<Workflow>(`/workflows/${workflowId}/approve`, {
    method: 'PATCH',
  });
}

// ============================================================================
// Execution
// ============================================================================

export async function executeWorkflow(
  workflowId: string,
  data?: WorkflowExecutionCreate
): Promise<WorkflowExecution> {
  return apiRequest<WorkflowExecution>(`/workflows/${workflowId}/execute`, {
    method: 'POST',
    body: JSON.stringify(data || { execution_context: {} }),
  });
}

export async function getExecution(
  executionId: string
): Promise<WorkflowExecutionDetail> {
  return apiRequest<WorkflowExecutionDetail>(
    `/workflows/executions/${executionId}`
  );
}

export async function listWorkflowExecutions(
  workflowId: string,
  params?: {
    page?: number;
    page_size?: number;
  }
): Promise<WorkflowExecutionListResponse> {
  const queryParams = new URLSearchParams();

  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.page_size)
    queryParams.append('page_size', params.page_size.toString());

  const query = queryParams.toString();
  const endpoint = query
    ? `/workflows/${workflowId}/executions?${query}`
    : `/workflows/${workflowId}/executions`;

  return apiRequest<WorkflowExecutionListResponse>(endpoint);
}

// ============================================================================
// Server-Sent Events (SSE) for Progress
// ============================================================================

export interface ProgressEvent {
  execution_id: string;
  workflow_id: string;
  event_type: string;
  data: any;
  timestamp: string;
}

export type ProgressCallback = (event: ProgressEvent) => void;

export function subscribeToExecutionProgress(
  executionId: string,
  onProgress: ProgressCallback,
  onError?: (error: Error) => void,
  onComplete?: () => void,
  authToken?: string
): () => void {
  const url = new URL(
    `/api/v1/workflows/sse/executions/${executionId}/progress`,
    API_BASE_URL
  );

  // Note: EventSource doesn't support custom headers (e.g., Authorization: Bearer)
  // Options for authentication:
  // 1. Use cookie-based auth (recommended for SSE with Clerk)
  // 2. Pass token as query parameter (less secure): url.searchParams.set('token', authToken)
  // 3. Configure Clerk to use cookies for session management
  //
  // For production, ensure backend SSE endpoint validates session cookies

  const eventSource = new EventSource(url.toString());

  eventSource.addEventListener('node_started', (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
  });

  eventSource.addEventListener('node_completed', (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
  });

  eventSource.addEventListener('node_failed', (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
  });

  eventSource.addEventListener('workflow_completed', (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
    if (onComplete) onComplete();
    eventSource.close();
  });

  eventSource.addEventListener('workflow_failed', (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
    if (onError) onError(new Error('Workflow execution failed'));
    eventSource.close();
  });

  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
    if (onError) onError(new Error('Connection lost'));
    eventSource.close();
  };

  // Return cleanup function
  return () => {
    eventSource.close();
  };
}

export function subscribeToWorkflowLive(
  workflowId: string,
  onProgress: ProgressCallback,
  onError?: (error: Error) => void,
  onComplete?: () => void,
  authToken?: string
): () => void {
  const url = new URL(
    `/api/v1/workflows/sse/workflows/${workflowId}/live`,
    API_BASE_URL
  );

  // Note: SSE authentication relies on cookie-based session
  // See subscribeToExecutionProgress for auth details

  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    onProgress(data);
  };

  eventSource.addEventListener('workflow_completed', () => {
    if (onComplete) onComplete();
    eventSource.close();
  });

  eventSource.onerror = (error) => {
    if (onError) onError(new Error('Connection lost'));
    eventSource.close();
  };

  return () => {
    eventSource.close();
  };
}

export { WorkflowAPIError };

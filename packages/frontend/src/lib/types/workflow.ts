/**
 * TypeScript types for workflow system
 * Matches backend Pydantic schemas
 */

export enum WorkflowStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  EXECUTING = 'executing',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum NodeType {
  TASK = 'task',
  DECISION = 'decision',
  PARALLEL_GROUP = 'parallel_group',
  CONDITIONAL = 'conditional',
  INPUT = 'input',
  OUTPUT = 'output',
  VERIFICATION = 'verification',
}

export enum NodeStatus {
  PENDING = 'pending',
  READY = 'ready',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
  BLOCKED = 'blocked',
}

export enum EdgeType {
  SEQUENTIAL = 'sequential',
  PARALLEL = 'parallel',
  CONDITIONAL = 'conditional',
}

export enum ExecutionStatus {
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

// Node Position
export interface NodePosition {
  x: number;
  y: number;
}

// Workflow Node
export interface WorkflowNode {
  id: string;
  workflow_id: string;
  name: string;
  description?: string;
  node_type: NodeType;
  status: NodeStatus;
  tool_name?: string;
  input_schema?: Record<string, any>;
  output_data?: Record<string, any>;
  can_run_parallel: boolean;
  position?: NodePosition;
  retry_count: number;
  max_retries: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowNodeCreate {
  name: string;
  description?: string;
  node_type?: NodeType;
  tool_name?: string;
  input_schema?: Record<string, any>;
  can_run_parallel?: boolean;
  position?: NodePosition;
  max_retries?: number;
}

export interface WorkflowNodeUpdate {
  name?: string;
  description?: string;
  node_type?: NodeType;
  tool_name?: string;
  input_schema?: Record<string, any>;
  can_run_parallel?: boolean;
  position?: NodePosition;
  max_retries?: number;
  status?: NodeStatus;
}

// Workflow Edge
export interface WorkflowEdge {
  id: string;
  workflow_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_type: EdgeType;
  condition?: Record<string, any>;
  created_at: string;
}

export interface WorkflowEdgeCreate {
  source_node_id: string;
  target_node_id: string;
  edge_type?: EdgeType;
  condition?: Record<string, any>;
}

// Workflow
export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: WorkflowStatus;
  llm_generated: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowDetail extends Workflow {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowCreate {
  name: string;
  description?: string;
  metadata?: Record<string, any>;
  llm_generated?: boolean;
  nodes?: WorkflowNodeCreate[];
  edges?: WorkflowEdgeCreate[];
}

export interface WorkflowUpdate {
  name?: string;
  description?: string;
  status?: WorkflowStatus;
  metadata?: Record<string, any>;
}

// Workflow Execution
export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: ExecutionStatus;
  current_node_id?: string;
  execution_context: Record<string, any>;
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface WorkflowExecutionDetail extends WorkflowExecution {
  workflow: WorkflowDetail;
}

export interface WorkflowExecutionCreate {
  execution_context?: Record<string, any>;
}

// LLM Plan Generation
export interface WorkflowPlanRequest {
  user_query: string;
  context?: Record<string, any>;
  auto_approve?: boolean;
}

export interface WorkflowPlanResponse {
  workflow: WorkflowDetail;
  plan_summary: string;
  estimated_duration?: string;
  requires_approval: boolean;
}

// Progress Updates (SSE)
export interface NodeProgressUpdate {
  execution_id: string;
  workflow_id: string;
  node_id: string;
  node_name: string;
  node_status: NodeStatus;
  progress_message: string;
  timestamp: string;
}

export interface WorkflowProgressUpdate {
  execution_id: string;
  workflow_id: string;
  workflow_status: ExecutionStatus;
  completed_nodes: number;
  total_nodes: number;
  progress_percentage: number;
  current_milestone?: string;
  timestamp: string;
}

// List Responses
export interface WorkflowListResponse {
  workflows: Workflow[];
  total: number;
  page: number;
  page_size: number;
}

export interface WorkflowExecutionListResponse {
  executions: WorkflowExecution[];
  total: number;
  page: number;
  page_size: number;
}

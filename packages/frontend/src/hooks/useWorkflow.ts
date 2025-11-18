/**
 * React hooks for workflow management
 * Provides easy-to-use hooks for components to interact with workflows
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import type {
  Workflow,
  WorkflowDetail,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowStatus,
  WorkflowExecution,
  WorkflowPlanRequest,
  WorkflowPlanResponse,
} from '@/lib/types/workflow';
import * as workflowAPI from '@/lib/api/workflows';
import type { ProgressEvent, ProgressCallback } from '@/lib/api/workflows';

// ============================================================================
// useWorkflow - Get single workflow with details
// ============================================================================

interface UseWorkflowResult {
  workflow: WorkflowDetail | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  update: (data: WorkflowUpdate) => Promise<void>;
  deleteWorkflow: () => Promise<void>;
  approve: () => Promise<void>;
  execute: () => Promise<WorkflowExecution>;
}

export function useWorkflow(workflowId: string | null): UseWorkflowResult {
  const [workflow, setWorkflow] = useState<WorkflowDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchWorkflow = useCallback(async () => {
    if (!workflowId) {
      setWorkflow(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await workflowAPI.getWorkflow(workflowId);
      setWorkflow(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [workflowId]);

  useEffect(() => {
    fetchWorkflow();
  }, [fetchWorkflow]);

  const update = useCallback(
    async (data: WorkflowUpdate) => {
      if (!workflowId) return;

      try {
        await workflowAPI.updateWorkflow(workflowId, data);
        await fetchWorkflow();
      } catch (err) {
        setError(err as Error);
        throw err;
      }
    },
    [workflowId, fetchWorkflow]
  );

  const deleteWorkflow = useCallback(async () => {
    if (!workflowId) return;

    try {
      await workflowAPI.deleteWorkflow(workflowId);
      setWorkflow(null);
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, [workflowId]);

  const approve = useCallback(async () => {
    if (!workflowId) return;

    try {
      await workflowAPI.approveWorkflow(workflowId);
      await fetchWorkflow();
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, [workflowId, fetchWorkflow]);

  const execute = useCallback(async () => {
    if (!workflowId) throw new Error('No workflow ID');

    try {
      const execution = await workflowAPI.executeWorkflow(workflowId);
      await fetchWorkflow();
      return execution;
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, [workflowId, fetchWorkflow]);

  return {
    workflow,
    loading,
    error,
    refresh: fetchWorkflow,
    update,
    deleteWorkflow,
    approve,
    execute,
  };
}

// ============================================================================
// useWorkflowList - Get list of workflows
// ============================================================================

interface UseWorkflowListResult {
  workflows: Workflow[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  setPage: (page: number) => void;
  setStatus: (status: WorkflowStatus | null) => void;
}

export function useWorkflowList(
  initialPage: number = 1,
  initialPageSize: number = 20
): UseWorkflowListResult {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialPage);
  const [pageSize] = useState(initialPageSize);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchWorkflows = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await workflowAPI.listWorkflows({
        status: status || undefined,
        page,
        page_size: pageSize,
      });
      setWorkflows(response.workflows);
      setTotal(response.total);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [status, page, pageSize]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  return {
    workflows,
    total,
    page,
    pageSize,
    loading,
    error,
    refresh: fetchWorkflows,
    setPage,
    setStatus,
  };
}

// ============================================================================
// useWorkflowGenerator - Generate workflow from natural language
// ============================================================================

interface UseWorkflowGeneratorResult {
  generating: boolean;
  error: Error | null;
  generatePlan: (
    userQuery: string,
    options?: {
      context?: Record<string, any>;
      autoApprove?: boolean;
    }
  ) => Promise<WorkflowPlanResponse>;
}

export function useWorkflowGenerator(): UseWorkflowGeneratorResult {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const generatePlan = useCallback(
    async (
      userQuery: string,
      options?: {
        context?: Record<string, any>;
        autoApprove?: boolean;
      }
    ): Promise<WorkflowPlanResponse> => {
      try {
        setGenerating(true);
        setError(null);

        const request: WorkflowPlanRequest = {
          user_query: userQuery,
          context: options?.context,
          auto_approve: options?.autoApprove || false,
        };

        const response = await workflowAPI.generateWorkflowPlan(request);
        return response;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setGenerating(false);
      }
    },
    []
  );

  return {
    generating,
    error,
    generatePlan,
  };
}

// ============================================================================
// useWorkflowExecution - Monitor workflow execution progress
// ============================================================================

interface UseWorkflowExecutionResult {
  execution: WorkflowExecution | null;
  progress: ProgressEvent[];
  loading: boolean;
  error: Error | null;
  isComplete: boolean;
  subscribe: (executionId: string) => void;
  unsubscribe: () => void;
}

export function useWorkflowExecution(): UseWorkflowExecutionResult {
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [progress, setProgress] = useState<ProgressEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [unsubscribeFn, setUnsubscribeFn] = useState<(() => void) | null>(null);

  const subscribe = useCallback((executionId: string) => {
    setLoading(true);
    setError(null);
    setIsComplete(false);
    setProgress([]);

    // Fetch initial execution state
    workflowAPI
      .getExecution(executionId)
      .then((exec) => {
        setExecution(exec);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });

    // Subscribe to SSE progress updates
    const cleanup = workflowAPI.subscribeToExecutionProgress(
      executionId,
      (event: ProgressEvent) => {
        setProgress((prev) => [...prev, event]);

        // Update execution state based on progress
        if (event.event_type === 'workflow_completed') {
          setIsComplete(true);
        }
      },
      (err: Error) => {
        setError(err);
      },
      () => {
        setIsComplete(true);
      }
    );

    setUnsubscribeFn(() => cleanup);
  }, []);

  const unsubscribe = useCallback(() => {
    if (unsubscribeFn) {
      unsubscribeFn();
      setUnsubscribeFn(null);
    }
  }, [unsubscribeFn]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (unsubscribeFn) {
        unsubscribeFn();
      }
    };
  }, [unsubscribeFn]);

  return {
    execution,
    progress,
    loading,
    error,
    isComplete,
    subscribe,
    unsubscribe,
  };
}

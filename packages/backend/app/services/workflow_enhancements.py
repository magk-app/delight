"""
Enhanced workflow features: Sub-workflows, Human-in-the-Loop, Event Triggers
These are high-impact additions that make the workflow system production-grade.
"""

from enum import Enum as PyEnum
from typing import Any, Callable
from uuid import UUID
from datetime import datetime

# ============================================================================
# FEATURE 1: Human-in-the-Loop Nodes
# ============================================================================

class HumanInputStatus(str, PyEnum):
    """Status of human input nodes."""
    WAITING = "waiting"           # Waiting for user input
    RECEIVED = "received"         # User provided input
    SKIPPED = "skipped"          # User skipped (if optional)
    TIMEOUT = "timeout"          # Timeout expired


class WorkflowNodeExtended:
    """Extended node model with human-in-the-loop support."""

    # Human input specific fields
    requires_human_input: bool = False
    input_prompt: str | None = None           # Question to ask user
    input_type: str = "text"                  # text, choice, rating, etc.
    input_options: dict[str, Any] | None = None  # For choice/rating types
    input_deadline: datetime | None = None    # Optional timeout
    human_input_status: HumanInputStatus = HumanInputStatus.WAITING
    user_response: dict[str, Any] | None = None  # User's input

    # Approval gate specific
    requires_approval: bool = False
    approval_prompt: str | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None


# ============================================================================
# FEATURE 2: Sub-Workflows (Workflow Composition)
# ============================================================================

class SubWorkflowConfig:
    """Configuration for sub-workflow execution."""

    workflow_template_id: UUID                # Which workflow to run
    parameter_mapping: dict[str, str]         # Map parent context to child params
    inherit_context: bool = True              # Share execution context
    on_failure: str = "propagate"             # propagate, continue, retry
    timeout_minutes: int | None = None


class WorkflowNodeWithSubWorkflow:
    """Node that executes another workflow."""

    sub_workflow_config: SubWorkflowConfig | None = None
    sub_workflow_execution_id: UUID | None = None  # Track child execution


# ============================================================================
# FEATURE 3: Event-Driven Workflow Triggers
# ============================================================================

class TriggerType(str, PyEnum):
    """Types of workflow triggers."""
    MANUAL = "manual"              # User manually starts
    SCHEDULE = "schedule"          # Cron-like scheduling
    WEBHOOK = "webhook"            # External API call
    USER_EVENT = "user_event"      # User action (mission, emotion, etc.)
    CONDITION = "condition"        # When condition met
    COMPLETION = "completion"      # When another workflow completes


class WorkflowTrigger:
    """Defines when/how a workflow should execute."""

    id: UUID
    workflow_id: UUID
    trigger_type: TriggerType

    # Schedule specific (cron)
    schedule_cron: str | None = None
    schedule_timezone: str = "UTC"

    # Webhook specific
    webhook_url: str | None = None
    webhook_secret: str | None = None

    # Event specific
    event_type: str | None = None         # "mission_completed", "emotion_logged"
    event_filter: dict[str, Any] | None = None  # Filter which events trigger

    # Condition specific
    condition_expression: str | None = None  # Python expression
    condition_check_interval: int = 300    # Seconds

    # Common
    enabled: bool = True
    last_triggered: datetime | None = None
    execution_context: dict[str, Any] = {}  # Initial context for execution


# ============================================================================
# FEATURE 4: Workflow Templates with Parameters
# ============================================================================

class WorkflowTemplate:
    """Reusable workflow template with parameters."""

    id: UUID
    name: str
    description: str
    category: str                    # "learning", "health", "productivity"

    # Template parameters
    parameters: list[dict[str, Any]]  # [{"name": "skill", "type": "string", "required": True}]

    # Template nodes (with {{variable}} placeholders)
    node_templates: list[dict[str, Any]]
    edge_templates: list[dict[str, Any]]

    # Metadata
    author_id: UUID | None = None
    is_public: bool = False
    usage_count: int = 0
    rating: float = 0.0
    tags: list[str] = []

    def instantiate(self, parameters: dict[str, Any]) -> dict:
        """Create concrete workflow from template with parameter values."""
        # Validate parameters
        for param in self.parameters:
            if param['required'] and param['name'] not in parameters:
                raise ValueError(f"Missing required parameter: {param['name']}")

        # Replace placeholders in nodes and edges
        import re

        def replace_placeholders(obj: Any) -> Any:
            """Recursively replace {{variable}} with actual values."""
            if isinstance(obj, str):
                # Replace {{variable}} patterns
                for key, value in parameters.items():
                    obj = re.sub(rf'\{{\{{\s*{key}\s*\}}}}', str(value), obj)
                return obj
            elif isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            return obj

        return {
            "name": replace_placeholders(self.name),
            "description": replace_placeholders(self.description),
            "nodes": replace_placeholders(self.node_templates),
            "edges": replace_placeholders(self.edge_templates),
            "metadata": {
                "template_id": str(self.id),
                "parameters": parameters
            }
        }


# ============================================================================
# FEATURE 5: Workflow Analytics & Optimization
# ============================================================================

class WorkflowAnalytics:
    """Analytics for workflow performance and optimization."""

    workflow_id: UUID

    # Performance metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration_seconds: float = 0.0
    p50_duration_seconds: float = 0.0
    p95_duration_seconds: float = 0.0

    # Cost metrics
    total_llm_tokens: int = 0
    total_cost_usd: float = 0.0
    average_cost_per_execution: float = 0.0

    # Node-level bottlenecks
    slowest_nodes: list[dict[str, Any]] = []  # [(node_id, avg_duration), ...]
    failure_prone_nodes: list[dict[str, Any]] = []  # [(node_id, failure_rate), ...]

    # Optimization suggestions
    optimization_suggestions: list[str] = []

    def analyze_and_suggest(self, executions: list[Any]) -> list[str]:
        """Analyze executions and suggest optimizations."""
        suggestions = []

        # Detect parallel opportunities
        # If nodes A and B always run sequentially but have no dependencies,
        # suggest marking them as can_run_parallel=True

        # Detect unnecessary nodes
        # If a node's output is never used, suggest removing it

        # Detect slow nodes
        # If a node consistently takes >90% of total time, investigate

        # Detect high-cost nodes
        # If LLM calls are expensive, suggest caching or cheaper models

        return suggestions


# ============================================================================
# FEATURE 6: Workflow Versioning & Rollback
# ============================================================================

class WorkflowVersion:
    """Version control for workflows."""

    id: UUID
    workflow_id: UUID
    version_number: int

    # Snapshot of workflow at this version
    snapshot: dict[str, Any]  # Complete workflow state

    # Version metadata
    created_by: UUID
    created_at: datetime
    commit_message: str
    is_production: bool = False

    # Statistics for this version
    executions: int = 0
    success_rate: float = 0.0

    def rollback(self) -> dict:
        """Restore workflow to this version."""
        return self.snapshot


# ============================================================================
# FEATURE 7: Workflow Testing Framework
# ============================================================================

class WorkflowTest:
    """Test case for workflow validation."""

    id: UUID
    workflow_id: UUID
    name: str
    description: str

    # Test input
    input_context: dict[str, Any]
    mock_tool_responses: dict[str, Any]  # Mock responses for tools

    # Expected output
    expected_final_state: dict[str, Any]
    expected_node_count: int | None = None
    expected_duration_max_seconds: int | None = None
    expected_cost_max_usd: float | None = None

    # Assertions
    assertions: list[dict[str, Any]]  # Custom assertions

    async def run(self, executor: Any) -> dict:
        """Run test and return results."""
        # Execute workflow with mocked tools
        # Validate assertions
        # Return pass/fail with details
        pass


# ============================================================================
# FEATURE 8: Workflow Marketplace & Sharing
# ============================================================================

class WorkflowMarketplace:
    """Public workflow templates marketplace."""

    def search_templates(
        self,
        query: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        min_rating: float = 0.0,
        sort_by: str = "popularity"  # popularity, rating, recent
    ) -> list[WorkflowTemplate]:
        """Search public workflow templates."""
        pass

    def publish_template(
        self,
        workflow_id: UUID,
        is_public: bool = True
    ) -> WorkflowTemplate:
        """Publish workflow as reusable template."""
        pass

    def fork_template(
        self,
        template_id: UUID,
        user_id: UUID
    ) -> UUID:
        """Create user's own copy of a template."""
        pass


# ============================================================================
# FEATURE 9: Intelligent Workflow Suggestions
# ============================================================================

class WorkflowSuggestionEngine:
    """AI-powered workflow recommendations."""

    async def suggest_for_goal(
        self,
        user_id: UUID,
        goal_description: str,
        user_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Suggest workflows based on user's goal.

        Considers:
        - User's past workflows
        - Similar users' successful workflows
        - Goal category and complexity
        - User's skill level and preferences
        """
        pass

    async def optimize_workflow(
        self,
        workflow_id: UUID,
        optimization_goals: list[str]  # ["speed", "cost", "reliability"]
    ) -> dict[str, Any]:
        """
        Suggest optimizations for existing workflow.

        Uses LLM to analyze workflow structure and suggest:
        - Parallelization opportunities
        - Node consolidation
        - Caching strategies
        - Cheaper alternatives
        """
        pass

    async def auto_parallelize(
        self,
        workflow_id: UUID
    ) -> list[tuple[UUID, UUID]]:
        """
        Automatically detect which nodes can run in parallel.

        Analyzes data dependencies to find independent nodes.
        """
        pass


# ============================================================================
# FEATURE 10: Advanced Error Handling & Circuit Breakers
# ============================================================================

class CircuitBreakerState(str, PyEnum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Too many failures, stop trying
    HALF_OPEN = "half_open"  # Testing if issue resolved


class WorkflowCircuitBreaker:
    """Prevent cascading failures in workflows."""

    workflow_id: UUID
    state: CircuitBreakerState = CircuitBreakerState.CLOSED

    # Configuration
    failure_threshold: int = 5        # Failures before opening
    success_threshold: int = 2        # Successes to close from half-open
    timeout_seconds: int = 60         # Time before trying again

    # State tracking
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: datetime | None = None

    def record_success(self):
        """Record successful execution."""
        self.consecutive_failures = 0
        self.consecutive_successes += 1

        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.consecutive_successes >= self.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.consecutive_successes = 0

    def record_failure(self):
        """Record failed execution."""
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def can_execute(self) -> bool:
        """Check if workflow can execute."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout expired
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).seconds
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
            return False

        # HALF_OPEN - allow limited attempts
        return True

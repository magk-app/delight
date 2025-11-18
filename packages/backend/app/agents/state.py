"""Goal-driven state management for AI agents"""
from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import operator


class AgentState(str, Enum):
    """Enumeration of agent states

    These states represent the agent's current position in the task workflow.
    State transitions are goal-driven and based on the available information
    and tool outputs.
    """
    # Initial state - understanding what the user wants
    INITIALIZE = "initialize"

    # Planning state - determining what steps are needed
    PLANNING = "planning"

    # Clarifying state - asking user questions when info is missing
    CLARIFYING = "clarifying"

    # Tool selection - choosing appropriate tools based on goal
    TOOL_SELECTION = "tool_selection"

    # Tool execution - running selected tools
    TOOL_EXECUTION = "tool_execution"

    # Analysis - processing tool outputs and determining next steps
    ANALYSIS = "analysis"

    # Synthesis - combining information to form the answer
    SYNTHESIS = "synthesis"

    # Completion - task is done, ready to respond
    COMPLETION = "completion"

    # Error - something went wrong, need to handle it
    ERROR = "error"


class Goal(BaseModel):
    """Represents a goal the agent is trying to achieve"""
    description: str = Field(description="Natural language description of the goal")
    constraints: List[str] = Field(
        default_factory=list,
        description="Constraints on how to achieve the goal"
    )
    required_info: List[str] = Field(
        default_factory=list,
        description="Information required to achieve the goal"
    )
    sub_goals: List["Goal"] = Field(
        default_factory=list,
        description="Sub-goals that need to be achieved"
    )
    is_completed: bool = Field(default=False, description="Whether this goal is achieved")
    completion_criteria: Optional[str] = Field(
        default=None,
        description="Criteria for determining goal completion"
    )


class Message(BaseModel):
    """Represents a message in the conversation"""
    role: str = Field(description="Role of the message sender (user, assistant, system)")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ToolExecution(BaseModel):
    """Record of a tool execution"""
    tool_name: str
    input_data: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    success: bool = False
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class GraphState(TypedDict):
    """The state that flows through the LangGraph

    This is the "blackboard" where all information is shared between
    different nodes and tools in the agent workflow.

    TypedDict is used for LangGraph compatibility, but we also use
    Annotated with operator.add for list fields to enable appending.
    """
    # Core workflow state
    current_state: AgentState
    previous_state: Optional[AgentState]

    # Goal and task information
    goal: Optional[Goal]
    user_request: str

    # Conversation history
    messages: Annotated[Sequence[Message], operator.add]

    # Tool-related state
    available_tools: List[str]
    selected_tools: List[str]
    tool_executions: Annotated[Sequence[ToolExecution], operator.add]
    tool_outputs: Dict[str, Any]  # Shared context from tool outputs

    # Information gathering
    required_information: List[str]  # What info is needed
    available_information: Dict[str, Any]  # What info we have
    questions_for_user: List[str]  # Questions to ask user

    # Planning and reasoning
    plan: Optional[str]  # Current execution plan
    reasoning: Optional[str]  # Current reasoning about next steps
    confidence: float  # Confidence in current approach (0-1)

    # Progress tracking
    sub_goals_completed: List[str]
    iterations: int  # Number of iterations through the graph

    # Final output
    final_response: Optional[str]
    error_message: Optional[str]


class StateManager:
    """Manages state transitions and provides utilities for state manipulation

    This class encapsulates the logic for:
    - Determining valid state transitions
    - Checking goal completion
    - Managing the information blackboard
    - Tracking tool usage to avoid redundancy
    """

    # Valid state transitions (from_state -> [to_states])
    VALID_TRANSITIONS: Dict[AgentState, List[AgentState]] = {
        AgentState.INITIALIZE: [
            AgentState.PLANNING,
            AgentState.CLARIFYING,
            AgentState.ERROR
        ],
        AgentState.PLANNING: [
            AgentState.CLARIFYING,
            AgentState.TOOL_SELECTION,
            AgentState.SYNTHESIS,  # If no tools needed
            AgentState.ERROR
        ],
        AgentState.CLARIFYING: [
            AgentState.PLANNING,  # After getting clarification
            AgentState.COMPLETION,  # If can't proceed
            AgentState.ERROR
        ],
        AgentState.TOOL_SELECTION: [
            AgentState.TOOL_EXECUTION,
            AgentState.CLARIFYING,  # If need more info to select tools
            AgentState.ERROR
        ],
        AgentState.TOOL_EXECUTION: [
            AgentState.ANALYSIS,
            AgentState.ERROR
        ],
        AgentState.ANALYSIS: [
            AgentState.TOOL_SELECTION,  # Need more tool calls
            AgentState.SYNTHESIS,  # Have enough information
            AgentState.CLARIFYING,  # Need user input
            AgentState.ERROR
        ],
        AgentState.SYNTHESIS: [
            AgentState.COMPLETION,
            AgentState.ANALYSIS,  # If synthesis reveals gaps
            AgentState.ERROR
        ],
        AgentState.COMPLETION: [],  # Terminal state
        AgentState.ERROR: [
            AgentState.CLARIFYING,  # Try to recover
            AgentState.COMPLETION  # Give up gracefully
        ]
    }

    @staticmethod
    def is_valid_transition(from_state: AgentState, to_state: AgentState) -> bool:
        """Check if a state transition is valid"""
        return to_state in StateManager.VALID_TRANSITIONS.get(from_state, [])

    @staticmethod
    def get_next_states(current_state: AgentState) -> List[AgentState]:
        """Get list of valid next states"""
        return StateManager.VALID_TRANSITIONS.get(current_state, [])

    @staticmethod
    def create_initial_state(user_request: str) -> GraphState:
        """Create initial state for a new task"""
        return GraphState(
            current_state=AgentState.INITIALIZE,
            previous_state=None,
            goal=None,
            user_request=user_request,
            messages=[],
            available_tools=[],
            selected_tools=[],
            tool_executions=[],
            tool_outputs={},
            required_information=[],
            available_information={},
            questions_for_user=[],
            plan=None,
            reasoning=None,
            confidence=0.5,
            sub_goals_completed=[],
            iterations=0,
            final_response=None,
            error_message=None
        )

    @staticmethod
    def transition_to(state: GraphState, new_state: AgentState, reasoning: str) -> GraphState:
        """Transition to a new state with validation

        Args:
            state: Current state
            new_state: Target state
            reasoning: Reason for the transition

        Returns:
            Updated state

        Raises:
            ValueError: If transition is invalid
        """
        current = AgentState(state["current_state"])

        if not StateManager.is_valid_transition(current, new_state):
            raise ValueError(
                f"Invalid state transition: {current} -> {new_state}. "
                f"Valid transitions from {current}: {StateManager.get_next_states(current)}"
            )

        state["previous_state"] = state["current_state"]
        state["current_state"] = new_state
        state["reasoning"] = reasoning
        state["iterations"] += 1

        return state

    @staticmethod
    def has_required_information(state: GraphState) -> bool:
        """Check if all required information is available"""
        required = state.get("required_information", [])
        available = state.get("available_information", {})

        return all(key in available for key in required)

    @staticmethod
    def get_missing_information(state: GraphState) -> List[str]:
        """Get list of missing required information"""
        required = state.get("required_information", [])
        available = state.get("available_information", {})

        return [key for key in required if key not in available]

    @staticmethod
    def was_tool_used(state: GraphState, tool_name: str) -> bool:
        """Check if a tool was already used (avoid redundancy)"""
        executions = state.get("tool_executions", [])
        return any(exec["tool_name"] == tool_name for exec in executions)

    @staticmethod
    def get_tool_result(state: GraphState, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the result of a previous tool execution"""
        executions = state.get("tool_executions", [])
        for exec in reversed(executions):  # Get most recent
            if exec["tool_name"] == tool_name and exec["success"]:
                return exec["output"]
        return None

    @staticmethod
    def should_ask_clarification(state: GraphState) -> bool:
        """Determine if the agent should ask for clarification"""
        # Ask if we're missing required info and have tried other approaches
        missing_info = StateManager.get_missing_information(state)
        iterations = state.get("iterations", 0)

        return bool(missing_info) and iterations > 1

    @staticmethod
    def is_goal_achieved(state: GraphState) -> bool:
        """Check if the main goal has been achieved"""
        goal = state.get("goal")
        if not goal:
            return False

        # Check if we have enough information for a response
        has_info = StateManager.has_required_information(state)

        # Check if all sub-goals are completed
        if goal.sub_goals:
            all_completed = all(sg.is_completed for sg in goal.sub_goals)
            return has_info and all_completed

        return has_info

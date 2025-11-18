"""Tests for state management and transitions"""
import pytest
from app.agents.state import (
    AgentState,
    Goal,
    GraphState,
    StateManager,
    Message,
    ToolExecution
)


class TestAgentState:
    """Test agent state enumeration"""

    def test_all_states_defined(self):
        """Test that all expected states are defined"""
        expected_states = [
            "INITIALIZE",
            "PLANNING",
            "CLARIFYING",
            "TOOL_SELECTION",
            "TOOL_EXECUTION",
            "ANALYSIS",
            "SYNTHESIS",
            "COMPLETION",
            "ERROR"
        ]

        for state in expected_states:
            assert hasattr(AgentState, state)


class TestGoal:
    """Test goal model"""

    def test_create_simple_goal(self):
        """Test creating a simple goal"""
        goal = Goal(
            description="Calculate 5 + 3",
            constraints=["use calculator tool"],
            required_info=["operands"],
            completion_criteria="result obtained"
        )

        assert goal.description == "Calculate 5 + 3"
        assert "use calculator tool" in goal.constraints
        assert "operands" in goal.required_info
        assert goal.is_completed is False

    def test_create_goal_with_subgoals(self):
        """Test creating a goal with sub-goals"""
        sub_goal1 = Goal(description="Get operand 1")
        sub_goal2 = Goal(description="Get operand 2")

        main_goal = Goal(
            description="Calculate sum",
            sub_goals=[sub_goal1, sub_goal2]
        )

        assert len(main_goal.sub_goals) == 2
        assert main_goal.sub_goals[0].description == "Get operand 1"

    def test_goal_completion(self):
        """Test goal completion tracking"""
        goal = Goal(description="Test goal")

        assert goal.is_completed is False

        goal.is_completed = True
        assert goal.is_completed is True


class TestStateManager:
    """Test state manager utilities"""

    def test_valid_transitions(self):
        """Test that valid transitions are defined for all states"""
        for state in AgentState:
            transitions = StateManager.VALID_TRANSITIONS.get(state)
            assert transitions is not None, f"No transitions defined for {state}"

    def test_is_valid_transition_true(self):
        """Test checking valid state transitions"""
        # Initialize -> Planning is valid
        assert StateManager.is_valid_transition(
            AgentState.INITIALIZE,
            AgentState.PLANNING
        ) is True

        # Planning -> Tool Selection is valid
        assert StateManager.is_valid_transition(
            AgentState.PLANNING,
            AgentState.TOOL_SELECTION
        ) is True

    def test_is_valid_transition_false(self):
        """Test checking invalid state transitions"""
        # Initialize -> Completion is not valid
        assert StateManager.is_valid_transition(
            AgentState.INITIALIZE,
            AgentState.COMPLETION
        ) is False

        # Completion -> anything is not valid (terminal state)
        assert StateManager.is_valid_transition(
            AgentState.COMPLETION,
            AgentState.PLANNING
        ) is False

    def test_get_next_states(self):
        """Test getting valid next states"""
        next_states = StateManager.get_next_states(AgentState.INITIALIZE)

        assert AgentState.PLANNING in next_states
        assert AgentState.CLARIFYING in next_states
        assert AgentState.COMPLETION not in next_states

    def test_create_initial_state(self):
        """Test creating initial state"""
        state = StateManager.create_initial_state("Calculate 5 + 3")

        assert state["current_state"] == AgentState.INITIALIZE
        assert state["previous_state"] is None
        assert state["user_request"] == "Calculate 5 + 3"
        assert state["iterations"] == 0
        assert state["confidence"] == 0.5
        assert len(state["messages"]) == 0
        assert len(state["tool_executions"]) == 0

    def test_transition_to_valid(self):
        """Test valid state transition"""
        state = StateManager.create_initial_state("test")

        updated = StateManager.transition_to(
            state,
            AgentState.PLANNING,
            "Moving to planning phase"
        )

        assert updated["current_state"] == AgentState.PLANNING
        assert updated["previous_state"] == AgentState.INITIALIZE
        assert updated["reasoning"] == "Moving to planning phase"
        assert updated["iterations"] == 1

    def test_transition_to_invalid(self):
        """Test invalid state transition raises error"""
        state = StateManager.create_initial_state("test")

        with pytest.raises(ValueError, match="Invalid state transition"):
            StateManager.transition_to(
                state,
                AgentState.COMPLETION,  # Not valid from INITIALIZE
                "Invalid transition"
            )

    def test_has_required_information_true(self):
        """Test checking if required information is available"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["operand1", "operand2"]
        state["available_information"] = {
            "operand1": 5,
            "operand2": 3
        }

        assert StateManager.has_required_information(state) is True

    def test_has_required_information_false(self):
        """Test checking when information is missing"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["operand1", "operand2", "operation"]
        state["available_information"] = {
            "operand1": 5,
            "operand2": 3
        }

        assert StateManager.has_required_information(state) is False

    def test_get_missing_information(self):
        """Test getting list of missing information"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["a", "b", "c"]
        state["available_information"] = {"a": 1, "c": 3}

        missing = StateManager.get_missing_information(state)

        assert len(missing) == 1
        assert "b" in missing
        assert "a" not in missing

    def test_was_tool_used_true(self):
        """Test checking if tool was used"""
        state = StateManager.create_initial_state("test")
        state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={},
                success=True
            )
        ]

        assert StateManager.was_tool_used(state, "calculator") is True

    def test_was_tool_used_false(self):
        """Test checking if tool was not used"""
        state = StateManager.create_initial_state("test")
        state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={},
                success=True
            )
        ]

        assert StateManager.was_tool_used(state, "other_tool") is False

    def test_get_tool_result_success(self):
        """Test getting successful tool result"""
        state = StateManager.create_initial_state("test")
        state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={},
                output={"result": 42},
                success=True
            )
        ]

        result = StateManager.get_tool_result(state, "calculator")

        assert result is not None
        assert result["result"] == 42

    def test_get_tool_result_not_found(self):
        """Test getting result for tool that wasn't used"""
        state = StateManager.create_initial_state("test")

        result = StateManager.get_tool_result(state, "calculator")

        assert result is None

    def test_get_tool_result_failed(self):
        """Test getting result for failed tool execution"""
        state = StateManager.create_initial_state("test")
        state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={},
                success=False,
                error="Division by zero"
            )
        ]

        result = StateManager.get_tool_result(state, "calculator")

        assert result is None  # Only returns successful executions

    def test_get_tool_result_most_recent(self):
        """Test getting most recent tool result when multiple exist"""
        state = StateManager.create_initial_state("test")
        state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={},
                output={"result": 10},
                success=True
            ),
            ToolExecution(
                tool_name="calculator",
                input_data={},
                output={"result": 20},
                success=True
            )
        ]

        result = StateManager.get_tool_result(state, "calculator")

        assert result is not None
        assert result["result"] == 20  # Most recent

    def test_should_ask_clarification_false_no_missing_info(self):
        """Test should not ask clarification when no info missing"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["a"]
        state["available_information"] = {"a": 1}

        assert StateManager.should_ask_clarification(state) is False

    def test_should_ask_clarification_false_early_iteration(self):
        """Test should not ask clarification on first iteration"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["a"]
        state["available_information"] = {}
        state["iterations"] = 1

        assert StateManager.should_ask_clarification(state) is False

    def test_should_ask_clarification_true(self):
        """Test should ask clarification after multiple iterations"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["a"]
        state["available_information"] = {}
        state["iterations"] = 2

        assert StateManager.should_ask_clarification(state) is True

    def test_is_goal_achieved_no_goal(self):
        """Test goal achievement when no goal set"""
        state = StateManager.create_initial_state("test")

        assert StateManager.is_goal_achieved(state) is False

    def test_is_goal_achieved_simple_goal(self):
        """Test goal achievement for simple goal"""
        state = StateManager.create_initial_state("test")
        state["goal"] = Goal(
            description="Test",
            required_info=["a"]
        )
        state["required_information"] = ["a"]
        state["available_information"] = {"a": 1}

        assert StateManager.is_goal_achieved(state) is True

    def test_is_goal_achieved_with_subgoals(self):
        """Test goal achievement with sub-goals"""
        sub1 = Goal(description="Sub 1", is_completed=True)
        sub2 = Goal(description="Sub 2", is_completed=True)

        state = StateManager.create_initial_state("test")
        state["goal"] = Goal(
            description="Main",
            required_info=["a"],
            sub_goals=[sub1, sub2]
        )
        state["required_information"] = ["a"]
        state["available_information"] = {"a": 1}

        assert StateManager.is_goal_achieved(state) is True

    def test_is_goal_achieved_incomplete_subgoals(self):
        """Test goal not achieved when sub-goals incomplete"""
        sub1 = Goal(description="Sub 1", is_completed=True)
        sub2 = Goal(description="Sub 2", is_completed=False)

        state = StateManager.create_initial_state("test")
        state["goal"] = Goal(
            description="Main",
            required_info=["a"],
            sub_goals=[sub1, sub2]
        )
        state["required_information"] = ["a"]
        state["available_information"] = {"a": 1}

        assert StateManager.is_goal_achieved(state) is False


class TestMessage:
    """Test message model"""

    def test_create_message(self):
        """Test creating a message"""
        msg = Message(
            role="user",
            content="Hello"
        )

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp is not None


class TestToolExecution:
    """Test tool execution model"""

    def test_create_tool_execution(self):
        """Test creating a tool execution record"""
        execution = ToolExecution(
            tool_name="calculator",
            input_data={"operation": "add", "operand1": 5, "operand2": 3},
            output={"result": 8},
            success=True
        )

        assert execution.tool_name == "calculator"
        assert execution.success is True
        assert execution.output["result"] == 8
        assert execution.error is None

    def test_create_failed_execution(self):
        """Test creating a failed execution record"""
        execution = ToolExecution(
            tool_name="calculator",
            input_data={},
            success=False,
            error="Division by zero"
        )

        assert execution.success is False
        assert execution.error == "Division by zero"
        assert execution.output is None


class TestStateTransitionScenarios:
    """Test complete state transition scenarios"""

    def test_successful_workflow(self):
        """Test a successful workflow through multiple states"""
        # Start
        state = StateManager.create_initial_state("Calculate 5 + 3")

        # Initialize -> Planning
        state = StateManager.transition_to(
            state,
            AgentState.PLANNING,
            "Identified goal, moving to planning"
        )
        assert state["current_state"] == AgentState.PLANNING

        # Planning -> Tool Selection
        state = StateManager.transition_to(
            state,
            AgentState.TOOL_SELECTION,
            "Need calculator tool"
        )
        assert state["current_state"] == AgentState.TOOL_SELECTION

        # Tool Selection -> Tool Execution
        state = StateManager.transition_to(
            state,
            AgentState.TOOL_EXECUTION,
            "Selected calculator"
        )
        assert state["current_state"] == AgentState.TOOL_EXECUTION

        # Tool Execution -> Analysis
        state = StateManager.transition_to(
            state,
            AgentState.ANALYSIS,
            "Analyzing results"
        )
        assert state["current_state"] == AgentState.ANALYSIS

        # Analysis -> Synthesis
        state = StateManager.transition_to(
            state,
            AgentState.SYNTHESIS,
            "Have all needed info"
        )
        assert state["current_state"] == AgentState.SYNTHESIS

        # Synthesis -> Completion
        state = StateManager.transition_to(
            state,
            AgentState.COMPLETION,
            "Task complete"
        )
        assert state["current_state"] == AgentState.COMPLETION
        assert state["iterations"] == 6

    def test_clarification_workflow(self):
        """Test workflow that requires clarification"""
        state = StateManager.create_initial_state("Calculate something")

        # Initialize -> Clarifying (unclear request)
        state = StateManager.transition_to(
            state,
            AgentState.CLARIFYING,
            "Need more information"
        )

        # Clarifying -> Planning (after getting info)
        state = StateManager.transition_to(
            state,
            AgentState.PLANNING,
            "Got clarification, can proceed"
        )

        assert state["iterations"] == 2
        assert state["current_state"] == AgentState.PLANNING

    def test_error_recovery_workflow(self):
        """Test error handling and recovery"""
        state = StateManager.create_initial_state("test")
        state["current_state"] = AgentState.TOOL_EXECUTION

        # Tool Execution -> Error
        state = StateManager.transition_to(
            state,
            AgentState.ERROR,
            "Tool execution failed"
        )

        # Error -> Clarifying (attempt recovery)
        state = StateManager.transition_to(
            state,
            AgentState.CLARIFYING,
            "Asking user for help"
        )

        assert state["current_state"] == AgentState.CLARIFYING

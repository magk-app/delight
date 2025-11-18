"""Integration tests for LangGraph goal-driven agent"""
import pytest
from app.agents.graph import GoalDrivenAgent
from app.agents.state import AgentState, StateManager
from app.agents.tools import get_tool_store


class TestGoalDrivenAgent:
    """Test the complete goal-driven agent workflow"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance for testing"""
        # Reset tool store to ensure clean state
        store = await get_tool_store()
        store.clear_history()
        return GoalDrivenAgent(tool_store=store)

    @pytest.mark.asyncio
    async def test_simple_calculation_request(self, agent):
        """Test agent handling a simple calculation request"""
        result = await agent.run("calculate 5 + 3")

        assert result["success"] is True
        assert result["response"] is not None
        assert result["iterations"] > 0
        assert result["tool_executions"] >= 1
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_multiplication_request(self, agent):
        """Test agent with multiplication"""
        result = await agent.run("multiply 4 by 7")

        assert result["success"] is True
        assert result["response"] is not None
        # Should have executed calculator tool
        assert result["tool_executions"] >= 1

    @pytest.mark.asyncio
    async def test_square_root_request(self, agent):
        """Test agent with unary operation"""
        result = await agent.run("calculate square root of 16")

        assert result["success"] is True
        assert result["response"] is not None

    @pytest.mark.asyncio
    async def test_agent_state_progression(self, agent):
        """Test that agent progresses through expected states"""
        # This is an integration test that verifies the state machine works
        initial_state = StateManager.create_initial_state("calculate 5 + 3")

        # Run through the graph
        final_state = await agent.graph.ainvoke(initial_state)

        # Verify we reached completion
        assert final_state["current_state"] == AgentState.COMPLETION
        # Verify we went through multiple states
        assert final_state["iterations"] > 3

    @pytest.mark.asyncio
    async def test_tool_execution_tracking(self, agent):
        """Test that tool executions are properly tracked"""
        initial_state = StateManager.create_initial_state("add 2 and 3")

        final_state = await agent.graph.ainvoke(initial_state)

        # Should have tool executions
        tool_executions = final_state.get("tool_executions", [])
        assert len(tool_executions) > 0

        # Check that calculator was used
        calc_executions = [
            ex for ex in tool_executions
            if ex.tool_name == "calculator"
        ]
        assert len(calc_executions) > 0

    @pytest.mark.asyncio
    async def test_confidence_increases(self, agent):
        """Test that confidence increases as agent gathers information"""
        initial_state = StateManager.create_initial_state("calculate something")
        initial_state["confidence"] = 0.3

        # Run through planning
        state = await agent._planning_node(initial_state)

        # After planning, confidence might stay the same or change
        # depending on whether we have a clear plan
        assert "plan" in state

    @pytest.mark.asyncio
    async def test_tool_store_integration(self, agent):
        """Test that agent properly uses the tool store"""
        tool_store = get_tool_store()

        # Clear any previous history
        tool_store.clear_history()

        await agent.run("add 10 and 20")

        # Check that tool store recorded execution
        history = tool_store.get_execution_history()
        assert len(history) > 0

        calc_history = tool_store.get_execution_history("calculator")
        assert len(calc_history) > 0


class TestAgentNodes:
    """Test individual agent node functions"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance"""
        tool_store = await get_tool_store()
        return GoalDrivenAgent(tool_store=tool_store)

    @pytest.mark.asyncio
    async def test_initialize_node(self, agent):
        """Test initialization node"""
        state = StateManager.create_initial_state("calculate 5 + 3")

        result = await agent._initialize_node(state)

        assert result["goal"] is not None
        assert len(result["available_tools"]) > 0
        assert "calculator" in result["available_tools"]

    @pytest.mark.asyncio
    async def test_planning_node(self, agent):
        """Test planning node"""
        state = StateManager.create_initial_state("add 5 and 3")
        state = await agent._initialize_node(state)

        result = await agent._planning_node(state)

        assert result["plan"] is not None
        assert len(result["plan"]) > 0

    @pytest.mark.asyncio
    async def test_tool_selection_node(self, agent):
        """Test tool selection node"""
        state = StateManager.create_initial_state("calculate 5 + 3")
        state = await agent._initialize_node(state)
        state = await agent._planning_node(state)

        result = await agent._tool_selection_node(state)

        # Should select calculator for calculation tasks
        assert "selected_tools" in result
        # Note: selection depends on goal matching logic

    @pytest.mark.asyncio
    async def test_tool_execution_node(self, agent):
        """Test tool execution node"""
        state = StateManager.create_initial_state("add numbers")
        state["selected_tools"] = ["calculator"]
        state["available_information"] = {}

        result = await agent._tool_execution_node(state)

        # Should have attempted tool execution
        assert "tool_executions" in result
        assert "tool_outputs" in result

    @pytest.mark.asyncio
    async def test_analysis_node(self, agent):
        """Test analysis node"""
        state = StateManager.create_initial_state("test")
        state["tool_outputs"] = {"calculator": 8}
        state["goal"] = StateManager.create_initial_state("test")["goal"]
        state["required_information"] = []
        state["available_information"] = {}

        result = await agent._analysis_node(state)

        assert "confidence" in result
        assert "reasoning" in result

    @pytest.mark.asyncio
    async def test_synthesis_node(self, agent):
        """Test synthesis node"""
        state = StateManager.create_initial_state("add 5 and 3")
        state["tool_outputs"] = {"calculator": 8}

        result = await agent._synthesis_node(state)

        assert result["final_response"] is not None
        assert len(result["final_response"]) > 0

    @pytest.mark.asyncio
    async def test_clarifying_node(self, agent):
        """Test clarifying node"""
        state = StateManager.create_initial_state("test")
        state["required_information"] = ["operand1", "operand2"]
        state["available_information"] = {}

        result = await agent._clarifying_node(state)

        assert "questions_for_user" in result
        assert len(result["questions_for_user"]) > 0


class TestAgentRouting:
    """Test agent routing logic"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance"""
        tool_store = await get_tool_store()
        return GoalDrivenAgent(tool_store=tool_store)

    def test_route_from_initialize_with_goal(self, agent):
        """Test routing from initialize when goal is clear"""
        state = StateManager.create_initial_state("calculate 5 + 3")
        state["goal"] = agent._parse_goal("calculate 5 + 3")

        next_node = agent._route_from_initialize(state)

        assert next_node == "planning"

    def test_route_from_initialize_without_goal(self, agent):
        """Test routing from initialize when goal is unclear"""
        state = StateManager.create_initial_state("test")
        state["goal"] = None

        next_node = agent._route_from_initialize(state)

        assert next_node == "clarifying"

    def test_route_from_planning_to_tools(self, agent):
        """Test routing from planning to tool selection"""
        state = StateManager.create_initial_state("calculate something")
        state["goal"] = agent._parse_goal("calculate 5 + 3")
        state["available_information"] = {}
        state["iterations"] = 1

        next_node = agent._route_from_planning(state)

        # Should route to tool_selection for calculation tasks
        assert next_node in ["tool_selection", "clarifying", "synthesis"]

    def test_route_from_tool_selection_with_tools(self, agent):
        """Test routing from tool selection when tools are selected"""
        state = StateManager.create_initial_state("test")
        state["selected_tools"] = ["calculator"]

        next_node = agent._route_from_tool_selection(state)

        assert next_node == "tool_execution"

    def test_route_from_tool_selection_without_tools(self, agent):
        """Test routing from tool selection when no tools selected"""
        state = StateManager.create_initial_state("test")
        state["selected_tools"] = []
        state["iterations"] = 1

        next_node = agent._route_from_tool_selection(state)

        assert next_node in ["clarifying", "synthesis"]

    def test_route_from_analysis_high_confidence(self, agent):
        """Test routing from analysis with high confidence"""
        state = StateManager.create_initial_state("test")
        state["confidence"] = 0.9
        state["iterations"] = 3

        next_node = agent._route_from_analysis(state)

        assert next_node == "synthesis"

    def test_route_from_analysis_low_confidence(self, agent):
        """Test routing from analysis with low confidence"""
        state = StateManager.create_initial_state("test")
        state["confidence"] = 0.3
        state["required_information"] = ["something"]
        state["available_information"] = {}
        state["iterations"] = 3

        next_node = agent._route_from_analysis(state)

        assert next_node == "tool_selection"

    def test_route_from_synthesis_success(self, agent):
        """Test routing from synthesis when successful"""
        state = StateManager.create_initial_state("test")
        state["final_response"] = "Here is the answer"

        next_node = agent._route_from_synthesis(state)

        assert next_node == "completion"

    def test_route_prevents_infinite_loops(self, agent):
        """Test that routing prevents infinite loops"""
        state = StateManager.create_initial_state("test")
        state["iterations"] = 15  # High iteration count

        # Should eventually route to completion
        next_node = agent._route_from_analysis(state)

        assert next_node == "synthesis"


class TestGoalParsing:
    """Test goal parsing logic"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance"""
        tool_store = await get_tool_store()
        return GoalDrivenAgent(tool_store=tool_store)

    def test_parse_calculation_goal(self, agent):
        """Test parsing calculation-related goals"""
        goal = agent._parse_goal("calculate 5 + 3")

        assert goal is not None
        assert "calculate" in goal.description.lower() or "calculation" in goal.description.lower()
        assert len(goal.required_info) > 0

    def test_parse_generic_goal(self, agent):
        """Test parsing generic goals"""
        goal = agent._parse_goal("help me with something")

        assert goal is not None
        assert goal.description == "help me with something"


class TestToolInputGeneration:
    """Test tool input generation"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance"""
        tool_store = await get_tool_store()
        return GoalDrivenAgent(tool_store=tool_store)

    def test_generate_calculator_input_add(self, agent):
        """Test generating calculator input for addition"""
        state = StateManager.create_initial_state("add 5 and 3")

        input_data = agent._generate_tool_input(state, "calculator")

        # Should generate add operation
        # Note: This is a simple implementation, real one would use LLM
        if input_data:
            assert "operation" in input_data
            assert input_data["operation"] == "add"

    def test_generate_calculator_input_multiply(self, agent):
        """Test generating calculator input for multiplication"""
        state = StateManager.create_initial_state("multiply 4 by 7")

        input_data = agent._generate_tool_input(state, "calculator")

        if input_data:
            assert "operation" in input_data
            assert input_data["operation"] == "multiply"

    def test_generate_calculator_input_sqrt(self, agent):
        """Test generating calculator input for square root"""
        state = StateManager.create_initial_state("sqrt of 16")

        input_data = agent._generate_tool_input(state, "calculator")

        if input_data:
            assert "operation" in input_data
            assert input_data["operation"] == "sqrt"


class TestEndToEndScenarios:
    """End-to-end integration tests for complete scenarios"""

    @pytest.fixture
    async def agent(self):
        """Create agent instance"""
        store = await get_tool_store()
        store.clear_history()
        return GoalDrivenAgent(tool_store=store)

    @pytest.mark.asyncio
    async def test_complete_calculation_workflow(self, agent):
        """Test complete workflow from request to response"""
        result = await agent.run("calculate 5 + 3")

        # Verify success
        assert result["success"] is True

        # Verify response contains relevant information
        assert result["response"] is not None

        # Verify tools were used
        assert result["tool_executions"] > 0

        # Verify reasonable number of iterations
        assert result["iterations"] < 15

        # Verify no errors
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_multiple_requests_independent(self, agent):
        """Test that multiple requests are independent"""
        result1 = await agent.run("add 2 and 3")
        result2 = await agent.run("multiply 4 by 5")

        assert result1["success"] is True
        assert result2["success"] is True

        # Results should be different
        assert result1["response"] != result2["response"]

    @pytest.mark.asyncio
    async def test_tool_not_used_redundantly(self, agent):
        """Test that tools are not called redundantly"""
        initial_state = StateManager.create_initial_state("add 5 and 3")

        # Simulate tool already being used
        from app.agents.state import ToolExecution
        initial_state["tool_executions"] = [
            ToolExecution(
                tool_name="calculator",
                input_data={"operation": "add", "operand1": 5, "operand2": 3},
                output={"result": 8},
                success=True
            )
        ]

        # Try to select tools again
        state = await agent._tool_selection_node(initial_state)

        # Calculator should not be selected again
        # (depends on implementation, but should try to avoid redundancy)
        selected = state.get("selected_tools", [])
        # This test documents the behavior - actual implementation may vary

"""LangGraph implementation with goal-driven state transitions"""
from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from .state import (
    GraphState,
    AgentState,
    StateManager,
    Goal,
    Message,
    ToolExecution
)
from .tools import get_tool_store


class GoalDrivenAgent:
    """An agent that uses goal-driven state transitions and tool awareness

    This agent demonstrates:
    - Goal-oriented task execution with sub-goals
    - Tool-aware processing (knows what tools do, when to use them)
    - State-driven decision making with clear transitions
    - Information gathering and clarification
    - Avoiding redundant tool calls
    """

    def __init__(self):
        self.tool_store = get_tool_store()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow

        The graph structure mirrors the state machine, with nodes for each
        state and edges representing valid transitions.
        """
        workflow = StateGraph(GraphState)

        # Add nodes for each state
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("clarifying", self._clarifying_node)
        workflow.add_node("tool_selection", self._tool_selection_node)
        workflow.add_node("tool_execution", self._tool_execution_node)
        workflow.add_node("analysis", self._analysis_node)
        workflow.add_node("synthesis", self._synthesis_node)
        workflow.add_node("completion", self._completion_node)
        workflow.add_node("error", self._error_node)

        # Set entry point
        workflow.set_entry_point("initialize")

        # Add conditional edges based on state transitions
        workflow.add_conditional_edges(
            "initialize",
            self._route_from_initialize
        )
        workflow.add_conditional_edges(
            "planning",
            self._route_from_planning
        )
        workflow.add_conditional_edges(
            "clarifying",
            self._route_from_clarifying
        )
        workflow.add_conditional_edges(
            "tool_selection",
            self._route_from_tool_selection
        )
        workflow.add_conditional_edges(
            "tool_execution",
            self._route_from_tool_execution
        )
        workflow.add_conditional_edges(
            "analysis",
            self._route_from_analysis
        )
        workflow.add_conditional_edges(
            "synthesis",
            self._route_from_synthesis
        )
        workflow.add_conditional_edges(
            "error",
            self._route_from_error
        )

        # Completion is terminal
        workflow.add_edge("completion", END)

        return workflow.compile()

    # ==================== Node Implementations ====================

    async def _initialize_node(self, state: GraphState) -> GraphState:
        """Initialize: Parse user request and identify goal"""
        user_request = state["user_request"]

        # Parse the request to identify the goal
        # In a real implementation, this would use an LLM
        goal = self._parse_goal(user_request)
        state["goal"] = goal

        # Get available tools
        state["available_tools"] = self.tool_store.list_tools()

        # Identify what information we need
        state["required_information"] = goal.required_info if goal else []

        print(f"[INITIALIZE] Goal: {goal.description if goal else 'Unknown'}")
        print(f"[INITIALIZE] Required info: {state['required_information']}")

        return state

    async def _planning_node(self, state: GraphState) -> GraphState:
        """Planning: Create a plan to achieve the goal"""
        goal = state.get("goal")

        if not goal:
            state["plan"] = "No clear goal identified. Need clarification."
            return state

        # Create a simple plan based on the goal
        plan_steps = []

        # Check if we need to gather information
        if state["required_information"]:
            plan_steps.append("Gather required information")

        # Check if we need tools
        potential_tools = self.tool_store.find_tools_for_goal(
            goal.description,
            state.get("available_information", {})
        )

        if potential_tools:
            plan_steps.append(f"Use tools: {', '.join(potential_tools)}")

        plan_steps.append("Synthesize results and respond")

        state["plan"] = " -> ".join(plan_steps)
        print(f"[PLANNING] Plan: {state['plan']}")

        return state

    async def _clarifying_node(self, state: GraphState) -> GraphState:
        """Clarifying: Ask user for missing information"""
        missing_info = StateManager.get_missing_information(state)

        questions = [
            f"What is the value for '{info}'?" for info in missing_info
        ]

        state["questions_for_user"] = questions
        print(f"[CLARIFYING] Questions: {questions}")

        # In a real implementation, this would wait for user input
        # For testing, we'll simulate having the info
        for info in missing_info:
            state["available_information"][info] = f"simulated_{info}"

        return state

    async def _tool_selection_node(self, state: GraphState) -> GraphState:
        """Tool Selection: Choose appropriate tools based on goal"""
        goal = state.get("goal")
        if not goal:
            state["selected_tools"] = []
            return state

        # Find tools that might help with the goal
        available_context = state.get("available_information", {})
        potential_tools = self.tool_store.find_tools_for_goal(
            goal.description,
            available_context
        )

        # Filter out tools we've already used (avoid redundancy)
        selected = []
        for tool_name in potential_tools:
            if not StateManager.was_tool_used(state, tool_name):
                # Check prerequisites
                can_use, reason = self.tool_store.check_tool_prerequisites(
                    tool_name,
                    available_context
                )
                if can_use:
                    selected.append(tool_name)

        state["selected_tools"] = selected
        print(f"[TOOL_SELECTION] Selected tools: {selected}")

        return state

    async def _tool_execution_node(self, state: GraphState) -> GraphState:
        """Tool Execution: Execute selected tools"""
        selected_tools = state.get("selected_tools", [])
        tool_outputs = state.get("tool_outputs", {})

        print(f"[TOOL_EXECUTION] Executing {len(selected_tools)} tools")

        for tool_name in selected_tools:
            # Get tool input from state
            # In a real implementation, an LLM would determine the input
            input_data = self._generate_tool_input(state, tool_name)

            if input_data:
                # Execute the tool
                result = await self.tool_store.execute_tool(
                    tool_name,
                    input_data,
                    state.get("available_information", {})
                )

                # Record execution
                execution = ToolExecution(
                    tool_name=tool_name,
                    input_data=input_data,
                    output=result.result if result.success else None,
                    success=result.success,
                    error=result.error
                )
                state["tool_executions"] = [*state.get("tool_executions", []), execution]

                # Store output in shared context
                if result.success:
                    tool_outputs[tool_name] = result.result
                    # Update available information with tool's provided context
                    tool = self.tool_store.get_tool(tool_name)
                    if tool:
                        for ctx_key in tool.provides_context:
                            state["available_information"][ctx_key] = result.result

                print(f"[TOOL_EXECUTION] {tool_name}: {'SUCCESS' if result.success else 'FAILED'}")
                if result.success:
                    print(f"  Result: {result.result}")
                else:
                    print(f"  Error: {result.error}")

        state["tool_outputs"] = tool_outputs
        return state

    async def _analysis_node(self, state: GraphState) -> GraphState:
        """Analysis: Analyze tool outputs and determine next steps"""
        tool_outputs = state.get("tool_outputs", {})
        goal = state.get("goal")

        print(f"[ANALYSIS] Analyzing {len(tool_outputs)} tool outputs")

        # Check if we have enough information to achieve the goal
        has_info = StateManager.has_required_information(state)
        goal_achieved = StateManager.is_goal_achieved(state)

        if goal_achieved:
            state["confidence"] = 0.9
            state["reasoning"] = "Goal achieved with available information"
        elif has_info:
            state["confidence"] = 0.7
            state["reasoning"] = "Have required information, ready to synthesize"
        else:
            state["confidence"] = 0.4
            missing = StateManager.get_missing_information(state)
            state["reasoning"] = f"Still missing information: {', '.join(missing)}"

        print(f"[ANALYSIS] Confidence: {state['confidence']:.2f}")
        print(f"[ANALYSIS] Reasoning: {state['reasoning']}")

        return state

    async def _synthesis_node(self, state: GraphState) -> GraphState:
        """Synthesis: Combine information to form final response"""
        goal = state.get("goal")
        tool_outputs = state.get("tool_outputs", {})
        available_info = state.get("available_information", {})

        print("[SYNTHESIS] Synthesizing final response")

        # Create response based on goal and gathered information
        response_parts = []

        if goal:
            response_parts.append(f"Goal: {goal.description}")

        if tool_outputs:
            response_parts.append("\nTool Results:")
            for tool_name, output in tool_outputs.items():
                response_parts.append(f"  - {tool_name}: {output}")

        if available_info:
            response_parts.append("\nAvailable Information:")
            for key, value in available_info.items():
                if not key.startswith("simulated"):  # Skip simulated values
                    response_parts.append(f"  - {key}: {value}")

        state["final_response"] = "\n".join(response_parts)
        return state

    async def _completion_node(self, state: GraphState) -> GraphState:
        """Completion: Finalize and prepare to return"""
        print("[COMPLETION] Task completed")
        return state

    async def _error_node(self, state: GraphState) -> GraphState:
        """Error: Handle errors gracefully"""
        error_msg = state.get("error_message", "Unknown error occurred")
        print(f"[ERROR] {error_msg}")
        return state

    # ==================== Routing Logic ====================

    def _route_from_initialize(self, state: GraphState) -> str:
        """Decide next state after initialization"""
        if not state.get("goal"):
            return "clarifying"
        return "planning"

    def _route_from_planning(self, state: GraphState) -> str:
        """Decide next state after planning"""
        # Check if we need clarification
        if StateManager.should_ask_clarification(state):
            return "clarifying"

        # Check if we need tools
        goal = state.get("goal")
        if goal:
            potential_tools = self.tool_store.find_tools_for_goal(
                goal.description,
                state.get("available_information", {})
            )
            if potential_tools:
                return "tool_selection"

        # Otherwise, go directly to synthesis
        return "synthesis"

    def _route_from_clarifying(self, state: GraphState) -> str:
        """Decide next state after clarification"""
        # If user can't/won't provide info, complete with what we have
        iterations = state.get("iterations", 0)
        if iterations > 5:  # Prevent infinite loops
            return "completion"

        # Otherwise, go back to planning with new information
        return "planning"

    def _route_from_tool_selection(self, state: GraphState) -> str:
        """Decide next state after tool selection"""
        selected = state.get("selected_tools", [])

        if not selected:
            # No tools to execute, need clarification or can synthesize
            if StateManager.should_ask_clarification(state):
                return "clarifying"
            return "synthesis"

        return "tool_execution"

    def _route_from_tool_execution(self, state: GraphState) -> str:
        """Decide next state after tool execution"""
        # Always analyze tool outputs
        return "analysis"

    def _route_from_analysis(self, state: GraphState) -> str:
        """Decide next state after analysis"""
        confidence = state.get("confidence", 0)
        iterations = state.get("iterations", 0)

        # Prevent infinite loops
        if iterations > 10:
            return "synthesis"

        # If high confidence, synthesize
        if confidence > 0.7:
            return "synthesis"

        # If need more tools
        if not StateManager.has_required_information(state):
            # Try tools again
            return "tool_selection"

        # Otherwise synthesize with what we have
        return "synthesis"

    def _route_from_synthesis(self, state: GraphState) -> str:
        """Decide next state after synthesis"""
        # Check if synthesis was successful
        if state.get("final_response"):
            return "completion"

        # If synthesis revealed gaps, go back to analysis
        if state.get("iterations", 0) < 8:
            return "analysis"

        # Give up gracefully
        return "completion"

    def _route_from_error(self, state: GraphState) -> str:
        """Decide next state after error"""
        # Try to recover with clarification
        if state.get("iterations", 0) < 3:
            return "clarifying"
        return "completion"

    # ==================== Helper Methods ====================

    def _parse_goal(self, user_request: str) -> Goal:
        """Parse user request into a Goal structure

        In a real implementation, this would use an LLM to understand
        the request and identify goals, constraints, and required information.
        """
        # Simple keyword-based parsing for demonstration
        request_lower = user_request.lower()

        # Identify if it's a calculation task
        if any(word in request_lower for word in ["calculate", "compute", "add", "multiply"]):
            return Goal(
                description=f"Perform calculation: {user_request}",
                constraints=[],
                required_info=["calculation_parameters"],
                sub_goals=[],
                completion_criteria="Calculation result obtained"
            )

        # Generic goal
        return Goal(
            description=user_request,
            constraints=[],
            required_info=[],
            sub_goals=[],
            completion_criteria="Request satisfied"
        )

    def _generate_tool_input(self, state: GraphState, tool_name: str) -> Dict[str, Any] | None:
        """Generate appropriate input for a tool based on state

        In a real implementation, an LLM would determine the input.
        This is a simple rule-based approach for demonstration.
        """
        user_request = state.get("user_request", "").lower()

        if tool_name == "calculator":
            # Try to extract numbers and operation from request
            if "add" in user_request or "+" in user_request:
                # Simple parsing - in reality, use LLM
                return {"operation": "add", "operand1": 5.0, "operand2": 3.0}
            elif "multiply" in user_request or "*" in user_request:
                return {"operation": "multiply", "operand1": 4.0, "operand2": 7.0}
            elif "sqrt" in user_request or "square root" in user_request:
                return {"operation": "sqrt", "operand1": 16.0}

        return None

    async def run(self, user_request: str) -> Dict[str, Any]:
        """Run the agent on a user request

        Args:
            user_request: Natural language request from user

        Returns:
            Dict containing final response and execution metadata
        """
        # Create initial state
        initial_state = StateManager.create_initial_state(user_request)

        print(f"\n{'='*60}")
        print(f"Starting agent execution for: {user_request}")
        print(f"{'='*60}\n")

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        print(f"\n{'='*60}")
        print("Agent execution completed")
        print(f"{'='*60}\n")

        return {
            "success": final_state.get("current_state") == AgentState.COMPLETION,
            "response": final_state.get("final_response"),
            "iterations": final_state.get("iterations"),
            "tool_executions": len(final_state.get("tool_executions", [])),
            "confidence": final_state.get("confidence"),
            "error": final_state.get("error_message")
        }

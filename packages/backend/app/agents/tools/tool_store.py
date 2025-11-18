"""Tool Store - Central registry for agent tools"""
from typing import Dict, List, Optional, Type, Any
from collections import defaultdict

from .base import BaseTool, ToolCategory, ToolOutput


class ToolStore:
    """Central registry and manager for agent tools

    The tool store acts as a "toolbox" that agents can query to:
    - Discover available tools
    - Find tools by category or capability
    - Check tool prerequisites against current state
    - Execute tools with proper tracking

    This implements the "tool awareness" concept where the agent knows
    what tools are available and what they can do.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tools_by_category: Dict[ToolCategory, List[str]] = defaultdict(list)
        self._execution_history: List[Dict[str, Any]] = []

    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool in the store

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        self._tools_by_category[tool.category].append(tool.name)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        requires_context: Optional[List[str]] = None
    ) -> List[str]:
        """List available tools, optionally filtered

        Args:
            category: Filter by tool category
            requires_context: Filter to tools that require specific context keys

        Returns:
            List of tool names
        """
        if category:
            tool_names = self._tools_by_category.get(category, [])
        else:
            tool_names = list(self._tools.keys())

        if requires_context:
            # Filter to tools that require at least one of the specified context keys
            tool_names = [
                name for name in tool_names
                if any(ctx in self._tools[name].required_context for ctx in requires_context)
            ]

        return tool_names

    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Get all tools in a specific category"""
        return [self._tools[name] for name in self._tools_by_category.get(category, [])]

    def find_tools_for_goal(
        self, goal_description: str, available_context: Dict[str, Any]
    ) -> List[str]:
        """Find tools that might be useful for achieving a goal

        This is a simple implementation that could be enhanced with embeddings
        or LLM-based tool selection.

        Args:
            goal_description: Natural language description of the goal
            available_context: Current state context

        Returns:
            List of potentially useful tool names
        """
        # Simple keyword matching for now
        goal_lower = goal_description.lower()
        useful_tools = []

        for name, tool in self._tools.items():
            # Check if tool can execute with current context
            can_execute, _ = tool.can_execute(available_context)
            if not can_execute:
                continue

            # Check if tool description matches goal keywords
            desc_lower = tool.description.lower()
            if any(word in desc_lower for word in goal_lower.split()):
                useful_tools.append(name)

        return useful_tools

    def check_tool_prerequisites(
        self, tool_name: str, state_context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Check if a tool's prerequisites are met

        Args:
            tool_name: Name of the tool to check
            state_context: Current state context

        Returns:
            Tuple of (can_execute: bool, reason: Optional[str])
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False, f"Tool '{tool_name}' not found"

        return tool.can_execute(state_context)

    async def execute_tool(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ToolOutput:
        """Execute a tool with tracking and history

        Args:
            tool_name: Name of the tool to execute
            input_data: Input parameters for the tool
            context: Current state context

        Returns:
            ToolOutput with results and metadata
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found in store"
            )

        # Check prerequisites
        can_execute, reason = tool.can_execute(context)
        if not can_execute:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Tool prerequisites not met: {reason}"
            )

        # Validate and execute
        try:
            validated_input = tool.validate_input(input_data)
            result = await tool._execute_with_tracking(validated_input, context)

            # Record execution in history
            self._execution_history.append({
                "tool_name": tool_name,
                "input": input_data,
                "success": result.success,
                "error": result.error,
                "metadata": result.metadata
            })

            return result
        except Exception as e:
            error_result = ToolOutput(
                success=False,
                result=None,
                error=f"Tool execution failed: {str(e)}"
            )
            self._execution_history.append({
                "tool_name": tool_name,
                "input": input_data,
                "success": False,
                "error": str(e),
                "metadata": {}
            })
            return error_result

    def get_execution_history(self, tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution history, optionally filtered by tool name"""
        if tool_name:
            return [h for h in self._execution_history if h["tool_name"] == tool_name]
        return self._execution_history.copy()

    def get_tool_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Get a catalog of all tools with their metadata

        This is useful for agents to understand what tools are available
        and what they can do.
        """
        catalog = {}
        for name, tool in self._tools.items():
            catalog[name] = {
                "name": name,
                "description": tool.description,
                "category": tool.category,
                "required_context": tool.required_context,
                "provides_context": tool.provides_context,
                "usage_stats": tool.get_usage_stats(),
                "input_schema": tool.input_schema.model_json_schema()
            }
        return catalog

    def clear_history(self) -> None:
        """Clear execution history"""
        self._execution_history.clear()

    def reset(self) -> None:
        """Reset the tool store (for testing)"""
        self._tools.clear()
        self._tools_by_category.clear()
        self._execution_history.clear()


# Global tool store instance
_global_tool_store: Optional[ToolStore] = None


def get_tool_store() -> ToolStore:
    """Get the global tool store instance"""
    global _global_tool_store
    if _global_tool_store is None:
        _global_tool_store = ToolStore()
        _initialize_default_tools()
    return _global_tool_store


def _initialize_default_tools() -> None:
    """Initialize the tool store with default tools"""
    from .calculator import CalculatorTool

    store = _global_tool_store
    if store:
        # Register default tools
        store.register_tool(CalculatorTool())

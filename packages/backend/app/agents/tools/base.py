"""Base tool interface for agent tools"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ToolCategory(str, Enum):
    """Categories of tools available to agents"""
    COMPUTATION = "computation"
    DATA_RETRIEVAL = "data_retrieval"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    UTILITY = "utility"


class ToolInput(BaseModel):
    """Base model for tool inputs with validation"""
    pass


class ToolOutput(BaseModel):
    """Standardized tool output format"""
    success: bool = Field(description="Whether the tool execution was successful")
    result: Any = Field(description="The actual result data from the tool")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the execution (e.g., execution time, tokens used)"
    )


class BaseTool(ABC):
    """Base class for all agent tools

    Tools are discrete capabilities that agents can invoke to accomplish tasks.
    Each tool has:
    - A unique name and description
    - Input/output schemas
    - Required parameters and constraints
    - Execution logic
    """

    def __init__(self):
        self._execution_count = 0
        self._last_execution_time: Optional[float] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does"""
        pass

    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        """Category this tool belongs to"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> type[ToolInput]:
        """Pydantic model describing the expected input"""
        pass

    @property
    def required_context(self) -> List[str]:
        """List of context keys this tool needs from state

        This allows the agent to check if required information is available
        before attempting to use the tool.
        """
        return []

    @property
    def provides_context(self) -> List[str]:
        """List of context keys this tool adds to state

        This allows the agent to understand what information becomes available
        after using this tool.
        """
        return []

    @abstractmethod
    async def execute(self, input_data: ToolInput, context: Dict[str, Any]) -> ToolOutput:
        """Execute the tool with given input and context

        Args:
            input_data: Validated input parameters
            context: Additional context from the agent state

        Returns:
            ToolOutput with success status, result, and metadata
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> ToolInput:
        """Validate and parse input data against the schema"""
        return self.input_schema(**input_data)

    def can_execute(self, state_context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check if this tool can execute given the current state context

        Returns:
            Tuple of (can_execute: bool, reason: Optional[str])
        """
        missing = [key for key in self.required_context if key not in state_context]
        if missing:
            return False, f"Missing required context: {', '.join(missing)}"
        return True, None

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for this tool"""
        return {
            "execution_count": self._execution_count,
            "last_execution_time": self._last_execution_time,
        }

    async def _execute_with_tracking(
        self, input_data: ToolInput, context: Dict[str, Any]
    ) -> ToolOutput:
        """Internal method that wraps execute with tracking"""
        import time
        start_time = time.time()

        try:
            result = await self.execute(input_data, context)
            execution_time = time.time() - start_time

            self._execution_count += 1
            self._last_execution_time = execution_time

            # Add execution metadata
            result.metadata.update({
                "execution_time": execution_time,
                "execution_count": self._execution_count,
                "tool_name": self.name,
            })

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolOutput(
                success=False,
                result=None,
                error=f"Tool execution failed: {str(e)}",
                metadata={
                    "execution_time": execution_time,
                    "tool_name": self.name,
                    "error_type": type(e).__name__,
                }
            )

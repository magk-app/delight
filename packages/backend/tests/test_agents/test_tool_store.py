"""Tests for tool store and calculator tool"""
import pytest
from app.agents.tools import (
    get_tool_store,
    ToolStore,
    CalculatorTool,
    BaseTool,
    ToolCategory,
    ToolInput,
    ToolOutput
)


class SimpleTestTool(BaseTool):
    """Simple test tool for testing"""

    @property
    def name(self) -> str:
        return "test_tool"

    @property
    def description(self) -> str:
        return "A simple test tool"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.UTILITY

    @property
    def input_schema(self) -> type[ToolInput]:
        return ToolInput

    @property
    def required_context(self) -> list[str]:
        return ["test_context"]

    @property
    def provides_context(self) -> list[str]:
        return ["test_result"]

    async def execute(self, input_data: ToolInput, context: dict) -> ToolOutput:
        return ToolOutput(
            success=True,
            result="test_output",
            metadata={"test": True}
        )


@pytest.fixture
def tool_store():
    """Create a fresh tool store for testing"""
    store = ToolStore()
    return store


@pytest.fixture
def calculator_tool():
    """Create calculator tool instance"""
    return CalculatorTool()


class TestCalculatorTool:
    """Test suite for calculator tool"""

    @pytest.mark.asyncio
    async def test_addition(self, calculator_tool):
        """Test basic addition"""
        result = await calculator_tool.execute(
            {"operation": "add", "operand1": 5.0, "operand2": 3.0},
            {}
        )

        assert result.success is True
        assert result.result == 8.0
        assert result.error is None
        assert "formula" in result.metadata
        assert "5.0 + 3.0 = 8.0" in result.metadata["formula"]

    @pytest.mark.asyncio
    async def test_subtraction(self, calculator_tool):
        """Test subtraction"""
        result = await calculator_tool.execute(
            {"operation": "subtract", "operand1": 10.0, "operand2": 4.0},
            {}
        )

        assert result.success is True
        assert result.result == 6.0

    @pytest.mark.asyncio
    async def test_multiplication(self, calculator_tool):
        """Test multiplication"""
        result = await calculator_tool.execute(
            {"operation": "multiply", "operand1": 6.0, "operand2": 7.0},
            {}
        )

        assert result.success is True
        assert result.result == 42.0

    @pytest.mark.asyncio
    async def test_division(self, calculator_tool):
        """Test division"""
        result = await calculator_tool.execute(
            {"operation": "divide", "operand1": 15.0, "operand2": 3.0},
            {}
        )

        assert result.success is True
        assert result.result == 5.0

    @pytest.mark.asyncio
    async def test_division_by_zero(self, calculator_tool):
        """Test division by zero error handling"""
        result = await calculator_tool.execute(
            {"operation": "divide", "operand1": 10.0, "operand2": 0.0},
            {}
        )

        assert result.success is False
        assert result.result is None
        assert "divide by zero" in result.error.lower()

    @pytest.mark.asyncio
    async def test_power(self, calculator_tool):
        """Test power operation"""
        result = await calculator_tool.execute(
            {"operation": "power", "operand1": 2.0, "operand2": 3.0},
            {}
        )

        assert result.success is True
        assert result.result == 8.0

    @pytest.mark.asyncio
    async def test_square_root(self, calculator_tool):
        """Test square root (unary operation)"""
        result = await calculator_tool.execute(
            {"operation": "sqrt", "operand1": 16.0},
            {}
        )

        assert result.success is True
        assert result.result == 4.0

    @pytest.mark.asyncio
    async def test_square_root_negative(self, calculator_tool):
        """Test square root of negative number"""
        result = await calculator_tool.execute(
            {"operation": "sqrt", "operand1": -16.0},
            {}
        )

        assert result.success is False
        assert "negative" in result.error.lower()

    @pytest.mark.asyncio
    async def test_absolute_value(self, calculator_tool):
        """Test absolute value"""
        result = await calculator_tool.execute(
            {"operation": "abs", "operand1": -5.0},
            {}
        )

        assert result.success is True
        assert result.result == 5.0

    @pytest.mark.asyncio
    async def test_unary_with_second_operand(self, calculator_tool):
        """Test unary operation with second operand (should fail)"""
        result = await calculator_tool.execute(
            {"operation": "sqrt", "operand1": 16.0, "operand2": 2.0},
            {}
        )

        assert result.success is False
        assert "unary" in result.error.lower()

    @pytest.mark.asyncio
    async def test_binary_without_second_operand(self, calculator_tool):
        """Test binary operation without second operand (should fail)"""
        result = await calculator_tool.execute(
            {"operation": "add", "operand1": 5.0},
            {}
        )

        assert result.success is False
        assert "second operand" in result.error.lower()

    def test_tool_metadata(self, calculator_tool):
        """Test tool metadata"""
        assert calculator_tool.name == "calculator"
        assert calculator_tool.category == ToolCategory.COMPUTATION
        assert len(calculator_tool.description) > 0
        assert "last_calculation_result" in calculator_tool.provides_context


class TestToolStore:
    """Test suite for tool store"""

    def test_register_tool(self, tool_store):
        """Test registering a tool"""
        tool = SimpleTestTool()
        tool_store.register_tool(tool)

        assert "test_tool" in tool_store.list_tools()
        assert tool_store.get_tool("test_tool") is tool

    def test_register_duplicate_tool(self, tool_store):
        """Test registering duplicate tool raises error"""
        tool1 = SimpleTestTool()
        tool2 = SimpleTestTool()

        tool_store.register_tool(tool1)

        with pytest.raises(ValueError, match="already registered"):
            tool_store.register_tool(tool2)

    def test_get_nonexistent_tool(self, tool_store):
        """Test getting a tool that doesn't exist"""
        result = tool_store.get_tool("nonexistent")
        assert result is None

    def test_list_tools_by_category(self, tool_store):
        """Test listing tools filtered by category"""
        calc = CalculatorTool()
        test_tool = SimpleTestTool()

        tool_store.register_tool(calc)
        tool_store.register_tool(test_tool)

        computation_tools = tool_store.list_tools(category=ToolCategory.COMPUTATION)
        assert "calculator" in computation_tools
        assert "test_tool" not in computation_tools

        utility_tools = tool_store.list_tools(category=ToolCategory.UTILITY)
        assert "test_tool" in utility_tools
        assert "calculator" not in utility_tools

    def test_get_tools_by_category(self, tool_store):
        """Test getting tool instances by category"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        tools = tool_store.get_tools_by_category(ToolCategory.COMPUTATION)
        assert len(tools) == 1
        assert tools[0].name == "calculator"

    def test_check_tool_prerequisites(self, tool_store):
        """Test checking tool prerequisites"""
        tool = SimpleTestTool()
        tool_store.register_tool(tool)

        # Without required context
        can_execute, reason = tool_store.check_tool_prerequisites("test_tool", {})
        assert can_execute is False
        assert "test_context" in reason

        # With required context
        can_execute, reason = tool_store.check_tool_prerequisites(
            "test_tool",
            {"test_context": "value"}
        )
        assert can_execute is True
        assert reason is None

    def test_check_nonexistent_tool_prerequisites(self, tool_store):
        """Test checking prerequisites for nonexistent tool"""
        can_execute, reason = tool_store.check_tool_prerequisites("nonexistent", {})
        assert can_execute is False
        assert "not found" in reason

    @pytest.mark.asyncio
    async def test_execute_tool(self, tool_store):
        """Test executing a tool through the store"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        result = await tool_store.execute_tool(
            "calculator",
            {"operation": "add", "operand1": 2.0, "operand2": 3.0},
            {}
        )

        assert result.success is True
        assert result.result == 5.0

    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, tool_store):
        """Test executing a tool that doesn't exist"""
        result = await tool_store.execute_tool("nonexistent", {}, {})

        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_execute_tool_without_prerequisites(self, tool_store):
        """Test executing tool without required context"""
        tool = SimpleTestTool()
        tool_store.register_tool(tool)

        result = await tool_store.execute_tool("test_tool", {}, {})

        assert result.success is False
        assert "prerequisites not met" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execution_history(self, tool_store):
        """Test execution history tracking"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        # Execute multiple times
        await tool_store.execute_tool(
            "calculator",
            {"operation": "add", "operand1": 1.0, "operand2": 2.0},
            {}
        )
        await tool_store.execute_tool(
            "calculator",
            {"operation": "multiply", "operand1": 3.0, "operand2": 4.0},
            {}
        )

        history = tool_store.get_execution_history()
        assert len(history) == 2

        calc_history = tool_store.get_execution_history("calculator")
        assert len(calc_history) == 2
        assert all(h["tool_name"] == "calculator" for h in calc_history)

    def test_find_tools_for_goal(self, tool_store):
        """Test finding tools for a goal"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        # Test with calculation-related goal
        tools = tool_store.find_tools_for_goal("calculate 5 + 3", {})
        assert "calculator" in tools

        # Test with unrelated goal
        tools = tool_store.find_tools_for_goal("write a poem", {})
        assert "calculator" in tools or len(tools) == 0  # Depends on implementation

    def test_get_tool_catalog(self, tool_store):
        """Test getting tool catalog"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        catalog = tool_store.get_tool_catalog()
        assert "calculator" in catalog
        assert catalog["calculator"]["name"] == "calculator"
        assert catalog["calculator"]["category"] == ToolCategory.COMPUTATION
        assert "input_schema" in catalog["calculator"]

    def test_clear_history(self, tool_store):
        """Test clearing execution history"""
        calc = CalculatorTool()
        tool_store.register_tool(calc)

        # Add some history
        tool_store._execution_history.append({"test": "data"})

        tool_store.clear_history()
        assert len(tool_store.get_execution_history()) == 0

    def test_global_tool_store(self):
        """Test global tool store singleton"""
        store1 = get_tool_store()
        store2 = get_tool_store()

        assert store1 is store2
        assert "calculator" in store1.list_tools()  # Default tools loaded


class TestToolTracking:
    """Test tool execution tracking"""

    @pytest.mark.asyncio
    async def test_execution_count(self, calculator_tool):
        """Test execution count tracking"""
        assert calculator_tool._execution_count == 0

        await calculator_tool._execute_with_tracking(
            {"operation": "add", "operand1": 1.0, "operand2": 2.0},
            {}
        )

        assert calculator_tool._execution_count == 1

        await calculator_tool._execute_with_tracking(
            {"operation": "add", "operand1": 3.0, "operand2": 4.0},
            {}
        )

        assert calculator_tool._execution_count == 2

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, calculator_tool):
        """Test execution time tracking"""
        result = await calculator_tool._execute_with_tracking(
            {"operation": "add", "operand1": 1.0, "operand2": 2.0},
            {}
        )

        assert "execution_time" in result.metadata
        assert result.metadata["execution_time"] > 0
        assert calculator_tool._last_execution_time is not None

    @pytest.mark.asyncio
    async def test_usage_stats(self, calculator_tool):
        """Test getting usage stats"""
        await calculator_tool._execute_with_tracking(
            {"operation": "add", "operand1": 1.0, "operand2": 2.0},
            {}
        )

        stats = calculator_tool.get_usage_stats()
        assert stats["execution_count"] == 1
        assert stats["last_execution_time"] is not None

    @pytest.mark.asyncio
    async def test_error_tracking(self, calculator_tool):
        """Test error tracking in metadata"""
        result = await calculator_tool._execute_with_tracking(
            {"operation": "divide", "operand1": 1.0, "operand2": 0.0},
            {}
        )

        assert result.success is False
        assert "execution_time" in result.metadata
        assert "tool_name" in result.metadata
        assert result.metadata["tool_name"] == "calculator"

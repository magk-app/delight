"""Calculator tool - simple example tool for mathematical operations"""
from typing import Any, Dict, Literal
from pydantic import Field
import operator
import math

from .base import BaseTool, ToolInput, ToolOutput, ToolCategory


class CalculatorInput(ToolInput):
    """Input schema for calculator operations"""
    operation: Literal["add", "subtract", "multiply", "divide", "power", "sqrt", "abs"] = Field(
        description="Mathematical operation to perform"
    )
    operand1: float = Field(description="First operand")
    operand2: float | None = Field(
        default=None,
        description="Second operand (not required for unary operations like sqrt, abs)"
    )


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic mathematical operations

    This serves as an example of a tool that:
    - Performs deterministic computations
    - Has clear input/output contracts
    - Handles edge cases (division by zero)
    - Provides useful error messages
    """

    OPERATIONS = {
        "add": operator.add,
        "subtract": operator.sub,
        "multiply": operator.mul,
        "divide": operator.truediv,
        "power": operator.pow,
        "sqrt": lambda x, _: math.sqrt(x),
        "abs": lambda x, _: abs(x),
    }

    UNARY_OPS = {"sqrt", "abs"}

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Performs basic mathematical operations (add, subtract, multiply, divide, "
            "power, sqrt, abs). Use this when you need to compute numerical results."
        )

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.COMPUTATION

    @property
    def input_schema(self) -> type[ToolInput]:
        return CalculatorInput

    @property
    def provides_context(self) -> list[str]:
        return ["last_calculation_result"]

    async def execute(self, input_data: ToolInput, context: Dict[str, Any]) -> ToolOutput:
        """Execute the calculation"""
        calc_input = input_data if isinstance(input_data, CalculatorInput) else CalculatorInput(**input_data)

        operation = calc_input.operation
        operand1 = calc_input.operand1
        operand2 = calc_input.operand2

        # Validate unary operations
        if operation in self.UNARY_OPS:
            if operand2 is not None:
                return ToolOutput(
                    success=False,
                    result=None,
                    error=f"Operation '{operation}' is unary and doesn't accept a second operand"
                )
        else:
            # Binary operations require operand2
            if operand2 is None:
                return ToolOutput(
                    success=False,
                    result=None,
                    error=f"Operation '{operation}' requires a second operand"
                )

        # Validate division by zero
        if operation == "divide" and operand2 == 0:
            return ToolOutput(
                success=False,
                result=None,
                error="Cannot divide by zero"
            )

        # Validate sqrt of negative number
        if operation == "sqrt" and operand1 < 0:
            return ToolOutput(
                success=False,
                result=None,
                error="Cannot take square root of negative number"
            )

        # Perform the calculation
        try:
            op_func = self.OPERATIONS[operation]
            result = op_func(operand1, operand2)

            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "operation": operation,
                    "operands": [operand1] + ([operand2] if operand2 is not None else []),
                    "formula": self._format_formula(operation, operand1, operand2, result)
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=f"Calculation error: {str(e)}"
            )

    def _format_formula(
        self, operation: str, operand1: float, operand2: float | None, result: float
    ) -> str:
        """Format a human-readable formula string"""
        if operation == "add":
            return f"{operand1} + {operand2} = {result}"
        elif operation == "subtract":
            return f"{operand1} - {operand2} = {result}"
        elif operation == "multiply":
            return f"{operand1} × {operand2} = {result}"
        elif operation == "divide":
            return f"{operand1} ÷ {operand2} = {result}"
        elif operation == "power":
            return f"{operand1}^{operand2} = {result}"
        elif operation == "sqrt":
            return f"√{operand1} = {result}"
        elif operation == "abs":
            return f"|{operand1}| = {result}"
        return f"{operation}({operand1}) = {result}"

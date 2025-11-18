"""
Demo script for goal-driven agent with state transitions and tool awareness

This script demonstrates:
1. Simple calculation requests
2. State transition flow
3. Tool execution and tracking
4. Goal-driven decision making

Run from backend directory:
    poetry run python examples/goal_driven_agent_demo.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.graph import GoalDrivenAgent
from app.agents.tools import get_tool_store


async def demo_simple_calculation():
    """Demonstrate simple calculation request"""
    print("\n" + "=" * 70)
    print("DEMO 1: Simple Calculation")
    print("=" * 70)

    agent = await GoalDrivenAgent.create()
    result = await agent.run("calculate 5 + 3")

    print("\n📊 Result Summary:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tool Executions: {result['tool_executions']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"\n📝 Response:\n{result['response']}")


async def demo_multiplication():
    """Demonstrate multiplication request"""
    print("\n" + "=" * 70)
    print("DEMO 2: Multiplication")
    print("=" * 70)

    agent = await GoalDrivenAgent.create()
    result = await agent.run("multiply 7 by 6")

    print("\n📊 Result Summary:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tool Executions: {result['tool_executions']}")
    print(f"\n📝 Response:\n{result['response']}")


async def demo_square_root():
    """Demonstrate unary operation"""
    print("\n" + "=" * 70)
    print("DEMO 3: Square Root (Unary Operation)")
    print("=" * 70)

    agent = await GoalDrivenAgent.create()
    result = await agent.run("calculate square root of 16")

    print("\n📊 Result Summary:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Tool Executions: {result['tool_executions']}")
    print(f"\n📝 Response:\n{result['response']}")


async def demo_tool_store():
    """Demonstrate tool store features"""
    print("\n" + "=" * 70)
    print("DEMO 4: Tool Store Capabilities")
    print("=" * 70)

    tool_store = get_tool_store()

    # Show available tools
    print("\n🔧 Available Tools:")
    catalog = tool_store.get_tool_catalog()
    for name, info in catalog.items():
        print(f"\n  {name}:")
        print(f"    Description: {info['description'][:80]}...")
        print(f"    Category: {info['category']}")
        print(f"    Required Context: {info['required_context']}")
        print(f"    Provides Context: {info['provides_context']}")

    # Execute a calculation
    print("\n\n🧮 Executing Calculator Tool Directly:")
    result = await tool_store.execute_tool(
        "calculator",
        {"operation": "add", "operand1": 15.0, "operand2": 27.0},
        {}
    )

    print(f"  Success: {result.success}")
    print(f"  Result: {result.result}")
    print(f"  Formula: {result.metadata.get('formula', 'N/A')}")
    print(f"  Execution Time: {result.metadata.get('execution_time', 0):.4f}s")

    # Show execution history
    print("\n\n📜 Execution History:")
    history = tool_store.get_execution_history()
    for i, exec in enumerate(history[-5:], 1):  # Last 5
        print(f"\n  {i}. {exec['tool_name']}")
        print(f"     Success: {exec['success']}")
        if exec['success']:
            print(f"     Input: {exec['input']}")


async def demo_state_transitions():
    """Demonstrate state transition tracking"""
    print("\n" + "=" * 70)
    print("DEMO 5: State Transition Flow")
    print("=" * 70)

    from app.agents.state import StateManager, AgentState

    # Show valid transitions
    print("\n📋 Valid State Transitions:")
    for state in AgentState:
        next_states = StateManager.get_next_states(state)
        if next_states:
            print(f"\n  {state.value}:")
            for next_state in next_states:
                print(f"    → {next_state.value}")
        else:
            print(f"\n  {state.value}: [TERMINAL]")

    # Demonstrate a transition sequence
    print("\n\n🔄 Example Transition Sequence:")
    state = StateManager.create_initial_state("test request")
    print(f"  1. {state['current_state'].value} (initial)")

    # Transition to planning
    state = StateManager.transition_to(
        state,
        AgentState.PLANNING,
        "Identified clear goal"
    )
    print(f"  2. {state['current_state'].value} (from {state['previous_state'].value})")

    # Transition to tool selection
    state = StateManager.transition_to(
        state,
        AgentState.TOOL_SELECTION,
        "Need calculator tool"
    )
    print(f"  3. {state['current_state'].value} (from {state['previous_state'].value})")

    print(f"\n  Total iterations: {state['iterations']}")


async def demo_error_handling():
    """Demonstrate error handling"""
    print("\n" + "=" * 70)
    print("DEMO 6: Error Handling")
    print("=" * 70)

    tool_store = get_tool_store()

    # Division by zero
    print("\n❌ Testing Division by Zero:")
    result = await tool_store.execute_tool(
        "calculator",
        {"operation": "divide", "operand1": 10.0, "operand2": 0.0},
        {}
    )
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    # Negative square root
    print("\n❌ Testing Negative Square Root:")
    result = await tool_store.execute_tool(
        "calculator",
        {"operation": "sqrt", "operand1": -16.0},
        {}
    )
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")

    # Invalid operation
    print("\n❌ Testing Invalid Tool:")
    result = await tool_store.execute_tool(
        "nonexistent_tool",
        {},
        {}
    )
    print(f"  Success: {result.success}")
    print(f"  Error: {result.error}")


async def demo_goal_parsing():
    """Demonstrate goal parsing"""
    print("\n" + "=" * 70)
    print("DEMO 7: Goal Parsing")
    print("=" * 70)

    agent = await GoalDrivenAgent.create()

    test_requests = [
        "calculate 10 + 20",
        "multiply 5 by 4",
        "compute the square root of 25",
        "help me with something"
    ]

    print("\n🎯 Parsing Different Request Types:")
    for request in test_requests:
        goal = agent._parse_goal(request)
        print(f"\n  Request: '{request}'")
        print(f"  Goal: {goal.description}")
        print(f"  Required Info: {goal.required_info}")
        print(f"  Completion Criteria: {goal.completion_criteria}")


async def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("GOAL-DRIVEN AGENT DEMONSTRATION")
    print("Showcasing state transitions and tool-aware processing")
    print("=" * 70)

    try:
        # Run each demo
        await demo_simple_calculation()
        await demo_multiplication()
        await demo_square_root()
        await demo_tool_store()
        await demo_state_transitions()
        await demo_error_handling()
        await demo_goal_parsing()

        print("\n" + "=" * 70)
        print("✅ All demos completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

"""Eliza AI Companion Agent using LangGraph

This module implements the Eliza agent using LangGraph for visual debugging
and testing in LangGraph Studio. This agent will eventually be used in Story 2.3
to replace the simple agent from Story 2.5.

For now, this is a basic implementation to enable LangGraph Studio testing.
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Import settings for OpenAI API key
import os


class ElizaState(TypedDict):
    """State for the Eliza agent.

    Attributes:
        messages: Conversation history
        retrieved_memories: Memories retrieved from vector search
        emotional_state: Detected emotional state (future: Story 2.6)
        user_context: Additional user context
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    retrieved_memories: List[Dict[str, Any]]
    emotional_state: Dict[str, Any]
    user_context: Dict[str, Any]


class ElizaAgent:
    """Eliza AI Companion Agent built with LangGraph.

    This agent uses a state machine approach to:
    1. Recall context from memory
    2. Analyze emotional state
    3. Generate empathetic responses

    For Story 2.5: Basic implementation without memory service integration
    For Story 2.3: Full implementation with memory service, emotion detection
    """

    def __init__(self, memory_service=None, openai_api_key: str = None):
        """Initialize the Eliza agent.

        Args:
            memory_service: Memory service instance (optional for Studio testing)
            openai_api_key: OpenAI API key (defaults to env var)
        """
        self.memory_service = memory_service
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            streaming=True,
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine.

        Graph structure:
        START -> recall_context -> analyze_emotion -> generate_response -> END

        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(ElizaState)

        # Add nodes
        workflow.add_node("recall_context", self._recall_context)
        workflow.add_node("analyze_emotion", self._analyze_emotion)
        workflow.add_node("generate_response", self._generate_response)

        # Add edges
        workflow.set_entry_point("recall_context")
        workflow.add_edge("recall_context", "analyze_emotion")
        workflow.add_edge("analyze_emotion", "generate_response")
        workflow.add_edge("generate_response", END)

        # Compile
        return workflow.compile()

    def _recall_context(self, state: ElizaState) -> ElizaState:
        """Recall relevant memories from vector database.

        In Studio: This will be a no-op (empty memories)
        In Production: Queries memory service with last message

        Args:
            state: Current agent state

        Returns:
            Updated state with retrieved_memories
        """
        # For Studio testing: return empty memories
        # For Production (Story 2.3): query memory service
        if self.memory_service is None:
            state["retrieved_memories"] = []
        else:
            # TODO: Query memory service with last message
            # memories = await self.memory_service.query_memories(...)
            state["retrieved_memories"] = []

        return state

    def _analyze_emotion(self, state: ElizaState) -> ElizaState:
        """Analyze emotional state from messages.

        In Studio: Simple keyword detection
        In Production (Story 2.6): cardiffnlp/roberta emotion model

        Args:
            state: Current agent state

        Returns:
            Updated state with emotional_state
        """
        # Get last message
        if not state["messages"]:
            state["emotional_state"] = {"dominant": "neutral", "intensity": 0.0}
            return state

        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            content = last_message.content.lower()

            # Simple keyword-based emotion detection (MVP)
            if any(word in content for word in ["overwhelmed", "stressed", "anxious"]):
                state["emotional_state"] = {
                    "dominant": "fear",
                    "intensity": 0.7,
                    "triggers": ["stress", "overwhelm"]
                }
            elif any(word in content for word in ["happy", "excited", "great"]):
                state["emotional_state"] = {
                    "dominant": "joy",
                    "intensity": 0.6,
                    "triggers": ["positive_event"]
                }
            else:
                state["emotional_state"] = {
                    "dominant": "neutral",
                    "intensity": 0.3,
                    "triggers": []
                }

        return state

    def _generate_response(self, state: ElizaState) -> ElizaState:
        """Generate empathetic response using GPT-4o-mini.

        Builds context from:
        - System prompt (Eliza's personality)
        - Retrieved memories
        - Emotional state
        - Conversation history

        Args:
            state: Current agent state

        Returns:
            Updated state with AI response added to messages
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(
            state.get("retrieved_memories", []),
            state.get("emotional_state", {})
        )

        # Prepare messages for LLM
        messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

        # Generate response
        response = self.llm.invoke(messages)

        # Add response to state
        state["messages"].append(AIMessage(content=response.content))

        return state

    def _build_system_prompt(
        self,
        memories: List[Dict[str, Any]],
        emotional_state: Dict[str, Any]
    ) -> str:
        """Build system prompt with memory and emotion context.

        Args:
            memories: Retrieved memories
            emotional_state: Detected emotional state

        Returns:
            System prompt string
        """
        base_prompt = """You are Eliza, an emotionally intelligent AI companion.

You help users balance ambition with well-being. You:
- Listen empathetically to their struggles
- Remember past conversations and reference them
- Validate their feelings before offering suggestions
- Distinguish between controllable and uncontrollable stressors
- Suggest circuit breakers when they're overwhelmed
- Celebrate their wins and encourage momentum

Be warm, supportive, and contextual."""

        # Add memory context
        if memories:
            memory_context = "\n\nWhat you remember about this user:\n"
            for memory in memories:
                memory_context += f"- {memory.get('content', '')}\n"
            base_prompt += memory_context

        # Add emotional context
        if emotional_state and emotional_state.get("dominant") != "neutral":
            emotion = emotional_state.get("dominant", "unknown")
            intensity = emotional_state.get("intensity", 0.0)
            base_prompt += f"\n\nCurrent emotional state: {emotion} (intensity: {intensity:.2f})"

        return base_prompt

    async def generate_response_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        user_context: Dict[str, Any] = None
    ):
        """Generate streaming response (for SSE).

        This is used by the chat API for real-time streaming.

        Args:
            user_message: User's message
            conversation_history: Previous messages
            user_context: Additional context

        Yields:
            Response tokens
        """
        # Prepare state
        messages = []

        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=user_message))

        # Create initial state
        initial_state = ElizaState(
            messages=messages,
            retrieved_memories=[],
            emotional_state={},
            user_context=user_context or {}
        )

        # Run graph (non-streaming for now)
        # TODO: Implement streaming in Story 2.3
        final_state = self.graph.invoke(initial_state)

        # Return last message
        if final_state["messages"]:
            last_message = final_state["messages"][-1]
            if isinstance(last_message, AIMessage):
                # For now, yield entire response
                # Story 2.3 will add proper streaming
                yield last_message.content


# Export graph for LangGraph Studio
def get_graph():
    """Get compiled graph for LangGraph Studio.

    This function is used by langgraph.json to expose the graph
    for visual debugging in LangGraph Studio.

    Returns:
        Compiled StateGraph
    """
    agent = ElizaAgent(memory_service=None)
    return agent.graph


# Export as 'graph' for Studio
graph = get_graph()

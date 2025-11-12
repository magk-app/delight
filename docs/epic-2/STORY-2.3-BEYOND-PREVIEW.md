# Story 2.3 and Beyond - Preview & Implementation Guide

**Date:** 2025-11-12  
**Purpose:** Preview upcoming Epic 2 stories and provide implementation guidance

---

## Story 2.3: Build Eliza Agent with LangGraph

### Overview

Build a stateful LangGraph agent that orchestrates Eliza's conversations with memory-aware reasoning. This is the **core intelligence** of the companion system.

### Key Components

**LangGraph State Machine (5 Nodes):**

```
┌─────────────┐
│ receive_input │ → Parse message, detect emotion
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ recall_context │ → Query 3-tier memory (personal/project/task)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ reason │ → LLM processes with memory context (STREAMING)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ respond │ → Format response (already done in reason)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ store_memory │ → Save conversation to task memory
└─────────────┘
```

### Implementation Structure

```python
# backend/app/agents/eliza_agent.py

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.services.memory_service import MemoryService
from app.models.memory import MemoryType

class ElizaState(TypedDict):
    user_id: str
    messages: List[Dict[str, str]]  # Conversation history
    retrieved_memories: List[Dict[str, Any]]
    emotional_state: Dict[str, float]
    user_context: Dict[str, Any]
    response_text: str

class ElizaAgent:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            streaming=True  # Enable streaming
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(ElizaState)

        # Add nodes
        graph.add_node("receive_input", self._receive_input)
        graph.add_node("recall_context", self._recall_context)
        graph.add_node("reason", self._reason)
        graph.add_node("respond", self._respond)
        graph.add_node("store_memory", self._store_memory)

        # Define edges
        graph.set_entry_point("receive_input")
        graph.add_edge("receive_input", "recall_context")
        graph.add_edge("recall_context", "reason")
        graph.add_edge("reason", "respond")
        graph.add_edge("respond", "store_memory")
        graph.add_edge("store_memory", END)

        return graph.compile()

    async def _receive_input(self, state: ElizaState) -> ElizaState:
        """Parse user message and detect emotion."""
        # Extract last user message
        last_message = state["messages"][-1]["content"]

        # Detect emotion (Story 2.6 integration)
        # For now, placeholder
        state["emotional_state"] = {
            "dominant": "neutral",
            "scores": {},
            "intensity": 0.5
        }

        return state

    async def _recall_context(self, state: ElizaState) -> ElizaState:
        """Query relevant memories using MemoryService."""
        user_id = UUID(state["user_id"])
        query_text = state["messages"][-1]["content"]

        # Always query personal tier (top 5)
        personal_memories = await self.memory_service.query_memories(
            user_id=user_id,
            query_text=query_text,
            memory_types=[MemoryType.PERSONAL],
            limit=5
        )

        # Query project tier if goal-related keywords detected
        project_memories = []
        goal_keywords = ["goal", "goals", "plan", "plans", "objective", "target"]
        if any(keyword in query_text.lower() for keyword in goal_keywords):
            project_memories = await self.memory_service.query_memories(
                user_id=user_id,
                query_text=query_text,
                memory_types=[MemoryType.PROJECT],
                limit=5
            )

        # Query task tier for recent context (top 3)
        task_memories = await self.memory_service.query_memories(
            user_id=user_id,
            query_text=query_text,
            memory_types=[MemoryType.TASK],
            limit=3
        )

        # Combine memories
        state["retrieved_memories"] = [
            {"type": "personal", "content": m.content, "metadata": m.metadata}
            for m in personal_memories
        ] + [
            {"type": "project", "content": m.content, "metadata": m.metadata}
            for m in project_memories
        ] + [
            {"type": "task", "content": m.content, "metadata": m.metadata}
            for m in task_memories
        ]

        return state

    async def _reason(self, state: ElizaState) -> ElizaState:
        """LLM processes input with memory context (STREAMING)."""
        # Build memory context string
        memory_context = self._format_memories(state["retrieved_memories"])

        # Build system prompt with user context
        system_prompt = self._build_system_prompt(
            emotional_state=state["emotional_state"],
            user_context=state.get("user_context", {})
        )

        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Relevant Memories:\n{memory_context}"),
        ] + [
            HumanMessage(content=m["content"]) if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in state["messages"][-10:]  # Last 10 messages
        ]

        # Stream LLM response
        response_chunks = []
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                response_chunks.append(chunk.content)

        response_text = "".join(response_chunks)

        # Add AI response to state
        state["messages"].append({
            "role": "assistant",
            "content": response_text
        })
        state["response_text"] = response_text

        return state

    def _build_system_prompt(self, emotional_state: Dict, user_context: Dict) -> str:
        """Build Eliza's system prompt with emotional intelligence."""
        return f"""You are Eliza, an empathetic AI companion who helps users balance ambition with well-being.

Your core principles:
1. **Emotional Intelligence**: Acknowledge feelings, validate experiences, offer support
2. **Control Triage**: Distinguish controllable vs uncontrollable stressors
3. **Energy-Based Push**: Validate before pushing, respect user's energy level
4. **Circuit Breaker**: When user is overwhelmed, prioritize well-being over productivity

Current User Context:
- Emotional State: {emotional_state.get('dominant', 'neutral')} (intensity: {emotional_state.get('intensity', 0.5)})
- User Values: {user_context.get('value_weights', {})}

Response Guidelines:
- Be warm, empathetic, and conversational
- Reference past conversations when relevant
- Ask clarifying questions when user is vague
- Offer grounding suggestions when user seems overwhelmed
- Celebrate wins and encourage momentum
- Balance productivity coaching with well-being support

Remember: You're not just a productivity coach—you're a companion who understands the human experience."""

    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for LLM context."""
        formatted = []
        for mem in memories:
            formatted.append(f"[{mem['type'].upper()}] {mem['content']}")
            if mem.get('metadata', {}).get('stressor'):
                formatted.append(f"  → Stressor: {mem['metadata'].get('category', 'general')}")
        return "\n".join(formatted)

    async def _respond(self, state: ElizaState) -> ElizaState:
        """Format response (already done in reason, but can add post-processing)."""
        # Response already formatted in reason node
        return state

    async def _store_memory(self, state: ElizaState) -> ElizaState:
        """Save conversation exchange to task memory."""
        user_id = UUID(state["user_id"])

        # Extract last exchange (user + AI)
        last_user_msg = state["messages"][-2]["content"]  # Second to last
        last_ai_msg = state["messages"][-1]["content"]  # Last

        exchange_content = f"User: {last_user_msg}\nEliza: {last_ai_msg}"

        # Store as task memory
        await self.memory_service.add_memory(
            user_id=user_id,
            memory_type=MemoryType.TASK,
            content=exchange_content,
            metadata={
                "conversation_id": state.get("conversation_id"),
                "emotional_state": state["emotional_state"],
                "exchange_type": "conversation"
            }
        )

        return state

    async def chat(self, user_id: str, message: str, conversation_id: str = None) -> str:
        """Main entry point for chat."""
        # Initialize state
        initial_state: ElizaState = {
            "user_id": user_id,
            "messages": [{"role": "user", "content": message}],
            "retrieved_memories": [],
            "emotional_state": {},
            "user_context": {},
            "response_text": "",
            "conversation_id": conversation_id
        }

        # Run graph
        final_state = await self.graph.ainvoke(initial_state)

        return final_state["response_text"]
```

### Key Features

1. **Memory-Aware Reasoning**: Uses MemoryService to retrieve relevant context
2. **Strategic Tier Querying**: Always queries personal, conditionally queries project/task
3. **Emotional Intelligence**: System prompt includes emotional state and user context
4. **Streaming Support**: LLM streams tokens (for Story 2.4 integration)
5. **State Management**: Maintains conversation history across messages

---

## Story 2.4: Create Companion Chat API with SSE Streaming

### Overview

Build FastAPI endpoints that integrate Eliza agent with SSE streaming for real-time responses.

### API Structure

```python
# backend/app/api/v1/companion.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.agents.eliza_agent import ElizaAgent
from app.services.memory_service import MemoryService
from app.db.session import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/companion", tags=["companion"])

@router.post("/chat")
async def create_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create or retrieve conversation, return conversation_id."""
    # Get or create conversation
    conversation = await get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )

    # Add user message to conversation
    conversation.messages.append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })
    await db.commit()

    return {
        "conversation_id": str(conversation.id),
        "message": "Stream started"
    }

@router.get("/stream/{conversation_id}")
async def stream_response(
    conversation_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """SSE stream for Eliza's response."""
    # Get conversation
    conversation = await get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    # Initialize agent
    memory_service = MemoryService(db)
    agent = ElizaAgent(memory_service)

    # Get last user message
    last_user_msg = conversation.messages[-1]["content"]

    async def generate_stream():
        """Generator for SSE stream."""
        try:
            # Initialize state
            state = {
                "user_id": str(current_user.id),
                "messages": conversation.messages,
                "conversation_id": conversation_id
            }

            # Run agent graph with streaming
            async for chunk in agent.stream_chat(state, last_user_msg):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            # Save final response to conversation
            final_response = await agent.get_final_response()
            conversation.messages.append({
                "role": "assistant",
                "content": final_response,
                "timestamp": datetime.now().isoformat()
            })
            await db.commit()

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

### SSE Format

```
data: {"type": "token", "content": "I "}
data: {"type": "token", "content": "hear "}
data: {"type": "token", "content": "you"}
data: {"type": "complete"}
```

---

## Story 2.5: Build Companion Chat UI (Frontend)

### Component Structure

```typescript
// frontend/src/components/companion/CompanionChat.tsx

"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function CompanionChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Create chat session
    const response = await fetch("/api/v1/companion/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: input,
        conversation_id: conversationId,
      }),
    });

    const { conversation_id } = await response.json();
    setConversationId(conversation_id);

    // Start SSE stream
    const eventSource = new EventSource(
      `/api/v1/companion/stream/${conversation_id}`
    );

    let aiMessageContent = "";
    const aiMessage: Message = {
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, aiMessage]);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        aiMessageContent += data.content;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1].content = aiMessageContent;
          return updated;
        });
      } else if (data.type === "complete") {
        eventSource.close();
        setIsLoading(false);
      } else if (data.type === "error") {
        console.error("Stream error:", data.message);
        eventSource.close();
        setIsLoading(false);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsLoading(false);
    };

    eventSourceRef.current = eventSource;
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-purple-50 to-white">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.role === "user"
                    ? "bg-purple-600 text-white"
                    : "bg-white text-gray-800 shadow-md"
                }`}
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## Story 2.6: Implement Emotional State Detection

### Service Structure

```python
# backend/app/services/emotion_service.py

from transformers import pipeline
from typing import Dict, List
import torch

class EmotionService:
    def __init__(self):
        # Load model on startup (cache in memory)
        self.classifier = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-emotion-multilingual-latest",
            return_all_scores=True,
            device=0 if torch.cuda.is_available() else -1
        )

    def detect_emotion(self, text: str) -> Dict:
        """Detect emotion with nuanced interpretation."""
        # Get classifier scores
        results = self.classifier(text)[0]
        scores = {r['label']: r['score'] for r in results}

        # Find dominant emotion
        dominant = max(scores.items(), key=lambda x: x[1])[0]

        # Calculate intensity
        intensity = scores[dominant]

        # Interpret nuanced context
        context = self._interpret_context(scores)

        # Extract triggers (simple keyword extraction for MVP)
        triggers = self._extract_triggers(text)

        return {
            "dominant": dominant,
            "scores": scores,
            "context": context,
            "intensity": intensity,
            "triggers": triggers
        }

    def _interpret_context(self, scores: Dict[str, float]) -> str:
        """Map emotion scores to nuanced contexts."""
        fear = scores.get('fear', 0)
        sadness = scores.get('sadness', 0)
        anger = scores.get('anger', 0)
        joy = scores.get('joy', 0)
        love = scores.get('love', 0)

        # Overwhelm: fear + sadness
        if fear > 0.5 and sadness > 0.4:
            return "overwhelm"

        # Frustration: fear + anger
        if fear > 0.4 and anger > 0.4:
            return "frustration"

        # Loneliness: sadness + low joy
        if sadness > 0.5 and joy < 0.2:
            return "loneliness"

        # Romantic interest: love + joy
        if love > 0.5 and joy > 0.3:
            return "romantic_interest"

        # Default to dominant emotion
        return max(scores.items(), key=lambda x: x[1])[0]

    def _extract_triggers(self, text: str) -> List[str]:
        """Extract emotion triggers from text (simple for MVP)."""
        # Simple keyword extraction
        trigger_keywords = [
            "overwhelmed", "stressed", "worried", "anxious",
            "happy", "excited", "sad", "lonely", "angry"
        ]
        triggers = []
        text_lower = text.lower()
        for keyword in trigger_keywords:
            if keyword in text_lower:
                triggers.append(keyword)
        return triggers
```

---

## Implementation Timeline

**Story 2.3 (Eliza Agent):** 8-12 hours

- LangGraph state machine setup
- Memory integration
- System prompt design
- Streaming support

**Story 2.4 (Chat API):** 4-6 hours

- FastAPI endpoints
- SSE streaming
- Conversation persistence
- Error handling

**Story 2.5 (Chat UI):** 6-8 hours

- React component
- SSE client integration
- Animations (Framer Motion)
- Responsive design

**Story 2.6 (Emotion Detection):** 4-6 hours

- Hugging Face model integration
- Nuanced interpretation
- Integration with agent

**Total Epic 2 Remaining:** ~22-32 hours

---

## Key Dependencies

- **Story 2.3** depends on Story 2.2 (MemoryService)
- **Story 2.4** depends on Story 2.3 (ElizaAgent)
- **Story 2.5** depends on Story 2.4 (Chat API)
- **Story 2.6** can be done in parallel with 2.3-2.5 (integrated into agent)

---

## Testing Strategy

1. **Unit Tests**: Each node function tested independently
2. **Integration Tests**: Full agent flow with mock memory service
3. **E2E Tests**: Full conversation flow (Playwright)
4. **Case Study Tests**: Real user scenarios (from Story 2.2)

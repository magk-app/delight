# Story 2.5: Companion Chat UI with Essential Memory (Vertical Slice)

**Story ID:** 2.5
**Epic:** 2 - Companion & Memory System
**Status:** drafted
**Priority:** P0 (Core User Experience - First Working Chat)
**Estimated Effort:** 8-12 hours (vertical slice including frontend + backend + essential memory)
**Assignee:** Claude Dev Agent
**Created:** 2025-11-12
**Updated:** 2025-11-12 (Initial draft - vertical slice approach)

---

## User Story

**As a** Delight user,
**I want** to chat with Eliza and see her remember context from previous messages,
**So that** I can have meaningful conversations where she understands my situation and provides contextual support.

---

## Context

### Problem Statement

This is the **critical validation story** for Epic 2. Instead of building memory infrastructure blindly (Story 2.2) and then discovering issues when building the UI, we take a **vertical slice approach**:

- Build a **working chat interface** with SSE streaming
- Implement **essential memory operations** inline (not as separate service yet)
- Enable **all test scenarios** (venting, creating tasks, memory recall)
- **Validate the experience** before committing to complex architecture

This approach follows the "make it work, make it right, make it fast" principle:
1. **Story 2.5 (this story)**: Make it work - functional chat with basic memory
2. **Story 2.2 (refactored)**: Make it right - extract service, add hybrid search
3. **Story 2.3**: Make it fast - advanced agent features, optimizations

### Why This Approach?

**From BMAD Best Practices: Vertical Slicing**

We implement a vertical slice instead of horizontal layers because:

- ✅ **Immediate Validation**: See memory retrieval working in browser, not just unit tests
- ✅ **Real User Testing**: Test all scenarios (venting, tasks, updates) immediately
- ✅ **Fast Feedback Loop**: Discover what hybrid search parameters actually need
- ✅ **Motivating Progress**: Functional chat beats infrastructure building
- ✅ **Risk Mitigation**: Fail fast on UX issues before building complex architecture

**What This Story Includes (Scope):**
- Chat UI with real-time SSE streaming
- Simple Eliza agent (basic prompt, no LangGraph yet)
- Essential memory operations (inline, not extracted service):
  - Store conversations as memories
  - Query memories with semantic search (vector similarity only)
  - Show retrieved memories in responses
- All test scenarios working end-to-end

**What This Story Defers (to Story 2.2):**
- ❌ Memory service extraction (keep it inline for now)
- ❌ Hybrid search (time decay, frequency boost)
- ❌ Memory pruning worker
- ❌ Goal-based search
- ❌ User priority system
- ❌ Advanced features (universal factors, etc.)

### Dependencies

- **Prerequisite Stories:**
  - 2.1 (PostgreSQL pgvector and Memory Schema) ✅ Complete
  - 1.3 (Clerk Authentication) ✅ Complete
  - Database tables (`memories`, `conversations`) exist
  - HNSW index created and functional
  - OpenAI API key configured (`OPENAI_API_KEY`)

- **Epic 2 Context:** This story **validates**:
  - Memory storage patterns (what metadata is useful?)
  - Memory retrieval quality (does semantic search work?)
  - User interaction flow (how do users want to chat?)
  - SSE streaming UX (is it smooth enough?)

- **This Story Enables**:
  - Story 2.2: Extract memory service based on what works
  - Story 2.3: Replace simple agent with LangGraph
  - Story 2.6: Add emotion detection to working system

### Technical Background

**From Epic 2 Tech Spec (tech-spec-epic-2.md lines 390-458 - Chat Flow section):**

This story implements the basic chat flow:
1. User types message → POST /api/v1/companion/chat
2. Backend stores user message → conversations table
3. Backend queries memories → basic vector search (HNSW index)
4. Eliza generates response → OpenAI GPT-4o-mini with memory context
5. Response streams via SSE → EventSource on frontend
6. Exchange stored as task memory → for next conversation

[Source: docs/tech-spec-epic-2.md lines 119-138]

**From "How Eliza Should Respond" (docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md):**

The chat must support these scenarios:
- **Venting**: "I'm overwhelmed with schoolwork" → store as personal memory
- **Creating Task**: "I want to work on my goal" → store as project/task memory
- **Asking Questions**: "What did I say about stress?" → retrieve memories
- **Memory Recall**: Second message references first message context

[Source: docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md - Case study examples]

---

## Acceptance Criteria

### AC1: Chat UI Displays and Accepts Messages

**Given** I am authenticated and viewing `/companion` page
**When** I type a message and press Enter or click Send
**Then**:
- Message appears immediately in chat history (optimistic update)
- Input field clears
- Loading indicator shows (typing dots animation)
- Message is visibly marked as "user" message
- Timestamp displays for message
- Send button disabled during loading

**Verification Steps:**
```typescript
// Playwright test
await page.goto('/companion');
await page.fill('[data-testid="chat-input"]', 'Hello Eliza');
await page.click('[data-testid="send-button"]');

// Message appears
await expect(page.locator('[data-testid="message-user"]')).toContainText('Hello Eliza');

// Loading state
await expect(page.locator('[data-testid="loading-indicator"]')).toBeVisible();

// Input cleared
await expect(page.locator('[data-testid="chat-input"]')).toHaveValue('');
```

[Source: docs/tech-spec-epic-2.md lines 704-715, docs/epics.md lines 308-310]

### AC2: SSE Streaming Displays Tokens in Real-Time

**Given** I sent a message and backend is responding
**When** tokens stream via SSE
**Then**:
- Eliza's message appears token-by-token (word-by-word)
- Smooth scrolling keeps latest token visible
- Loading indicator hides when first token arrives
- Message builds up naturally (not jumpy)
- Complete message marked with timestamp when done
- Connection errors show user-friendly message

**Verification Steps:**
```typescript
// Send message
await page.fill('[data-testid="chat-input"]', 'How are you?');
await page.click('[data-testid="send-button"]');

// Wait for first token
await expect(page.locator('[data-testid="message-assistant"]')).toBeVisible({ timeout: 2000 });

// Token-by-token display (check message grows)
const message = page.locator('[data-testid="message-assistant"]').last();
await expect(message).toContainText(/\w+/); // At least one word
await page.waitForTimeout(500);
const text1 = await message.textContent();
await page.waitForTimeout(500);
const text2 = await message.textContent();
expect(text2.length).toBeGreaterThan(text1.length); // Message grew
```

[Source: docs/tech-spec-epic-2.md lines 339-347, docs/epics.md lines 311-312]

### AC3: Conversation Persists Across Page Refreshes

**Given** I had a conversation with Eliza
**When** I refresh the page or navigate away and back
**Then**:
- Full conversation history loads
- Messages display in chronological order
- User and assistant messages correctly labeled
- Timestamps preserved
- Conversation continues from same context (conversation_id maintained)

**Verification Steps:**
```typescript
// Have conversation
await page.fill('[data-testid="chat-input"]', 'Remember I like coffee');
await page.click('[data-testid="send-button"]');
await expect(page.locator('[data-testid="message-assistant"]')).toBeVisible();

// Refresh page
await page.reload();

// History loads
await expect(page.locator('[data-testid="message-user"]')).toContainText('Remember I like coffee');
await expect(page.locator('[data-testid="message-assistant"]')).toBeVisible();
```

[Source: docs/tech-spec-epic-2.md lines 197-206]

### AC4: Memory Storage - Venting Scenario

**Given** I vent about stress or problems
**When** I send message: "I'm overwhelmed with my schoolwork because I have to catch up"
**Then**:
- Message stored in `conversations` table
- Memory created in `memories` table:
  - `memory_type` = "personal" (stressor)
  - `content` = message content
  - `embedding` = 1536-dim vector (OpenAI)
  - `metadata` includes: `{source: 'conversation', category: 'academic', stressor: true}`
- Eliza responds empathetically (acknowledges feeling)
- Memory retrievable in next conversation

**Verification Steps:**
```python
# Backend test
async def test_venting_creates_personal_memory(client, test_user):
    # Send venting message
    response = await client.post(
        "/api/v1/companion/chat",
        json={
            "message": "I'm overwhelmed with my schoolwork because I have to catch up"
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Check memory created
    memories = await db.execute(
        select(Memory).where(
            Memory.user_id == test_user.id,
            Memory.memory_type == MemoryType.PERSONAL
        )
    )
    memory = memories.scalars().first()
    assert memory is not None
    assert "overwhelmed" in memory.content.lower()
    assert memory.metadata.get("stressor") == True
    assert memory.embedding is not None
    assert len(memory.embedding) == 1536
```

[Source: docs/tech-spec-epic-2.md lines 659-687, docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md - Stressor Log principle]

### AC5: Memory Storage - Task/Goal Scenario

**Given** I discuss tasks or goals
**When** I send message: "I want to work on my goal to graduate early"
**Then**:
- Memory created with `memory_type` = "project"
- `metadata` includes: `{source: 'conversation', category: 'goal', goal_related: true}`
- Eliza responds supportively (acknowledges goal)
- Memory retrievable when discussing goals later

**Verification Steps:**
```python
async def test_goal_discussion_creates_project_memory(client, test_user):
    response = await client.post(
        "/api/v1/companion/chat",
        json={"message": "I want to work on my goal to graduate early"},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    # Check project memory created
    memories = await db.execute(
        select(Memory).where(
            Memory.user_id == test_user.id,
            Memory.memory_type == MemoryType.PROJECT
        )
    )
    memory = memories.scalars().first()
    assert memory is not None
    assert memory.metadata.get("goal_related") == True
```

[Source: docs/tech-spec-epic-2.md lines 659-687, docs/epics.md lines 313-315]

### AC6: Memory Retrieval - Context Recall

**Given** I had previous conversations stored as memories
**When** I send a new message related to past topics
**Then**:
- Backend queries memories via vector similarity search
- Top 5 relevant memories retrieved (semantic search)
- Memories included in Eliza's context window
- Eliza's response references past context
- Response feels contextual, not generic

**Example Flow (from "How Eliza Should Respond" case study):**
```
Message 1: "I'm stressed about class registration"
→ Memory stored: {type: personal, content: "stressed about class registration"}

Message 2: "I'm feeling overwhelmed"
→ Queries memories, finds "stressed about class registration"
→ Eliza: "I remember you mentioned stress about class registration. Is this related?"
```

[Source: docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md, docs/tech-spec-epic-2.md lines 423-445]

**Verification Steps:**
```python
async def test_memory_retrieval_in_conversation(client, test_user, db):
    # First message (creates memory)
    await client.post("/api/v1/companion/chat",
        json={"message": "I'm stressed about class registration"},
        headers={"Authorization": f"Bearer {test_user.token}"})

    # Wait for memory to be created
    await asyncio.sleep(0.5)

    # Second message (should retrieve memory)
    response = await client.post("/api/v1/companion/chat",
        json={"message": "I'm feeling overwhelmed"},
        headers={"Authorization": f"Bearer {test_user.token}"})

    # Get SSE stream response
    stream_response = await client.get(
        f"/api/v1/companion/stream/{response.json()['conversation_id']}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    # Response should reference class registration
    full_response = ""
    async for line in stream_response.aiter_lines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if data["type"] == "token":
                full_response += data["content"]

    assert "class" in full_response.lower() or "registration" in full_response.lower()
    # Eliza references past context
```

### AC7: Mobile Responsive Design

**Given** I view the chat on mobile device (<768px width)
**When** I interact with the chat
**Then**:
- Chat takes full screen (no wasted space)
- Input field always visible at bottom
- Messages readable without zooming
- Send button easily tappable (>44px touch target)
- Keyboard doesn't obscure input field
- Scrolling smooth on touch

**Verification Steps:**
```typescript
// Playwright mobile emulation
await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

await page.goto('/companion');

// Layout fills screen
const chatContainer = page.locator('[data-testid="chat-container"]');
await expect(chatContainer).toBeVisible();

// Input accessible
const input = page.locator('[data-testid="chat-input"]');
await expect(input).toBeVisible();
await input.click();
await input.fill('Test message');

// Send button tappable
const sendButton = page.locator('[data-testid="send-button"]');
const box = await sendButton.boundingBox();
expect(box.width).toBeGreaterThanOrEqual(44);
expect(box.height).toBeGreaterThanOrEqual(44);
```

[Source: docs/tech-spec-epic-2.md lines 704-715]

### AC8: Accessible Keyboard Navigation

**Given** I use keyboard navigation (no mouse)
**When** I interact with the chat
**Then**:
- Tab key moves focus through UI elements
- Enter key sends message from input field
- Escape key cancels message composition
- Screen reader announces new messages
- ARIA labels present for all interactive elements
- Focus indicators visible

**Verification Steps:**
```typescript
// Keyboard-only test
await page.goto('/companion');

// Tab to input
await page.keyboard.press('Tab');
await page.keyboard.press('Tab'); // Navigate through header
const focusedElement = await page.evaluate(() => document.activeElement.getAttribute('data-testid'));
expect(focusedElement).toBe('chat-input');

// Type and send with Enter
await page.keyboard.type('Hello Eliza');
await page.keyboard.press('Enter');

// Message sent
await expect(page.locator('[data-testid="message-user"]')).toContainText('Hello Eliza');

// ARIA labels present
const input = page.locator('[data-testid="chat-input"]');
await expect(input).toHaveAttribute('aria-label');
```

[Source: docs/tech-spec-epic-2.md lines 704-715]

---

## Tasks / Subtasks

### Task 1: Create Chat API Endpoints (AC: #1, #2, #6)

**Estimated Time:** 2 hours

- [ ] **1.1** Create `packages/backend/app/api/v1/companion.py`
- [ ] **1.2** Implement `POST /api/v1/companion/chat` endpoint:
  ```python
  @router.post("/chat")
  async def chat_with_eliza(
      request: ChatRequest,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ) -> ChatResponse:
      # Create/retrieve conversation
      # Store user message
      # Return conversation_id
  ```
- [ ] **1.3** Implement `GET /api/v1/companion/stream/{conversation_id}` endpoint:
  ```python
  @router.get("/stream/{conversation_id}")
  async def stream_response(
      conversation_id: UUID,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      # Verify conversation belongs to user
      # Query memories (basic vector search)
      # Generate Eliza response with OpenAI streaming
      # Store assistant message
      # Store conversation as task memory
      # Yield SSE events
  ```
- [ ] **1.4** Implement `GET /api/v1/companion/history` endpoint:
  ```python
  @router.get("/history")
  async def get_conversation_history(
      limit: int = 50,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ) -> ConversationHistoryResponse:
      # Return user's conversations
  ```
- [ ] **1.5** Add Pydantic schemas in `app/schemas/companion.py`:
  - `ChatRequest`, `ChatResponse`, `ConversationHistoryResponse`
- [ ] **1.6** Register router in `app/api/v1/__init__.py`

### Task 2: Implement Essential Memory Operations (Inline) (AC: #4, #5, #6)

**Estimated Time:** 2.5 hours

- [ ] **2.1** Create inline helper functions in `companion.py`:
  ```python
  async def _generate_embedding(text: str) -> List[float]:
      """Generate embedding using OpenAI API."""
      client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
      response = await client.embeddings.create(
          model="text-embedding-3-small",
          input=text
      )
      return response.data[0].embedding

  async def _store_memory(
      db: AsyncSession,
      user_id: UUID,
      memory_type: MemoryType,
      content: str,
      metadata: Dict[str, Any]
  ) -> Memory:
      """Store memory with automatic embedding generation."""
      embedding = await _generate_embedding(content)
      memory = Memory(
          user_id=user_id,
          memory_type=memory_type,
          content=content,
          embedding=embedding,
          extra_data=metadata  # Remember: metadata is reserved keyword
      )
      db.add(memory)
      await db.commit()
      await db.refresh(memory)
      return memory

  async def _query_memories(
      db: AsyncSession,
      user_id: UUID,
      query_text: str,
      limit: int = 5
  ) -> List[Memory]:
      """Query memories using basic vector similarity search."""
      query_embedding = await _generate_embedding(query_text)

      # Basic vector search (no hybrid scoring yet)
      result = await db.execute(
          select(Memory)
          .where(Memory.user_id == user_id)
          .order_by(Memory.embedding.cosine_distance(query_embedding))
          .limit(limit)
      )
      return result.scalars().all()
  ```
- [ ] **2.2** Implement memory storage logic in `stream_response()`:
  - Determine memory type from message content (simple heuristics)
  - Store user message as memory
  - Store assistant response as task memory
- [ ] **2.3** Implement memory retrieval in `stream_response()`:
  - Query memories before generating response
  - Format memories for Eliza's context window
- [ ] **2.4** Add simple heuristics for memory type detection:
  ```python
  def _detect_memory_type(message: str) -> MemoryType:
      """Determine memory type from message content."""
      message_lower = message.lower()

      # Check for stressors/venting
      if any(word in message_lower for word in ['overwhelmed', 'stressed', 'anxious', 'worried']):
          return MemoryType.PERSONAL

      # Check for goals/plans
      if any(word in message_lower for word in ['goal', 'plan', 'want to', 'working on']):
          return MemoryType.PROJECT

      # Default to task
      return MemoryType.TASK
  ```

### Task 3: Implement Simple Eliza Agent (AC: #6)

**Estimated Time:** 1.5 hours

- [ ] **3.1** Create `packages/backend/app/agents/simple_eliza.py`
- [ ] **3.2** Implement `SimpleElizaAgent` class:
  ```python
  class SimpleElizaAgent:
      """Simple Eliza agent without LangGraph (for vertical slice)."""

      def __init__(self, openai_api_key: str):
          self.client = AsyncOpenAI(api_key=openai_api_key)

      async def generate_response(
          self,
          user_message: str,
          conversation_history: List[Dict[str, str]],
          retrieved_memories: List[Memory]
      ) -> AsyncIterator[str]:
          """Generate streaming response with memory context."""
          # Build system prompt
          system_prompt = self._build_system_prompt(retrieved_memories)

          # Build messages
          messages = [
              {"role": "system", "content": system_prompt},
              *conversation_history,
              {"role": "user", "content": user_message}
          ]

          # Stream response
          stream = await self.client.chat.completions.create(
              model="gpt-4o-mini",
              messages=messages,
              stream=True,
              temperature=0.7
          )

          async for chunk in stream:
              if chunk.choices[0].delta.content:
                  yield chunk.choices[0].delta.content

      def _build_system_prompt(self, memories: List[Memory]) -> str:
          """Build system prompt with memory context."""
          base_prompt = """You are Eliza, an emotionally intelligent AI companion.

You help users balance ambition with well-being. You:
- Listen empathetically to their struggles
- Remember past conversations and reference them
- Validate their feelings before offering suggestions
- Distinguish between controllable and uncontrollable stressors
- Suggest circuit breakers when they're overwhelmed
- Celebrate their wins and encourage momentum

Be warm, supportive, and contextual."""

          if memories:
              memory_context = "\n\nWhat you remember about this user:\n"
              for memory in memories:
                  memory_context += f"- {memory.content}\n"
              return base_prompt + memory_context

          return base_prompt
  ```
- [ ] **3.3** Integrate agent into `stream_response()` endpoint
- [ ] **3.4** Add error handling for OpenAI API failures

### Task 4: Implement SSE Streaming (AC: #2)

**Estimated Time:** 1 hour

- [ ] **4.1** Install SSE dependencies (if not already present):
  ```toml
  # pyproject.toml - already have fastapi with streaming support
  ```
- [ ] **4.2** Implement SSE response in `stream_response()`:
  ```python
  from fastapi.responses import StreamingResponse

  async def stream_response(...):
      async def event_generator():
          try:
              # Query memories
              memories = await _query_memories(db, current_user.id, last_user_message)

              # Generate response
              agent = SimpleElizaAgent(settings.OPENAI_API_KEY)
              full_response = ""

              async for token in agent.generate_response(
                  user_message=last_user_message,
                  conversation_history=conversation.messages[-10:],  # Last 10 messages
                  retrieved_memories=memories
              ):
                  full_response += token
                  yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

              # Store assistant message
              # Store as task memory

              yield f"data: {json.dumps({'type': 'complete'})}\n\n"

          except Exception as e:
              logger.error(f"Streaming error: {e}")
              yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

      return StreamingResponse(
          event_generator(),
          media_type="text/event-stream",
          headers={
              "Cache-Control": "no-cache",
              "X-Accel-Buffering": "no"  # Disable nginx buffering
          }
      )
  ```
- [ ] **4.3** Test SSE streaming with curl:
  ```bash
  curl -N -H "Authorization: Bearer {token}" \
    http://localhost:8000/api/v1/companion/stream/{conversation_id}
  ```

### Task 5: Create Chat UI Components (AC: #1, #2, #3, #7)

**Estimated Time:** 3 hours

- [ ] **5.1** Create `packages/frontend/src/app/companion/page.tsx`:
  ```typescript
  'use client';

  import { useState, useEffect, useRef } from 'react';
  import { useUser } from '@clerk/nextjs';
  import { CompanionChat } from '@/components/companion/CompanionChat';

  export default function CompanionPage() {
      return (
          <main className="flex h-screen flex-col">
              <header className="border-b px-6 py-4">
                  <h1 className="text-2xl font-bold">Chat with Eliza</h1>
              </header>
              <CompanionChat />
          </main>
      );
  }
  ```
- [ ] **5.2** Create `packages/frontend/src/components/companion/CompanionChat.tsx`:
  ```typescript
  'use client';

  import { useState, useEffect, useRef } from 'react';
  import { MessageList } from './MessageList';
  import { MessageInput } from './MessageInput';
  import { useChat } from '@/lib/hooks/useChat';

  export function CompanionChat() {
      const { messages, isLoading, sendMessage, error } = useChat();

      return (
          <div className="flex flex-1 flex-col" data-testid="chat-container">
              <MessageList messages={messages} isLoading={isLoading} />
              <MessageInput onSend={sendMessage} disabled={isLoading} />
              {error && (
                  <div className="px-6 py-2 bg-red-50 text-red-600 text-sm">
                      {error}
                  </div>
              )}
          </div>
      );
  }
  ```
- [ ] **5.3** Create `packages/frontend/src/components/companion/MessageList.tsx`:
  ```typescript
  import { useEffect, useRef } from 'react';
  import { Message } from './Message';
  import { LoadingIndicator } from './LoadingIndicator';

  interface MessageListProps {
      messages: Array<{ role: 'user' | 'assistant'; content: string; timestamp: Date }>;
      isLoading: boolean;
  }

  export function MessageList({ messages, isLoading }: MessageListProps) {
      const bottomRef = useRef<HTMLDivElement>(null);

      // Auto-scroll to bottom
      useEffect(() => {
          bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, [messages]);

      return (
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {messages.map((message, index) => (
                  <Message key={index} {...message} />
              ))}
              {isLoading && <LoadingIndicator />}
              <div ref={bottomRef} />
          </div>
      );
  }
  ```
- [ ] **5.4** Create `packages/frontend/src/components/companion/Message.tsx`:
  - User message styling
  - Assistant message styling
  - Timestamp display
  - Framer Motion animations (fade in)
- [ ] **5.5** Create `packages/frontend/src/components/companion/MessageInput.tsx`:
  - Input field with auto-resize
  - Send button
  - Loading state handling
  - Enter to send, Shift+Enter for new line
- [ ] **5.6** Create `packages/frontend/src/components/companion/LoadingIndicator.tsx`:
  - Typing dots animation
  - Framer Motion breathing effect

### Task 6: Implement useChat Hook with SSE (AC: #2, #3)

**Estimated Time:** 2 hours

- [ ] **6.1** Create `packages/frontend/src/lib/hooks/useChat.ts`:
  ```typescript
  import { useState, useEffect, useRef } from 'react';
  import { useAuth } from '@clerk/nextjs';

  interface Message {
      role: 'user' | 'assistant';
      content: string;
      timestamp: Date;
  }

  export function useChat() {
      const { getToken } = useAuth();
      const [messages, setMessages] = useState<Message[]>([]);
      const [isLoading, setIsLoading] = useState(false);
      const [error, setError] = useState<string | null>(null);
      const [conversationId, setConversationId] = useState<string | null>(null);
      const eventSourceRef = useRef<EventSource | null>(null);

      // Load conversation history on mount
      useEffect(() => {
          loadHistory();
      }, []);

      async function loadHistory() {
          const token = await getToken();
          const response = await fetch('/api/v1/companion/history', {
              headers: { Authorization: `Bearer ${token}` }
          });
          const data = await response.json();

          if (data.conversations.length > 0) {
              const latest = data.conversations[0];
              setConversationId(latest.id);
              setMessages(latest.messages.map(m => ({
                  ...m,
                  timestamp: new Date(m.timestamp)
              })));
          }
      }

      async function sendMessage(content: string) {
          // Optimistic update
          const userMessage: Message = {
              role: 'user',
              content,
              timestamp: new Date()
          };
          setMessages(prev => [...prev, userMessage]);
          setIsLoading(true);
          setError(null);

          try {
              const token = await getToken();

              // Send message
              const response = await fetch('/api/v1/companion/chat', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${token}`
                  },
                  body: JSON.stringify({
                      message: content,
                      conversation_id: conversationId
                  })
              });

              const data = await response.json();
              setConversationId(data.conversation_id);

              // Start SSE stream
              streamResponse(data.conversation_id, token);
          } catch (err) {
              setError('Failed to send message. Please try again.');
              setIsLoading(false);
          }
      }

      function streamResponse(convId: string, token: string) {
          // Close existing connection
          eventSourceRef.current?.close();

          // Create new SSE connection
          const eventSource = new EventSource(
              `/api/v1/companion/stream/${convId}?token=${token}`
          );
          eventSourceRef.current = eventSource;

          let assistantMessage = '';

          eventSource.onmessage = (event) => {
              const data = JSON.parse(event.data);

              if (data.type === 'token') {
                  assistantMessage += data.content;

                  // Update message in real-time
                  setMessages(prev => {
                      const lastMessage = prev[prev.length - 1];
                      if (lastMessage?.role === 'assistant') {
                          return [...prev.slice(0, -1), {
                              ...lastMessage,
                              content: assistantMessage
                          }];
                      } else {
                          return [...prev, {
                              role: 'assistant',
                              content: assistantMessage,
                              timestamp: new Date()
                          }];
                      }
                  });
              } else if (data.type === 'complete') {
                  setIsLoading(false);
                  eventSource.close();
              } else if (data.type === 'error') {
                  setError(data.message);
                  setIsLoading(false);
                  eventSource.close();
              }
          };

          eventSource.onerror = () => {
              setError('Connection lost. Please try again.');
              setIsLoading(false);
              eventSource.close();
          };
      }

      return { messages, isLoading, sendMessage, error };
  }
  ```
- [ ] **6.2** Add error handling for SSE disconnections
- [ ] **6.3** Add auto-reconnect logic (optional enhancement)
- [ ] **6.4** Test SSE streaming in browser DevTools

### Task 7: Add Framer Motion Animations (AC: #2, #7)

**Estimated Time:** 1 hour

- [ ] **7.1** Install Framer Motion:
  ```bash
  cd packages/frontend
  pnpm add framer-motion
  ```
- [ ] **7.2** Add message animations in `Message.tsx`:
  ```typescript
  import { motion } from 'framer-motion';

  export function Message({ role, content, timestamp }: MessageProps) {
      return (
          <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={role === 'user' ? 'user-message' : 'assistant-message'}
          >
              {/* Message content */}
          </motion.div>
      );
  }
  ```
- [ ] **7.3** Add breathing effect to loading indicator:
  ```typescript
  import { motion } from 'framer-motion';

  export function LoadingIndicator() {
      return (
          <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="typing-dots"
          >
              <span>•</span>
              <span>•</span>
              <span>•</span>
          </motion.div>
      );
  }
  ```
- [ ] **7.4** Test animations on different devices

### Task 8: Mobile Responsive Styling (AC: #7)

**Estimated Time:** 1 hour

- [ ] **8.1** Add responsive CSS to chat components:
  ```tsx
  // CompanionChat.tsx
  <div className="flex h-screen flex-col md:max-w-4xl md:mx-auto">
      {/* Chat content */}
  </div>
  ```
- [ ] **8.2** Ensure input field stays visible on mobile keyboard open
- [ ] **8.3** Test on mobile viewport (375px width)
- [ ] **8.4** Test touch interactions (scroll, tap)
- [ ] **8.5** Adjust font sizes for mobile readability

### Task 9: Accessibility (AC: #8)

**Estimated Time:** 1 hour

- [ ] **9.1** Add ARIA labels to interactive elements:
  ```typescript
  <input
      aria-label="Chat message input"
      data-testid="chat-input"
      {...props}
  />

  <button
      aria-label="Send message"
      data-testid="send-button"
      {...props}
  >
      Send
  </button>
  ```
- [ ] **9.2** Add screen reader announcements for new messages:
  ```typescript
  <div
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      className="sr-only"
  >
      {messages[messages.length - 1]?.content}
  </div>
  ```
- [ ] **9.3** Ensure keyboard navigation works (Tab, Enter, Escape)
- [ ] **9.4** Test with screen reader (NVDA/VoiceOver)
- [ ] **9.5** Verify focus indicators visible

### Task 10: Integration Testing (AC: All)

**Estimated Time:** 2 hours

- [ ] **10.1** Create `packages/backend/tests/integration/test_companion_chat.py`:
  - Test POST /chat endpoint
  - Test SSE streaming endpoint
  - Test memory storage during chat
  - Test memory retrieval in responses
- [ ] **10.2** Create `packages/frontend/tests/e2e/companion-chat.spec.ts`:
  - Test sending message
  - Test SSE streaming display
  - Test conversation persistence
  - Test mobile responsive
  - Test keyboard navigation
- [ ] **10.3** Test all scenarios end-to-end:
  - **Venting**: "I'm overwhelmed" → personal memory created
  - **Goal**: "I want to work on my goal" → project memory created
  - **Recall**: Second message references first message
- [ ] **10.4** Test error scenarios:
  - OpenAI API failure
  - SSE disconnection
  - Network errors

### Task 11: Documentation (AC: All)

**Estimated Time:** 1 hour

- [ ] **11.1** Add docstrings to all backend functions
- [ ] **11.2** Document inline memory operations (note: will extract to service in Story 2.2)
- [ ] **11.3** Add JSDoc comments to frontend components
- [ ] **11.4** Update `docs/dev/SETUP.md` with companion chat setup
- [ ] **11.5** Create `docs/stories/2-5-TESTING-GUIDE.md` with manual testing steps
- [ ] **11.6** Document memory storage patterns discovered

---

## Dev Notes

### Why Vertical Slice First?

**From BMAD Best Practices:**

This story follows the **vertical slice pattern** instead of horizontal layering:

❌ **Horizontal (Bad)**: Story 2.2 (Memory Service) → Story 2.5 (Chat UI)
- Can't validate memory works until UI built
- Discover UX issues late
- Harder to iterate on architecture

✅ **Vertical (Good)**: Story 2.5 (Chat + Essential Memory) → Story 2.2 (Extract Service)
- Immediate validation in browser
- Fast feedback loop
- Easy to refine based on real usage

### Essential Memory Operations (Inline)

**Decision: Keep memory operations inline (not extracted service) for this story**

**Why:**
- Faster to implement (no service abstraction yet)
- Easier to iterate based on what we learn
- Story 2.2 will extract service once patterns proven

**Operations Included:**
```python
# In companion.py
async def _generate_embedding(text: str) -> List[float]
async def _store_memory(db, user_id, type, content, metadata) -> Memory
async def _query_memories(db, user_id, query, limit=5) -> List[Memory]
def _detect_memory_type(message: str) -> MemoryType
```

**Operations Deferred (to Story 2.2):**
- Hybrid search (time decay, frequency boost)
- Memory pruning worker
- Advanced search (goal-based, user priority)
- Service extraction and proper architecture

### Learnings from Previous Story (2.1)

**Story 2.1 Delivered Database Foundation:** [Source: stories/2-1-set-up-postgresql-pgvector-and-memory-schema.md]

**New Files Available (Use These - Don't Recreate):**
- **`packages/backend/app/models/memory.py`** - Memory, MemoryCollection models with MemoryType enum
  - Classes: `Memory`, `MemoryCollection`, `MemoryType` enum (PERSONAL, PROJECT, TASK)
  - Use these models directly in Task 2 for inline memory operations
- **`packages/backend/app/schemas/memory.py`** - Pydantic schemas
  - Schemas: `MemoryCreate`, `MemoryUpdate`, `MemoryResponse`, `MemoryQuery`, `MemoryWithDistance`
  - Use these schemas for API request/response validation
- **`packages/backend/app/db/migrations/versions/003_create_memory_tables.py`** - Alembic migration
  - Creates `memories` table with VECTOR(1536) column
  - Creates `memory_collections` table
  - HNSW index already created and optimized
- **`packages/backend/test_memory_system.py`** - Example usage patterns
  - Shows how to create memories with metadata
  - Demonstrates vector similarity query structure

**⚠️ CRITICAL: SQLAlchemy Reserved Keyword Issue**

From Story 2.1 Debug Log (lines 574-578):
- **Problem:** `metadata` is a reserved attribute name in SQLAlchemy Declarative API
- **Solution:** Memory model uses `extra_data` attribute internally
- **Database column is still named "metadata"** (for API compatibility)
- **In Task 2, you MUST use:** `memory.extra_data = {...}` NOT `memory.metadata = {...}`
- Pydantic schemas handle the alias automatically in JSON API responses
- Example:
  ```python
  # ✅ CORRECT - Use extra_data attribute
  memory = Memory(
      user_id=user_id,
      memory_type=MemoryType.PERSONAL,
      content="I'm stressed about class registration",
      extra_data={"stressor": True, "category": "academic"}  # ← Use extra_data!
  )

  # ❌ WRONG - Will raise SQLAlchemy error
  memory.metadata = {"stressor": True}  # ← Don't do this!
  ```

**Key Architectural Decisions from Story 2.1:**
- **Vector Dimensions:** Vector(1536) for OpenAI text-embedding-3-small
- **HNSW Index Parameters:** m=16, ef_construction=64 (optimized for 1536-dim vectors)
- **Distance Metric:** Cosine distance (vector_cosine_ops) for semantic similarity
- **Metadata Storage:** JSONB column (`extra_data`) stores flexible data:
  - Stressor logging: `{stressor: true, emotion: 'fear', category: 'academic'}`
  - Goal tracking: `{goal_related: true, goal_id: uuid, priority: 'high'}`
  - Task context: `{task_id: uuid, status: 'in_progress', deadline: timestamp}`
- **Cascade Delete:** User deletion automatically removes all memories
- **LRU Tracking:** `accessed_at` timestamp enables future frequency-based ranking

**Why Story 2.5 Before 2.2 (Vertical Slice Approach):**
- Story 2.1 prepared for Story 2.2 (memory service extraction)
- But vertical slice approach validates memory patterns with working UI first
- Story 2.5 provides real-world usage data to inform Story 2.2 service design
- Learnings captured in Story 2.5 will feed into Story 2.2 architecture:
  - What metadata fields are actually useful?
  - What similarity threshold works best? (test different values)
  - How many memories to retrieve? (start with 5, may need tuning)
  - Do simple heuristics work for memory type detection?

**Migration Status:**
- Migration file created and verified (`alembic history` shows 002 → 003 chain)
- Ready to run: `poetry run alembic upgrade head`
- Database will be ready for Story 2.5 implementation

### Simple Eliza Agent (No LangGraph Yet)

**Decision: Use simple OpenAI streaming, not LangGraph**

**Why:**
- LangGraph adds complexity (state machine, nodes, edges)
- Don't need advanced agent features yet
- Story 2.3 will replace with full LangGraph agent

**Simple Agent Pattern:**
```python
class SimpleElizaAgent:
    async def generate_response(self, message, history, memories):
        system_prompt = self._build_system_prompt(memories)
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": message}
        ]
        # Stream response from OpenAI
        async for token in openai_stream(messages):
            yield token
```

**Story 2.3 will replace with:**
- LangGraph state machine
- Sophisticated memory retrieval strategies
- Emotion-aware response generation

### Memory Type Detection (Simple Heuristics)

**Heuristics for MVP:**
```python
def _detect_memory_type(message: str) -> MemoryType:
    # Stressors/venting → PERSONAL
    if 'overwhelmed' or 'stressed' or 'anxious' in message:
        return MemoryType.PERSONAL

    # Goals/plans → PROJECT
    if 'goal' or 'plan' or 'want to' in message:
        return MemoryType.PROJECT

    # Default → TASK
    return MemoryType.TASK
```

**Story 2.3 will improve with:**
- LLM-based classification (GPT-4o-mini)
- Context-aware detection
- User-specific patterns

### SSE Streaming Implementation

**Event Format:**
```json
// Token event
{"type": "token", "content": "I "}

// Complete event
{"type": "complete"}

// Error event
{"type": "error", "message": "Error description"}
```

**Backend Pattern:**
```python
async def event_generator():
    try:
        async for token in agent.generate_response(...):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

return StreamingResponse(
    event_generator(),
    media_type="text/event-stream"
)
```

**Frontend Pattern:**
```typescript
const eventSource = new EventSource('/api/v1/companion/stream/{id}?token={token}');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'token') {
        // Append token to message
    } else if (data.type === 'complete') {
        // Finish loading
    } else if (data.type === 'error') {
        // Show error
    }
};
```

### Test Scenarios (All Must Pass)

**Scenario 1: Venting**
```
User: "I'm overwhelmed with my schoolwork because I have to catch up"
→ Personal memory created with stressor metadata
→ Eliza: "I hear you're feeling overwhelmed with schoolwork..."
```

**Scenario 2: Goal Discussion**
```
User: "I want to work on my goal to graduate early"
→ Project memory created with goal metadata
→ Eliza: "That's an ambitious goal! Let's talk about..."
```

**Scenario 3: Memory Recall**
```
Message 1: "I'm stressed about class registration"
→ Memory stored

Message 2: "I'm feeling overwhelmed"
→ Query retrieves "class registration" memory
→ Eliza: "I remember you mentioned stress about class registration. Is this related?"
```

**Scenario 4: Task Update**
```
User: "I completed my walk today"
→ Task memory created
→ Eliza: "That's great! How did it feel?"
```

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Memory Query (p95)** | < 100ms | HNSW index from Story 2.1 |
| **Embedding Generation** | < 200ms | OpenAI API latency |
| **First Token (p95)** | < 1s | Streaming starts quickly |
| **UI Responsiveness** | < 50ms | User input feels instant |
| **SSE Connection Latency** | < 50ms | Low overhead streaming |

### Learnings to Capture (for Story 2.2)

**What to Document:**
- What metadata fields are actually useful?
- What similarity threshold works best? (default 0.7)
- How many memories to retrieve? (default 5)
- What memory types are most common?
- Do heuristics work for type detection?
- SSE connection stability issues?

**Feed into Story 2.2:**
- Hybrid search parameters tuning
- Service extraction patterns
- Memory pruning strategy
- Advanced features priorities

### Project Structure

**New Files Created:**
```
packages/backend/
├── app/
│   ├── api/v1/
│   │   └── companion.py               # NEW: Chat endpoints
│   ├── agents/
│   │   └── simple_eliza.py            # NEW: Simple agent (no LangGraph)
│   └── schemas/
│       └── companion.py               # NEW: Chat schemas

packages/frontend/
├── src/
│   ├── app/
│   │   └── companion/
│   │       └── page.tsx               # NEW: Companion chat page
│   ├── components/
│   │   └── companion/
│   │       ├── CompanionChat.tsx      # NEW: Main chat component
│   │       ├── MessageList.tsx        # NEW: Message list
│   │       ├── Message.tsx            # NEW: Individual message
│   │       ├── MessageInput.tsx       # NEW: Input component
│   │       └── LoadingIndicator.tsx   # NEW: Loading animation
│   └── lib/
│       └── hooks/
│           └── useChat.ts             # NEW: Chat hook with SSE
```

**Modified Files:**
```
packages/backend/
├── app/api/v1/__init__.py             # UPDATE: Register companion router

packages/frontend/
└── package.json                        # UPDATE: Add framer-motion
```

### Relationship to Epic 2 Stories

**This story (2.5) validates:**
- ✅ Memory storage patterns work
- ✅ Memory retrieval quality is good
- ✅ User interaction flow is smooth
- ✅ SSE streaming is performant

**This story enables:**
- **Story 2.2**: Extract memory service based on proven patterns
- **Story 2.3**: Replace simple agent with LangGraph
- **Story 2.6**: Add emotion detection to working system

**Dependencies Flow (Revised):**
```
Story 2.1 (Memory Schema) ✅
    ↓
Story 2.5 (Chat + Essential Memory) ← THIS STORY (vertical slice)
    ↓
Story 2.2 (Extract Memory Service) ← Refine based on 2.5 learnings
    ↓
Story 2.3 (Full Eliza Agent) ← Replace simple agent
    ↓
Story 2.4 (Enhanced Chat API) ← Add advanced features
    ↓
Story 2.6 (Emotion Detection) ← Integrate emotions
    = Production-Ready Companion! 🎉
```

### References

**Source Documents:**
- **Epic 2 Tech Spec**: `docs/tech-spec-epic-2.md` (Chat flow, SSE streaming)
- **Story 2.1**: `docs/stories/2-1-set-up-postgresql-pgvector-and-memory-schema.md` (Database foundation)
- **Story 1.3**: `docs/stories/1-3-integrate-clerk-authentication-system.md` (Auth patterns)
- **How Eliza Should Respond**: `docs/epic-2/1. How Eliza Should Respond (The Walkthrough).md` (Agent behavior)

**Technical Documentation:**
- **OpenAI Streaming**: https://platform.openai.com/docs/api-reference/streaming
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- **Framer Motion**: https://www.framer.com/motion/
- **EventSource API**: https://developer.mozilla.org/en-US/docs/Web/API/EventSource

---

## Definition of Done

- [ ] ✅ Chat UI displays and accepts messages
- [ ] ✅ SSE streaming displays tokens in real-time
- [ ] ✅ Conversation persists across page refreshes
- [ ] ✅ Venting scenario creates personal memory with stressor metadata
- [ ] ✅ Goal discussion creates project memory with goal metadata
- [ ] ✅ Memory retrieval works (second message references first)
- [ ] ✅ Mobile responsive design (works on <768px screens)
- [ ] ✅ Keyboard navigation fully functional
- [ ] ✅ Screen reader announces new messages
- [ ] ✅ All test scenarios passing (venting, goal, recall, task)
- [ ] ✅ Integration tests passing (backend + frontend)
- [ ] ✅ E2E tests passing (Playwright)
- [ ] ✅ Manual testing checklist 100% complete
- [ ] ✅ Documentation updated (setup guide, testing guide)
- [ ] ✅ Learnings documented for Story 2.2
- [ ] ✅ No secrets committed (API keys in .env only)
- [ ] ✅ Code follows async patterns (backend) and React best practices (frontend)
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline

- **Task 1** (Chat API Endpoints): 2 hours
- **Task 2** (Essential Memory Inline): 2.5 hours
- **Task 3** (Simple Eliza Agent): 1.5 hours
- **Task 4** (SSE Streaming): 1 hour
- **Task 5** (Chat UI Components): 3 hours
- **Task 6** (useChat Hook): 2 hours
- **Task 7** (Framer Motion): 1 hour
- **Task 8** (Mobile Responsive): 1 hour
- **Task 9** (Accessibility): 1 hour
- **Task 10** (Integration Testing): 2 hours
- **Task 11** (Documentation): 1 hour

**Total:** 18 hours → **Estimated 12-15 hours** with parallel work

### Risk Mitigation

**Risk:** OpenAI API failures during streaming
- **Mitigation**: Retry logic, error messages, graceful degradation
- **Impact**: Medium (conversation interrupted, but doesn't lose data)

**Risk:** SSE connections drop on mobile networks
- **Mitigation**: Auto-reconnect logic, HTTP fallback
- **Impact**: Medium (UX degradation, but functional)

**Risk:** Memory retrieval quality poor
- **Mitigation**: This story validates quality, can adjust similarity threshold
- **Impact**: Low (easy to tune in Story 2.2)

**Risk:** Chat UI feels slow/janky
- **Mitigation**: Optimize animations, test on devices
- **Impact**: Low (polish issue, not blocker)

### Future Enhancements (Post-Story)

After this story completes, Story 2.2 will add:
- [ ] Extract memory service (proper architecture)
- [ ] Hybrid search (time decay, frequency boost)
- [ ] Memory pruning worker
- [ ] Goal-based search enhancements
- [ ] User priority system
- [ ] Advanced features from Story 2.2 ACs 9-14

Story 2.3 will add:
- [ ] Replace simple agent with LangGraph state machine
- [ ] Advanced memory retrieval strategies
- [ ] Emotion-aware response generation

---

**Last Updated:** 2025-11-12 (Initial draft - vertical slice approach)
**Story Status:** drafted
**Next Steps:** Run `story-context` workflow to generate technical context XML → mark `ready-for-dev`

## Vertical Slice Success Criteria

This story succeeds if:
1. ✅ **Users can chat with Eliza** (functional UI + backend)
2. ✅ **Memory is stored** (venting, goals, tasks all create memories)
3. ✅ **Memory is retrieved** (second message shows context from first)
4. ✅ **All scenarios work** (can test manually in browser)
5. ✅ **Learnings captured** (know what to improve in Story 2.2)

**Goal:** Working chat with memory retrieval in ONE story, refine architecture in NEXT story.

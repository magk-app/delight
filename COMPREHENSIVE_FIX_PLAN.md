# Comprehensive Fix Plan - Experimental Chat Integration

**Created:** 2025-11-19
**Status:** Investigation Complete, Implementation In Progress

---

## 🎯 Executive Summary

This document outlines all identified issues with the experimental chat system and detailed solutions. The fixes address persistence, performance, UI consistency, and memory efficiency.

---

## 📋 Issues Identified

### 1. **User ID Persistence** ❌ CRITICAL
**Problem:**
- Each page refresh generates new UUID
- Memories created but not visible because user ID changes
- No way to login as specific user for testing

**Evidence:**
- User reports: "memory is not persistent across sessions"
- Backend logs show memories ARE being created
- Frontend shows "Total Memories: 0" because it's querying with new user ID

**Root Cause:**
- No localStorage persistence in MemoryVisualization, AnalyticsDashboard
- Each component generates own user ID
- No shared user state

---

### 2. **Light/Dark Mode Mismatch** ⚠️ HIGH
**Problem:**
- MemoryVisualization uses light theme (white bg, black text)
- AnalyticsDashboard uses light theme (white bg, black text)
- ChatInterface and main page use dark theme (slate-900 bg, white text)
- Inconsistent visual experience

**User Feedback:**
> "analytics and memory are in light mode while everything is in dark mode"

**Files Affected:**
- `MemoryVisualization.tsx` (lines 49-269: all white bg)
- `AnalyticsDashboard.tsx` (lines 22-207: all white bg)

---

### 3. **Chat Flow Performance** ⚠️ HIGH
**Problem:**
- Memory creation is blocking - response waits for fact extraction + categorization + embedding generation
- Current flow: Retrieve → Respond → Create memories (all synchronous)
- Users wait ~2-3 seconds for simple messages

**Current Code Flow** (`chat_api.py:128-180`):
```python
# Step 1: Retrieve memories (150ms)
relevant_memories = await memory_service.search_memories(...)

# Step 2: Generate response (800ms)
response = await openai.chat.completions.create(...)

# Step 3: Create memories (BLOCKING - 1500ms!)
created_memories = await memory_service.create_memory_from_message(
    extract_facts=True,      # LLM call: 600ms
    auto_categorize=True,     # LLM call: 400ms
    generate_embeddings=True, # OpenAI call: 300ms
    link_facts=True           # DB queries: 200ms
)

# Step 4: Commit and return (100ms)
await db.commit()
return response  # User waits 2.95 seconds total
```

**User's Request:**
> "you should retrieve memory, then get the ai response, then store memory afterwards, thats fine, so we  have faster response"

**Desired Flow:**
1. Retrieve memories (150ms)
2. Generate AI response (800ms)
3. **Return response immediately** ← User sees response in 950ms
4. Create memories in background (1500ms, user doesn't wait)

**Savings:** 1.5 seconds per message = 60% faster perceived response time

---

### 4. **Memory Batching/Efficiency** ❌ CRITICAL
**Problem:**
- Similar facts stored as separate memories (inefficient)
- Example: "favorite cuisine: Italian", "favorite cuisine: Japanese", "favorite cuisine: Thai" = 3 memories
- Should be: "favorite cuisines: [Italian, Japanese, Thai]" = 1 memory
- Wastes database space and makes search slower

**User Feedback:**
> "similar memory like favorite cuisine could have multiple values but you can't store them as 3 its too inefficient"

**Current Fact Extraction** (`fact_extractor.py:77-124`):
```
Input: "I love Italian, Japanese, and Thai food"

Current Output:
- Fact 1: "Likes Italian food" (type: preference)
- Fact 2: "Likes Japanese food" (type: preference)
- Fact 3: "Likes Thai food" (type: preference)

Desired Output:
- Fact 1: "Favorite cuisines: Italian, Japanese, Thai" (type: preference, multi_value: true)
```

**Solution Requirements:**
1. Detect similar facts (same attribute, different values)
2. Merge into single fact with array values
3. Update existing memory if similar fact already exists
4. Use structured format for multi-value facts

---

### 5. **Fact Extraction Format** ⚠️ MEDIUM
**Problem:**
- Facts extracted in natural language: "Prefers TypeScript over JavaScript"
- No structured format for programmatic querying
- Hard to update values (have to parse natural language)

**User Request:**
> "find a way to extract the facts quicker using a llm to process the message and always give a list in a similar format"

**Current Format:**
```json
{
  "content": "Prefers TypeScript over JavaScript",
  "fact_type": "preference"
}
```

**Desired Format:**
```json
{
  "attribute": "preferred_language",
  "values": ["TypeScript"],
  "context": "prefers over JavaScript",
  "fact_type": "preference",
  "multi_value": false
}
```

**Benefits:**
- Easy to merge facts with same attribute
- Programmatic updates (append to values array)
- Better deduplication
- Structured queries

---

### 6. **Chat History Persistence** ❌ CRITICAL
**Problem:**
- Chat history only in frontend state (lost on refresh)
- No database storage of conversation messages
- Can't view past conversations
- Can't resume conversations
- Can't analyze conversation patterns

**User Feedback:**
> "there is no persistent way to store chatHistory so that would need to be implemented as well, because its important to be able to see past history and cross history stuff as well"

**Current State:**
- `conversation_history` passed from frontend in each request
- Lives in React state: `const [messages, setMessages] = useState<Message[]>([...])`
- Reset on page refresh

**Needed:**
1. Database schema for chat messages
2. API endpoint to load conversation history
3. Frontend to load history on mount
4. Conversation list UI
5. Session/conversation management

---

### 7. **Mock Analytics Data** ⚠️ HIGH
**Problem:**
- Token usage shows mock data
- Not tracking real OpenAI API costs
- Can't monitor actual usage

**User Feedback:**
> "the token is still mocked wtf"

**Current Code** (`AnalyticsDashboard.tsx:62-68`):
```tsx
<StatCard
  title="Total Tokens"
  value={usage?.total_tokens?.toLocaleString() || '0'}  // Mock: 15,000
  icon="📊"
  color="cyan"
/>
<StatCard
  title="Total Cost"
  value={`$${usage?.total_cost?.toFixed(4) || '0.00'}`}  // Mock: $0.0230
  icon="💰"
  color="green"
/>
```

**Needed:**
1. Track token usage in database after each OpenAI call
2. Store model, prompt_tokens, completion_tokens, cost
3. API endpoint to aggregate usage stats
4. Real-time cost calculation

---

### 8. **Memory Management UI** ⚠️ MEDIUM
**Problem:**
- Can delete individual memories (✓)
- Cannot edit memories (❌)
- Cannot clear all memories for user (❌)
- No bulk operations

**User Feedback:**
> "nor can you clear the memory for the user, you should be able to edit or delete memories"

**Current State:**
- Delete button exists in `MemoryVisualization.tsx:239-245`
- Uses emoji trash icon (🗑️) - should be Lucide icon
- No edit functionality
- No "Clear All" button

---

### 9. **User Switching for Testing** ⚠️ MEDIUM
**Problem:**
- No way to switch between test users
- Have to clear localStorage manually
- No user management UI

**User Feedback:**
> "find a way to create a way to be able to login to specific users, or create new users in someways, i don't mind security because this is just testing as well"

**Needed:**
1. User switcher dropdown in header
2. "New User" button (generates new UUID)
3. Recent users list (stored in localStorage)
4. Current user display

---

## 🔧 Detailed Solutions

### Solution 1: User ID Persistence (Frontend)

**Files to Modify:**
1. `ChatInterface.tsx` - Refactor to use `usePersistentUser` hook
2. `MemoryVisualization.tsx` - Add hook, convert to dark theme
3. `AnalyticsDashboard.tsx` - Add hook, convert to dark theme
4. `experimental/page.tsx` - Pass userId to all components

**Implementation:**

```tsx
// packages/frontend/src/app/experimental/page.tsx
export default function ExperimentalPage() {
  const { userId, isLoading, clearUser } = usePersistentUser();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <>
      {activeTab === 'chat' && <ChatInterface userId={userId} />}
      {activeTab === 'memories' && <MemoryVisualization userId={userId} />}
      {activeTab === 'analytics' && <AnalyticsDashboard userId={userId} />}
    </>
  );
}
```

```tsx
// packages/frontend/src/components/experimental/ChatInterface.tsx
export function ChatInterface({ userId }: { userId: string }) {
  // Remove inline localStorage logic
  // Use userId prop directly
  const response = await experimentalAPI.sendChatMessage({
    message: userMessage.content,
    user_id: userId,
    conversation_history: conversationHistory,
  });
}
```

**Time Estimate:** 1 hour

---

### Solution 2: Dark Theme Conversion

**Color Palette:**
```css
/* Current (Light Theme) */
bg-white → bg-slate-900/80
text-gray-800 → text-white
text-gray-600 → text-slate-400
border-gray-300 → border-slate-700/50

/* Glassmorphism Effects */
backdrop-blur-xl
shadow-2xl
border border-slate-700/50
```

**Files to Update:**
- `MemoryVisualization.tsx` (269 lines)
- `AnalyticsDashboard.tsx` (207 lines)

**Icons to Replace:**
- 🔄 → `<RefreshCw className="w-4 h-4" />`
- 📝 → `<List className="w-4 h-4" />`
- 🕸️ → `<Network className="w-4 h-4" />`
- 🗑️ → `<Trash2 className="w-4 h-4" />`
- 🧠 → `<Brain className="w-4 h-4" />`
- 📊 → `<BarChart3 className="w-4 h-4" />`
- 💰 → `<DollarSign className="w-4 h-4" />`

**Time Estimate:** 2 hours

---

### Solution 3: Async Memory Processing (Backend)

**Approach: FastAPI Background Tasks**

```python
from fastapi import BackgroundTasks

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, background_tasks: BackgroundTasks):
    """Send message with fast response, memory processing in background"""

    user_id = UUID(request.user_id) if request.user_id else uuid4()

    async with AsyncSessionLocal() as db:
        # Step 1: Ensure user exists
        await chat_service._ensure_user_exists(user_id, db)

        # Step 2: Retrieve memories (keep for context)
        relevant_memories = await memory_service.search_memories(
            user_id=user_id,
            query=request.message,
            db=db,
            limit=5
        )

        # Step 3: Generate AI response
        response = await chat_service.generate_response(
            message=request.message,
            memories=relevant_memories,
            history=request.conversation_history
        )

        # Step 4: Return response immediately
        result = ChatResponse(
            response=response.content,
            memories_retrieved=[...],
            memories_created=[],  # Empty - processing in background
            timestamp=datetime.now().isoformat()
        )

        # Step 5: Process memories in background (non-blocking)
        background_tasks.add_task(
            process_memories_async,
            user_id=user_id,
            message=request.message,
            response=response.content
        )

        return result

async def process_memories_async(user_id: UUID, message: str, response: str):
    """Background task for memory processing"""
    async with AsyncSessionLocal() as db:
        try:
            await memory_service.create_memory_from_message(
                user_id=user_id,
                message=message,
                memory_type=MemoryType.PERSONAL,
                db=db,
                extract_facts=True,
                auto_categorize=True,
                generate_embeddings=True
            )
            await db.commit()
        except Exception as e:
            print(f"Background memory processing error: {e}")
            await db.rollback()
```

**Benefits:**
- Response time: 2950ms → 950ms (68% faster)
- User sees response immediately
- Memory processing doesn't block
- Errors in background task don't crash request

**Tradeoffs:**
- `memories_created` field will be empty in response
- Need to refresh memory browser to see new memories
- Can add WebSocket notification when memories ready

**Time Estimate:** 2 hours

---

### Solution 4: Chat History Persistence (Backend + Frontend)

**Database Schema:**

```sql
-- New table for chat messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,  -- memories_retrieved, memories_created, etc.
    INDEX idx_conversation_messages (conversation_id, created_at),
    INDEX idx_user_messages (user_id, created_at)
);

-- New table for conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),  -- Auto-generated from first message
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    INDEX idx_user_conversations (user_id, updated_at DESC)
);
```

**API Endpoints:**

```python
@router.get("/conversations")
async def list_conversations(user_id: str):
    """Get all conversations for user"""
    ...

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get all messages in a conversation"""
    ...

@router.post("/conversations")
async def create_conversation(user_id: str):
    """Create new conversation"""
    ...

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation and all messages"""
    ...
```

**Frontend Changes:**

```tsx
// Load conversation on mount
useEffect(() => {
  const loadConversation = async () => {
    const convId = searchParams.get('conversation_id');
    if (convId) {
      const messages = await experimentalAPI.getConversationMessages(convId);
      setMessages(messages);
      setConversationId(convId);
    } else {
      // Create new conversation
      const newConv = await experimentalAPI.createConversation(userId);
      setConversationId(newConv.id);
    }
  };
  loadConversation();
}, [userId]);

// Save each message to DB
const handleSendMessage = async () => {
  // ... send to API ...

  // Save user message
  await experimentalAPI.saveMessage({
    conversation_id: conversationId,
    role: 'user',
    content: userMessage.content
  });

  // Save assistant message
  await experimentalAPI.saveMessage({
    conversation_id: conversationId,
    role: 'assistant',
    content: response.response,
    metadata: {
      memories_retrieved: response.memories_retrieved,
      memories_created: response.memories_created
    }
  });
};
```

**UI for Conversation List:**
- Sidebar with recent conversations
- Click to load conversation
- "New Chat" button
- Auto-generate titles from first message

**Time Estimate:** 4 hours

---

### Solution 5: Memory Batching & Deduplication (Backend)

**Enhanced Fact Extraction:**

```python
class ExtractedFactV2(BaseModel):
    """Enhanced fact with structured attributes"""
    attribute: str = Field(description="The attribute name (e.g., 'favorite_cuisine', 'programming_language')")
    values: List[str] = Field(description="List of values for this attribute")
    context: Optional[str] = Field(description="Additional context or comparison")
    fact_type: str = Field(description="Category of fact")
    confidence: float = Field(ge=0.0, le=1.0)

# New system prompt
SYSTEM_PROMPT_V2 = """Extract facts with structured attributes.

For multi-value facts, group them together:

Input: "I love Italian, Japanese, and Thai food"
Output:
{
  "attribute": "favorite_cuisines",
  "values": ["Italian", "Japanese", "Thai"],
  "fact_type": "preference",
  "confidence": 0.95
}

Input: "I know Python, JavaScript, and Go"
Output:
{
  "attribute": "programming_languages",
  "values": ["Python", "JavaScript", "Go"],
  "fact_type": "skill",
  "confidence": 0.98
}
```

**Deduplication Logic:**

```python
async def merge_or_create_memory(
    self,
    user_id: UUID,
    new_fact: ExtractedFactV2,
    db: AsyncSession
) -> Memory:
    """Merge fact with existing memory or create new one"""

    # Search for existing memory with same attribute
    existing = await db.execute(
        select(Memory)
        .where(Memory.user_id == user_id)
        .where(Memory.content.like(f"%{new_fact.attribute}%"))
        .order_by(Memory.created_at.desc())
        .limit(1)
    )
    existing_memory = existing.scalar_one_or_none()

    if existing_memory and self._is_similar_fact(existing_memory, new_fact):
        # Merge values
        existing_values = existing_memory.extra_data.get("values", [])
        new_values = list(set(existing_values + new_fact.values))

        existing_memory.extra_data["values"] = new_values
        existing_memory.content = f"{new_fact.attribute}: {', '.join(new_values)}"
        existing_memory.updated_at = datetime.utcnow()

        return existing_memory
    else:
        # Create new memory
        return Memory(
            user_id=user_id,
            content=f"{new_fact.attribute}: {', '.join(new_fact.values)}",
            memory_type=MemoryType.PERSONAL,
            extra_data={
                "attribute": new_fact.attribute,
                "values": new_fact.values,
                "multi_value": True
            }
        )
```

**Time Estimate:** 6 hours

---

### Solution 6: Real Token Tracking (Backend)

**Database Schema:**

```sql
CREATE TABLE token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    model VARCHAR(50) NOT NULL,
    operation VARCHAR(50) NOT NULL,  -- 'chat', 'fact_extraction', 'categorization', 'embedding'
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    INDEX idx_user_usage (user_id, created_at),
    INDEX idx_model_usage (model, created_at)
);
```

**Tracking Service:**

```python
class TokenTracker:
    """Track OpenAI token usage and costs"""

    # Pricing (as of 2025)
    PRICING = {
        "gpt-4o-mini": {
            "prompt": 0.150 / 1_000_000,  # $0.150 per 1M input tokens
            "completion": 0.600 / 1_000_000  # $0.600 per 1M output tokens
        },
        "text-embedding-3-small": {
            "prompt": 0.020 / 1_000_000,  # $0.020 per 1M tokens
            "completion": 0.0
        }
    }

    async def track_usage(
        self,
        user_id: UUID,
        model: str,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int,
        db: AsyncSession
    ):
        """Track token usage to database"""
        total_tokens = prompt_tokens + completion_tokens

        pricing = self.PRICING.get(model, {"prompt": 0, "completion": 0})
        cost = (
            prompt_tokens * pricing["prompt"] +
            completion_tokens * pricing["completion"]
        )

        usage = TokenUsage(
            user_id=user_id,
            model=model,
            operation=operation,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost
        )

        db.add(usage)
        await db.flush()

        return cost

# Use in chat service
response = await self.openai.chat.completions.create(...)
await token_tracker.track_usage(
    user_id=user_id,
    model=self.config.chat_model,
    operation="chat",
    prompt_tokens=response.usage.prompt_tokens,
    completion_tokens=response.usage.completion_tokens,
    db=db
)
```

**Analytics Endpoint:**

```python
@router.get("/analytics/token-usage")
async def get_token_usage(
    user_id: Optional[str] = None,
    hours: int = 24
):
    """Get token usage statistics"""

    since = datetime.utcnow() - timedelta(hours=hours)

    query = select(
        TokenUsage.model,
        func.sum(TokenUsage.total_tokens).label("tokens"),
        func.sum(TokenUsage.cost_usd).label("cost")
    ).where(TokenUsage.created_at >= since)

    if user_id:
        query = query.where(TokenUsage.user_id == UUID(user_id))

    query = query.group_by(TokenUsage.model)

    result = await db.execute(query)

    return {
        "by_model": {
            row.model: {"tokens": row.tokens, "cost": float(row.cost)}
            for row in result
        },
        "total_tokens": sum(row.tokens for row in result),
        "total_cost": sum(row.cost for row in result)
    }
```

**Time Estimate:** 3 hours

---

### Solution 7: User Switching UI (Frontend)

**Component:**

```tsx
function UserSwitcher({ currentUserId, onUserChange }: Props) {
  const [recentUsers, setRecentUsers] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    // Load recent users from localStorage
    const recent = JSON.parse(localStorage.getItem('recent_users') || '[]');
    setRecentUsers(recent);
  }, []);

  const switchToUser = (userId: string) => {
    localStorage.setItem('experimental_user_id', userId);
    onUserChange(userId);

    // Update recent users
    const updated = [userId, ...recentUsers.filter(id => id !== userId)].slice(0, 5);
    localStorage.setItem('recent_users', JSON.stringify(updated));
    setRecentUsers(updated);
  };

  const createNewUser = () => {
    const newId = crypto.randomUUID();
    switchToUser(newId);
  };

  return (
    <div className="relative">
      <button onClick={() => setShowDropdown(!showDropdown)}>
        <User className="w-4 h-4" />
        <span>{currentUserId.slice(0, 8)}...</span>
        <ChevronDown className="w-4 h-4" />
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-xl">
          <div className="p-2">
            <div className="text-xs text-slate-400 mb-2">Current User</div>
            <div className="font-mono text-xs text-white">{currentUserId}</div>
          </div>

          {recentUsers.length > 0 && (
            <>
              <div className="border-t border-slate-700 p-2">
                <div className="text-xs text-slate-400 mb-2">Recent Users</div>
                {recentUsers.map(userId => (
                  <button
                    key={userId}
                    onClick={() => switchToUser(userId)}
                    className="w-full text-left px-2 py-1 text-xs font-mono hover:bg-slate-700 rounded"
                  >
                    {userId.slice(0, 8)}...
                  </button>
                ))}
              </div>
            </>
          )}

          <div className="border-t border-slate-700 p-2">
            <button
              onClick={createNewUser}
              className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 rounded text-sm font-medium"
            >
              + New User
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Time Estimate:** 2 hours

---

## 📊 Implementation Priority

### Phase 1: Critical Fixes (High Impact, User Blocking)
1. ✅ User ID persistence (1 hour)
2. ✅ Dark theme conversion (2 hours)
3. ⏳ User switching UI (2 hours)

**Total: 5 hours**

### Phase 2: Performance & UX (High Impact, Quality)
4. ⏳ Async memory processing (2 hours)
5. ⏳ Chat history persistence (4 hours)

**Total: 6 hours**

### Phase 3: Data Quality (Medium Impact, Long Term)
6. ⏳ Memory batching/deduplication (6 hours)
7. ⏳ Real token tracking (3 hours)
8. ⏳ Memory edit UI (2 hours)

**Total: 11 hours**

---

## ✅ Implementation Checklist

### Frontend (9 hours)
- [ ] Refactor ChatInterface to use usePersistentUser hook
- [ ] Convert MemoryVisualization to dark theme + add hook
- [ ] Convert AnalyticsDashboard to dark theme + add hook
- [ ] Add UserSwitcher component to experimental page header
- [ ] Add conversation list sidebar
- [ ] Load chat history from database on mount
- [ ] Save messages to database after each interaction
- [ ] Update AnalyticsDashboard to show real token data
- [ ] Add memory edit modal/inline editing
- [ ] Add "Clear All Memories" button with confirmation

### Backend (13 hours)
- [ ] Migrate chat API to use FastAPI BackgroundTasks
- [ ] Create ChatMessage and Conversation models
- [ ] Create Alembic migration for chat_messages and conversations tables
- [ ] Implement conversation CRUD endpoints
- [ ] Implement message storage/retrieval endpoints
- [ ] Create TokenUsage model
- [ ] Create Alembic migration for token_usage table
- [ ] Implement TokenTracker service
- [ ] Track tokens in chat, fact extraction, categorization, embedding calls
- [ ] Create token usage analytics endpoint
- [ ] Enhance fact extractor to use structured attributes
- [ ] Implement merge_or_create_memory deduplication logic
- [ ] Add memory update endpoint

### Testing (2 hours)
- [ ] Test user persistence across page refreshes
- [ ] Test user switching functionality
- [ ] Verify async memory processing doesn't block responses
- [ ] Test chat history loads correctly
- [ ] Test conversation creation and switching
- [ ] Verify token tracking accuracy
- [ ] Test memory merging with multi-value facts
- [ ] Test memory edit and delete

---

## 🚀 Getting Started

Start with Phase 1 (Critical Fixes) to unblock user immediately. This fixes:
1. User can see their memories persist
2. Consistent dark theme experience
3. Easy user switching for testing

Phase 2 improves performance and adds critical features.
Phase 3 improves long-term data quality and analytics.

---

**Total Estimated Time:** 24 hours (3 working days)
**Priority:** Start immediately with Phase 1

# Coding Tips for Improving AI Agent Responses

**Date:** 2025-11-12  
**Purpose:** Best practices for getting better code generation from AI agents (Claude, GPT-4, etc.)

---

## 1. Context Management

### ✅ DO: Provide Comprehensive Context

**Bad:**
```
"Add a function to query memories"
```

**Good:**
```
"Add a function to query memories in the MemoryService class. 
The function should:
- Use the existing MemoryService.query_memories() method
- Filter by memory_type (personal/project/task)
- Support goal-based search when goal keywords detected
- Return List[Memory] objects
- Follow async/await patterns from Story 2.2"
```

### ✅ DO: Reference Existing Code

**Good:**
```
"Following the pattern from Story 2.1's migration file (003_create_memory_tables.py),
create a similar migration for adding indexes to the conversations table."
```

### ✅ DO: Include File Paths and Line Numbers

**Good:**
```
"In packages/backend/app/services/memory_service.py around line 250,
update the query_memories() method to support goal-based search."
```

---

## 2. Specificity and Clarity

### ✅ DO: Be Specific About Requirements

**Bad:**
```
"Make it better"
```

**Good:**
```
"Improve error handling in the embedding generation:
- Add retry logic with exponential backoff (3 attempts)
- Log errors with user_id and content preview
- Return None if all retries fail (don't raise exception)
- Follow the error handling pattern from Story 2.2 AC6"
```

### ✅ DO: Provide Examples

**Good:**
```
"Add a method calculate_user_priorities() that returns:
{
    'value_weights': {'health': 0.3, 'learning': 0.4, ...},
    'push_factors': ['achievement', 'growth'],
    'current_context': {'emotion': 'overwhelm', 'stress': 'high'},
    'recommendations': {'prioritize': 'well-being', 'defer': 'learning'}
}

Example usage:
priority_profile = await service.calculate_user_priorities(
    user_id, 
    current_emotion='overwhelm',
    stress_level='high'
)
assert priority_profile['value_weights']['health'] > 0.3
```

---

## 3. Architecture and Patterns

### ✅ DO: Reference Architecture Decisions

**Good:**
```
"Following the 3-tier memory architecture from Story 2.2:
- Personal tier: Always queried (top 5)
- Project tier: Queried when goal keywords detected
- Task tier: Recent context (top 3)

Implement the recall_context node in ElizaAgent to use this pattern."
```

### ✅ DO: Specify Patterns to Follow

**Good:**
```
"Use async SQLAlchemy 2.0 patterns throughout:
- async with get_db() as db: ...
- await db.execute(select(...))
- await db.commit()

Follow the pattern from Story 2.1's memory models."
```

---

## 4. Error Handling and Edge Cases

### ✅ DO: Specify Error Handling Requirements

**Good:**
```
"Handle the following error cases:
1. OpenAI API failure: Retry 3 times with exponential backoff, then store memory without embedding
2. Database connection failure: Log error, return empty list (don't crash)
3. Invalid user_id: Raise HTTPException(404, 'User not found')
4. Empty query_text: Return empty list (don't query all memories)

Follow the error handling pattern from Story 2.2 AC6."
```

### ✅ DO: Mention Edge Cases

**Good:**
```
"Handle edge cases:
- Empty memory list: Return empty list, don't crash
- access_count = 0: Use 1 for frequency boost calculation
- days_since_access < 0: Use 0 for time boost calculation
- Similarity threshold too high: Return empty list with warning log"
```

---

## 5. Testing Requirements

### ✅ DO: Specify Test Requirements

**Good:**
```
"Add unit tests for the new method:
- Test with valid inputs
- Test with invalid inputs (edge cases)
- Test error handling (mock OpenAI API failure)
- Mock MemoryService for isolation
- Target: 80%+ coverage

Create test file: packages/backend/tests/services/test_memory_service.py"
```

### ✅ DO: Provide Test Examples

**Good:**
```
"Add integration test for case study scenario:
- Create memories: 'I'm overwhelmed with schoolwork', 'Family issue', etc.
- Query with: 'I'm overwhelmed with schoolwork'
- Verify: Top 3 results include overwhelm/schoolwork related memories

See Story 2.2 AC10 for test scenarios."
```

---

## 6. Code Style and Conventions

### ✅ DO: Reference Style Guides

**Good:**
```
"Follow Python style conventions:
- Use snake_case for functions and variables
- Use PascalCase for classes
- Add type hints for all function parameters and returns
- Use async/await for database operations
- Follow PEP 8 with 4-space indentation

See docs/dev/CONTRIBUTING.md for style guide."
```

### ✅ DO: Specify Naming Conventions

**Good:**
```
"Use these naming conventions:
- Service methods: query_memories(), add_memory(), prune_old_task_memories()
- Helper methods: _calculate_time_boost(), _detect_goal_keywords() (private)
- Constants: MEMORY_SIMILARITY_THRESHOLD, EMBEDDING_DIMENSIONS
- Variables: memory_service, user_id, query_text"
```

---

## 7. Dependencies and Integration

### ✅ DO: Specify Dependencies

**Good:**
```
"This feature depends on:
- Story 2.2: MemoryService must be implemented
- OpenAI API key configured (OPENAI_API_KEY env var)
- PostgreSQL with pgvector extension enabled
- ARQ worker infrastructure for background jobs

See Story 2.2 dependencies section."
```

### ✅ DO: Mention Integration Points

**Good:**
```
"Integrate with:
- MemoryService.query_memories() for context retrieval
- EmotionService.detect_emotion() for emotional state (Story 2.6)
- User model for user preferences and priority profile
- Conversation model for message persistence"
```

---

## 8. Performance and Optimization

### ✅ DO: Specify Performance Requirements

**Good:**
```
"Performance targets:
- Memory query: < 100ms (p95)
- Embedding generation: < 200ms
- LLM first token: < 1s
- Full response: < 5s

Optimize by:
- Using HNSW index for vector search
- Caching embeddings by content hash
- Limiting conversation history to last 10 messages
- Batch updating access tracking"
```

---

## 9. Documentation Requirements

### ✅ DO: Specify Documentation Needs

**Good:**
```
"Add documentation:
- Comprehensive docstrings for all methods (Google style)
- Inline comments for complex algorithms (hybrid search scoring)
- Usage examples in docstrings
- Update API-TESTING-GUIDE.md with examples
- Document in architecture docs

See Story 2.2 Task 14 for documentation requirements."
```

---

## 10. Incremental Development

### ✅ DO: Break Down Large Tasks

**Bad:**
```
"Build the entire Eliza agent"
```

**Good:**
```
"Build Eliza agent incrementally:

1. First: Create basic LangGraph structure with 5 nodes (no memory integration)
2. Second: Add memory integration to recall_context node
3. Third: Add emotional intelligence to system prompt
4. Fourth: Add streaming support
5. Fifth: Add memory storage to store_memory node

Test after each step."
```

---

## 11. Code Review and Quality

### ✅ DO: Specify Review Criteria

**Good:**
```
"Before marking as done, ensure:
- All acceptance criteria met (AC1-AC14)
- Unit tests passing (80%+ coverage)
- Integration tests passing
- Code follows style guide
- No secrets committed
- Documentation updated
- Story status updated in sprint-status.yaml

See Story 2.2 Definition of Done."
```

---

## 12. Common Patterns for This Project

### ✅ DO: Use Project-Specific Patterns

**Good:**
```
"Follow Delight project patterns:
- Services in app/services/ (business logic)
- Agents in app/agents/ (LangGraph agents)
- Models in app/models/ (SQLAlchemy)
- Schemas in app/schemas/ (Pydantic)
- API endpoints in app/api/v1/ (FastAPI routes)
- Workers in app/workers/ (ARQ background jobs)

See docs/architecture/implementation-patterns.md"
```

---

## 13. Prompt Engineering Tips

### ✅ DO: Use Structured Prompts

**Good:**
```
"Task: Implement goal-based memory search

Context:
- Story 2.2 AC9: Goal-based search requirements
- MemoryService.query_memories() exists at line 250
- Goal keywords: ['goal', 'goals', 'plan', 'plans', 'objective', 'target']

Requirements:
1. Add _detect_goal_keywords() helper method
2. Update query_memories() to auto-include PROJECT tier when keywords detected
3. Add goal_id filtering support
4. Add unit tests

Acceptance Criteria:
- AC9: Goal-based search works correctly
- Tests pass with goal-related queries

Files to modify:
- packages/backend/app/services/memory_service.py
- packages/backend/tests/services/test_memory_service.py"
```

---

## 14. Debugging and Troubleshooting

### ✅ DO: Provide Debugging Context

**Good:**
```
"If you encounter issues:
- Check Story 2.2 Dev Notes for implementation details
- Verify MemoryService is initialized correctly
- Check OpenAI API key is configured
- Review hybrid search algorithm in tech-spec-epic-2.md
- Test with case study scenarios from AC10

Common issues:
- Embedding generation fails → Check API key, retry logic
- Memory query slow → Check HNSW index created
- Goal keywords not detected → Check keyword list matches AC9"
```

---

## 15. Iterative Refinement

### ✅ DO: Request Iterative Improvements

**Good:**
```
"First iteration: Basic implementation
- Get it working end-to-end
- Don't worry about optimization yet

Second iteration: Optimize
- Add caching
- Improve error handling
- Add logging

Third iteration: Polish
- Add comprehensive tests
- Update documentation
- Code review feedback"
```

---

## Summary: The Perfect Prompt Template

```
Task: [Specific task description]

Context:
- Related Story: [Story ID and key requirements]
- Existing Code: [File paths and line numbers]
- Dependencies: [What must exist first]

Requirements:
1. [Specific requirement 1]
2. [Specific requirement 2]
3. [Specific requirement 3]

Implementation Details:
- Pattern to follow: [Reference existing code]
- Error handling: [Specific error cases]
- Performance: [Target metrics]

Testing:
- Unit tests: [What to test]
- Integration tests: [End-to-end scenarios]
- Coverage target: [Percentage]

Files:
- Create: [New files]
- Modify: [Existing files]

Acceptance Criteria:
- [AC reference or specific criteria]

Example:
[Code example or usage example]
```

---

## Quick Reference: What Makes a Good Prompt

✅ **Comprehensive**: Includes all necessary context  
✅ **Specific**: Clear requirements, not vague  
✅ **Referenced**: Points to existing code/docs  
✅ **Structured**: Organized with sections  
✅ **Testable**: Includes test requirements  
✅ **Incremental**: Can be built step-by-step  
✅ **Pattern-Aware**: Follows project conventions  

❌ **Vague**: "Make it better"  
❌ **Missing Context**: No file paths or references  
❌ **Too Broad**: "Build everything"  
❌ **No Examples**: Hard to understand intent  
❌ **No Tests**: Unclear how to verify  

---

**Remember**: The better your prompt, the better the code. Invest time in writing clear, comprehensive prompts—it pays off in code quality and reduces back-and-forth iterations.


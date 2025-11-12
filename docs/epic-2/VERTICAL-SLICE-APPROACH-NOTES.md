# Vertical Slice Approach: Story Order Revision (2025-11-12)

## Decision: Build Story 2.5 Before Story 2.2

**Date:** 2025-11-12
**Decision Maker:** Jack + Claude
**Status:** Approved

---

## Context

Originally planned to build:
1. Story 2.1: Database (✅ DONE)
2. Story 2.2: Memory Service (infrastructure)
3. Story 2.5: Chat UI (user-facing)

This follows **horizontal layering** (build infrastructure, then UI).

## Problem with Original Approach

**Can't validate memory works without UI:**
- Memory service built blindly (no visual feedback)
- Can't test real user scenarios (venting, tasks, memory recall)
- Unit tests don't capture UX quality
- Hard to iterate on hybrid search parameters
- Discover issues late (after building architecture)

**Story 2.2 became too comprehensive:**
- 14 acceptance criteria (normally 4-7)
- Advanced features (user priority system, universal factors)
- No way to manually test until Story 2.5 exists
- High risk of building wrong thing

## Solution: Vertical Slice Pattern

**Build Story 2.5 FIRST (vertical slice):**
- Working chat UI with SSE streaming
- Essential memory operations **inline** (not extracted service yet)
- Basic semantic search (vector similarity only, no hybrid yet)
- All test scenarios working end-to-end

**Then refactor Story 2.2 (extract and enhance):**
- Extract proven memory operations into proper service
- Add hybrid search based on Story 2.5 learnings
- Add pruning worker
- Advanced features (may move to Story 2.2b)

## Benefits

✅ **Immediate Validation**: See memory working in browser, not just tests
✅ **Real User Testing**: Test all scenarios (venting, tasks, recall) immediately
✅ **Fast Feedback Loop**: Discover what hybrid search parameters actually need
✅ **Lower Risk**: Fail fast on UX issues before building complex architecture
✅ **Motivating Progress**: Functional chat beats infrastructure building

## Revised Story Sequence

1. **Story 2.1**: Database foundation (pgvector, memory tables) ✅ COMPLETE
2. **Story 2.5**: Chat UI + Essential Memory ← DO THIS FIRST
   - Working chat you can test
   - Memory storage patterns proven
   - Search quality validated
3. **Story 2.2**: Memory Service Extraction ← DO THIS SECOND
   - Extract from 2.5
   - Add hybrid search
   - Add pruning
   - Optimize based on learnings
4. **Story 2.3**: Full Eliza Agent (LangGraph)
5. **Story 2.4**: Enhanced Chat API
6. **Story 2.6**: Emotion Detection

## Story 2.5 Scope (Vertical Slice)

### Included (Essential for Validation):
- ✅ Chat UI with SSE streaming
- ✅ Simple Eliza agent (basic prompt, no LangGraph yet)
- ✅ Essential memory operations (inline):
  - Store conversations as memories
  - Query memories with semantic search
  - Show retrieved memories in responses
- ✅ All test scenarios:
  - Venting → personal memory
  - Creating task → task memory
  - Memory recall → second message references first

### Deferred to Story 2.2:
- ❌ Memory service extraction
- ❌ Hybrid search (time decay, frequency boost)
- ❌ Memory pruning worker
- ❌ Goal-based search
- ❌ User priority system
- ❌ Advanced features (ACs 9-14 from original 2.2 draft)

## Story 2.2 Refactoring (After 2.5)

Story 2.2 will be **simplified and refocused**:

**New Focus:**
- Extract memory operations from Story 2.5 into proper service
- Add hybrid search based on what Story 2.5 reveals we need
- Add pruning worker
- Optimize performance based on real usage patterns

**Original ACs 9-14 (Advanced Features):**
- May move to Story 2.2b (separate story)
- Or defer to later epic (if not needed for MVP)
- Decision based on Story 2.5 learnings

## Learnings to Capture from Story 2.5

**For Story 2.2 refinement:**
- What metadata fields are actually useful?
- What similarity threshold works best? (default 0.7)
- How many memories to retrieve? (default 5)
- What memory types are most common?
- Do heuristics work for type detection?
- SSE connection stability issues?
- Performance bottlenecks?

**Feed into Story 2.2:**
- Hybrid search parameters tuning
- Service extraction patterns
- Memory pruning strategy
- Advanced features priorities

## Success Criteria

**Story 2.5 succeeds if:**
1. ✅ Users can chat with Eliza (functional UI + backend)
2. ✅ Memory is stored (venting, goals, tasks all create memories)
3. ✅ Memory is retrieved (second message shows context from first)
4. ✅ All scenarios work (can test manually in browser)
5. ✅ Learnings captured (know what to improve in Story 2.2)

**Story 2.2 succeeds if:**
1. ✅ Memory service extracted with clean architecture
2. ✅ Hybrid search improves retrieval quality
3. ✅ Pruning worker maintains database performance
4. ✅ All Story 2.5 tests still pass (no regressions)

## References

- **Story 2.5**: `docs/stories/2-5-companion-chat-ui-with-essential-memory.md`
- **Story 2.2**: `docs/stories/2-2-implement-memory-service-with-3-tier-architecture.md` (needs refactoring)
- **Tech Spec**: `docs/tech-spec-epic-2.md` (updated with vertical slice approach)

---

**Decision Status:** ✅ APPROVED
**Next Action:** Implement Story 2.5 first, capture learnings, then refactor Story 2.2

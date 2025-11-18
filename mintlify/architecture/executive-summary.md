---
title: Executive Summary
description: High-level overview of Delight's architecture and design principles
---

# Executive Summary

Delight is a self-improvement companion platform that blends emotionally-aware AI coaching with narrative world-building. The architecture is designed to support a **living narrative engine** where real-world goal achievement drives personalized story progression, multi-character AI interactions, and adaptive quest systems. The system prioritizes **premium AI experience** with a target operational cost of **$0.50/user/day** (pricing: $1/day subscription + pay-as-you-go for premium features).

## Key Architectural Approach

- **Frontend:** Next.js 15 + React 19 for modern, performant UI with streaming support
- **Backend:** FastAPI for async-first API layer optimized for AI orchestration
- **AI Layer:** LangGraph + LangChain for stateful multi-agent character system
- **Memory:** PostgreSQL with pgvector extension for unified vector + structured storage
- **Real-Time:** Hybrid SSE + HTTP for AI streaming and user actions, WebSocket for world state updates
- **Novel Patterns:** Living narrative engine, character-initiated interactions, pre-planned hidden quest system

## Cost Target

**$0.50/user/day operational cost** achieved through:

- GPT-4o-mini for routine interactions (~80% cheaper than GPT-4o)
- PostgreSQL pgvector for vector storage (no separate vector DB costs)
- Efficient prompt engineering to minimize token usage
- Selective use of GPT-4o for premium narrative generation only

## Design Philosophy

1. **Emotion-First:** Every interaction starts with understanding the user's current state
2. **Memory-Powered:** Persistent context across all conversations and sessions
3. **Narrative-Driven:** Progress is framed as story advancement, not task completion
4. **Cost-Conscious:** Premium experience without premium pricing

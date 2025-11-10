# Performance Considerations

**Frontend:**

- Code splitting: Next.js automatic
- Image optimization: `next/image` with AVIF
- Caching: Static pages cached, dynamic with revalidation
- Bundle size: Target < 200KB initial JS

**Backend:**

- Database: Connection pooling (SQLAlchemy), indexes on foreign keys
- Caching: Redis for world state, user sessions (15min TTL)
- AI calls: Rate limiting, token caching where possible
- Background jobs: ARQ workers scale horizontally

**Cost Management (Target: $0.50/user/day):**

- **LLM calls:** GPT-4o-mini for primary interactions (~$0.03/user/day), GPT-4o for narrative generation only
- **Model Cost Breakdown:**
  - Eliza chat: GPT-4o-mini @ $0.15/$0.60 per 1M tokens
  - Narrative generation: GPT-4o @ $2.50/$10 per 1M tokens (infrequent)
  - Embeddings: text-embedding-3-small @ $0.02 per 1M tokens
  - Emotion detection: Self-hosted (free after infrastructure)
- **Vector storage:** PostgreSQL pgvector (unified database, no separate service)
- **Authentication:** Clerk free tier (10K MAU), then $25/1000 MAU
- **Database:** Connection pooling, efficient indexing on vector columns
- **Caching:** Redis for narrative templates, character prompts, world state
- **Monitoring:** Track LLM costs per user in real-time, implement soft limits

---

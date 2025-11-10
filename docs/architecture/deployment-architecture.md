# Deployment Architecture

**Experimental Version:**

- **Frontend:** Vercel (Next.js optimized)
- **Backend:** Railway or Fly.io (Docker containers)
- **Database:** Railway PostgreSQL with pgvector or Supabase (has pgvector support)
- **Redis:** Upstash (serverless Redis)
- **File Storage:** S3-compatible (AWS S3 or MinIO)

**Production Version:**

- **Frontend:** Vercel (edge network)
- **Backend:** AWS ECS/Fargate or Fly.io (auto-scaling)
- **Database:** AWS RDS PostgreSQL with pgvector extension (managed)
- **Redis:** AWS ElastiCache or Upstash
- **File Storage:** AWS S3
- **Monitoring:** Sentry (errors, performance, session replay), CloudWatch for infrastructure

---

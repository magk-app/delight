# Security Architecture

**Authentication:**

- **Clerk** - Managed authentication service
  - Session management with JWTs (handled by Clerk)
  - OAuth providers (Google, GitHub, etc.)
  - Magic link authentication
  - Multi-factor authentication (2FA)
  - Password policies and breach detection
- **Backend:** Clerk session verification middleware
- **Frontend:** `@clerk/nextjs` for auth UI and session management

**Authorization:**

- User-scoped data access (users can only access their own missions, progress)
- Clerk user IDs used as primary user identifier in database
- Role-based: User, Admin (future, managed via Clerk metadata)

**Data Protection:**

- Encryption at rest: Database encryption (PostgreSQL)
- Encryption in transit: HTTPS/TLS
- Evidence uploads: S3 with signed URLs, user-only access
- Clerk handles password security (not stored in our database)

**Privacy:**

- Opt-in for any tracking (tab monitoring, etc.)
- User data export/deletion: GDPR-compliant endpoints
- Clerk compliance: SOC 2 Type II, GDPR, CCPA compliant

---

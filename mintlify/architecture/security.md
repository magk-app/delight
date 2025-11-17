---
title: Security Architecture
description: Authentication, authorization, and data protection strategies
---

# Security Architecture

## Authentication

### Clerk Integration

Delight uses **Clerk** as the managed authentication service, providing enterprise-grade security without the complexity of building custom auth:

**Key Features:**
- Session management with JWTs (handled by Clerk)
- OAuth providers (Google, GitHub, Microsoft, etc.)
- Magic link authentication (passwordless)
- Multi-factor authentication (2FA via SMS or authenticator app)
- Password policies and breach detection
- SOC 2 Type II, GDPR, CCPA compliant

### Frontend Authentication

```typescript
// Next.js middleware protects routes
import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

// Protected pages use Clerk hooks
import { useUser } from "@clerk/nextjs";

function Dashboard() {
  const { user, isLoaded } = useUser();
  // user.id is the Clerk user ID
}
```

### Backend Authentication

```python
# FastAPI middleware verifies Clerk session tokens
from app.core.clerk_auth import verify_clerk_token

@app.get("/api/v1/missions")
async def get_missions(user_id: str = Depends(verify_clerk_token)):
    # user_id is the verified Clerk user ID
    missions = await mission_service.get_user_missions(user_id)
    return missions
```

**Session Verification:**
1. Frontend includes Clerk session token in `Authorization` header
2. Backend verifies token signature using Clerk's public keys
3. Extracts `clerk_user_id` from verified token
4. Uses `clerk_user_id` to query database (not storing passwords)

---

## Authorization

### User-Scoped Data Access

All data is scoped to the authenticated user:

```python
# Example: Users can only access their own missions
async def get_user_missions(user_id: str):
    result = await db.execute(
        select(Mission).where(Mission.user_id == user_id)
    )
    return result.scalars().all()
```

**Key Principles:**
- Every query includes `WHERE user_id = :user_id`
- No endpoint allows cross-user data access
- Admin endpoints (future) use role-based access via Clerk metadata

### Role-Based Access (Future)

```json
// Clerk user metadata
{
  "role": "admin",
  "permissions": ["view_all_users", "manage_content"]
}
```

---

## Data Protection

### Encryption at Rest

- **Database:** Supabase provides automatic encryption at rest for PostgreSQL
- **File Storage:** S3 server-side encryption (SSE-S3)
- **Backups:** Encrypted backups via Supabase

### Encryption in Transit

- **HTTPS/TLS:** All API communication encrypted with TLS 1.3
- **Frontend ↔ Backend:** HTTPS only (enforced in production)
- **Database connections:** SSL/TLS required for PostgreSQL connections

### Evidence Uploads

```python
# S3 signed URLs for secure uploads
def generate_upload_url(user_id: str, filename: str):
    # Generate pre-signed URL valid for 15 minutes
    url = s3_client.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=f"evidence/{user_id}/{uuid4()}/{filename}",
        ExpiresIn=900  # 15 minutes
    )
    return url
```

**Security features:**
- User-specific S3 paths (`evidence/{user_id}/...`)
- Time-limited signed URLs (15 minutes)
- Content-Type validation
- File size limits (10MB max)

### Password Security

**Clerk handles all password security:**
- Passwords never stored in Delight's database
- PBKDF2 with SHA-256 hashing (Clerk standard)
- Breach detection via HaveIBeenPwned integration
- Automatic password strength requirements

---

## Privacy

### Data Collection

**What we collect:**
- User account info (email, name from Clerk)
- Missions, progress, conversations
- Emotional state (for personalization)
- Optional: Tab monitoring data (with explicit opt-in)

**What we DON'T collect:**
- Passwords (managed by Clerk)
- Sensitive personal information
- Location data (unless explicitly provided)

### User Rights (GDPR Compliance)

**Data Export:**
```python
@app.get("/api/v1/users/me/export")
async def export_user_data(user_id: str = Depends(verify_clerk_token)):
    data = await user_service.export_all_data(user_id)
    return JSONResponse(content=data)
```

**Data Deletion:**
```python
@app.delete("/api/v1/users/me")
async def delete_user_account(user_id: str = Depends(verify_clerk_token)):
    # CASCADE deletes all user data
    await user_service.delete_user(user_id)
    # Also delete from Clerk
    await clerk_client.delete_user(user_id)
```

### Opt-In Features

**Tab monitoring (for DCI calculation):**
```python
class UserPreferences(Base):
    tab_monitoring_enabled: bool = False  # Opt-in
    emotion_tracking_enabled: bool = True  # Enabled by default, can opt-out
```

---

## API Security

### Rate Limiting

```python
# Redis-based rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_user_id)

@app.post("/api/v1/companion/chat")
@limiter.limit("20/minute")  # Prevent chat spam
async def chat(request: Request):
    pass
```

**Limits:**
- Default: 100 requests/minute per user
- Companion chat: 20 requests/minute
- Mission creation: 50 requests/hour

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class MissionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    duration_minutes: int = Field(..., ge=1, le=480)  # 1-480 minutes

    @validator('title')
    def sanitize_title(cls, v):
        # Remove potentially malicious content
        return bleach.clean(v)
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://delight.so",
        "https://app.delight.so",
        "http://localhost:3000"  # Dev only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

---

## Monitoring & Incident Response

### Error Tracking

```python
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
)
```

**What we track:**
- Unhandled exceptions
- Failed authentication attempts
- Rate limit violations
- Unusual API usage patterns

### Security Monitoring

**Alerts triggered on:**
- Multiple failed login attempts (Clerk handles this)
- Unusual data access patterns
- Elevated error rates
- Suspicious API usage

### Incident Response

1. **Detection:** Sentry alerts or Clerk security notifications
2. **Investigation:** Review logs, identify affected users
3. **Mitigation:** Revoke sessions, block IPs if needed
4. **Notification:** Email affected users within 72 hours (GDPR requirement)
5. **Post-mortem:** Document incident, update security measures

---

## Security Best Practices

### For Developers

- ✅ Never commit secrets (use environment variables)
- ✅ Always validate user input with Pydantic
- ✅ Use parameterized queries (SQLAlchemy handles this)
- ✅ Scope all queries to authenticated user
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated (automated with Dependabot)

### For Users

- ✅ Enable 2FA in Clerk settings
- ✅ Use strong, unique passwords
- ✅ Review connected OAuth providers
- ✅ Log out on shared devices

---

## Compliance

### GDPR

- ✅ User consent for data processing
- ✅ Right to access (data export)
- ✅ Right to erasure (account deletion)
- ✅ Data portability (JSON export)
- ✅ Privacy policy (provided)

### SOC 2 (via Clerk)

- ✅ Access controls
- ✅ Encryption at rest and in transit
- ✅ Logging and monitoring
- ✅ Incident response procedures

### CCPA (California Privacy)

- ✅ Disclosure of data collection
- ✅ Right to opt-out of data sale (we don't sell data)
- ✅ Right to deletion

---

## Vulnerability Disclosure

**Found a security issue?**

Email: security@delight.so

**What to include:**
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

**Our commitment:**
- Acknowledge within 48 hours
- Provide timeline for fix within 7 days
- Credit researchers (with permission) in security advisories

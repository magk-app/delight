# Story 1.3 Tests - Quick Reference Card

## Quick Test Commands

### Backend Tests (37 tests)

```bash
# Run all auth tests (fastest: ~3-5 seconds)
cd packages/backend
poetry run pytest tests/integration/test_auth.py tests/integration/test_webhooks.py -v

# Run with coverage
poetry run pytest tests/integration/ -v --cov=app.core.clerk_auth --cov=app.api.v1.webhooks --cov=app.services.clerk_service

# Run single test
poetry run pytest tests/integration/test_auth.py::TestGetCurrentUser::test_get_current_user_with_valid_token -v
```

### Frontend Tests (18 tests)

```bash
# Run all E2E auth tests (~45-60 seconds)
cd packages/frontend
npm run test:e2e tests/e2e/auth.spec.ts

# Run with UI (debug mode)
npm run test:e2e:ui tests/e2e/auth.spec.ts

# Run single test
npx playwright test auth.spec.ts -g "should complete sign-in"
```

---

## Test Files Overview

| File | Tests | What It Tests |
|------|-------|---------------|
| `packages/backend/tests/integration/test_auth.py` | 11 | JWT validation, `get_current_user()`, `/users/me` endpoint |
| `packages/backend/tests/integration/test_webhooks.py` | 26 | Svix signatures, user creation/updates, idempotency |
| `packages/frontend/tests/e2e/auth.spec.ts` | 18 | Sign-up, sign-in, route protection, session persistence |

**Total: 55 test cases**

---

## Required Environment Variables

### Backend

```bash
export CLERK_SECRET_KEY="sk_test_..."
export CLERK_WEBHOOK_SECRET="whsec_..."
export DATABASE_URL="postgresql+asyncpg://..." # or use SQLite default
```

### Frontend

```bash
export CLERK_TEST_USER_EMAIL="test@delight.dev"
export CLERK_TEST_USER_PASSWORD="YourSecurePassword123!"
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
```

---

## Test Coverage

### Backend Components

- ✅ `app/core/clerk_auth.py` - `get_current_user()` dependency
- ✅ `app/api/v1/users.py` - `/users/me` endpoint
- ✅ `app/api/v1/webhooks.py` - `/webhooks/clerk` endpoint
- ✅ `app/services/clerk_service.py` - User sync logic
- ✅ `app/schemas/webhook.py` - Webhook payload validation

### Frontend Components

- ✅ `src/middleware.ts` - Route protection
- ✅ `src/app/sign-in/[[...sign-in]]/page.tsx` - Sign-in UI
- ✅ `src/app/sign-up/[[...sign-up]]/page.tsx` - Sign-up UI
- ✅ Session persistence and cross-tab authentication

---

## Test Helpers

### Backend

```python
# Create JWT token
from tests.helpers.auth import create_mock_jwt_token
token = create_mock_jwt_token("user_123")

# Create auth headers
from tests.helpers.auth import create_auth_headers
headers = create_auth_headers("user_123")

# Create test user
from tests.helpers.auth import create_test_user
user = await create_test_user(db, clerk_user_id="user_123", email="test@example.com")
```

### Frontend

```typescript
// Sign in helper
import { login } from "../support/helpers/auth";
await login(page, email, password);

// Sign out helper
import { logout } from "../support/helpers/auth";
await logout(page);
```

---

## Common Test Patterns

### Backend: Test Protected Endpoint

```python
async def test_protected_endpoint(client: AsyncClient, db_session: AsyncSession):
    # Create user
    user = await create_test_user(db_session, clerk_user_id="user_123")

    # Create auth headers
    headers = create_auth_headers("user_123")

    # Make request
    response = await client.get("/api/v1/protected", headers=headers)

    assert response.status_code == 200
```

### Backend: Test Webhook

```python
async def test_webhook(client: AsyncClient, db_session: AsyncSession):
    from app.core.config import settings

    payload = {
        "type": "user.created",
        "data": {
            "id": "user_123",
            "email_addresses": [{"email_address": "test@example.com"}],
        },
    }

    headers = create_webhook_headers(payload, settings.CLERK_WEBHOOK_SECRET)
    response = await client.post("/api/v1/webhooks/clerk", json=payload, headers=headers)

    assert response.status_code == 200
```

### Frontend: Test Authentication Flow

```typescript
test("should sign in", async ({ page }) => {
  await page.goto("/sign-in");

  // Wait for Clerk form
  await page.waitForSelector('input[name="identifier"]');

  // Fill credentials
  await page.fill('input[name="identifier"]', TEST_EMAIL);
  await page.click('button[type="submit"]');

  await page.waitForSelector('input[name="password"]');
  await page.fill('input[name="password"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');

  // Verify redirect
  await page.waitForURL((url) => !url.pathname.includes("/sign-in"));
});
```

---

## Debugging Tips

### Backend

```bash
# Run with print statements visible
poetry run pytest tests/integration/test_auth.py -v -s

# Run with PDB debugger on failure
poetry run pytest tests/integration/test_auth.py -v --pdb

# View SQL queries
# Set echo=True in conftest.py async_engine
```

### Frontend

```bash
# Run with browser visible
npx playwright test auth.spec.ts --headed

# Run in debug mode (pauses on steps)
npx playwright test auth.spec.ts --debug

# View trace files
npx playwright show-trace trace.zip
```

---

## Success Criteria Checklist

- [ ] All 37 backend tests pass
- [ ] Backend coverage ≥ 90% for auth code
- [ ] All 18 frontend tests pass
- [ ] Total test time < 2 minutes (backend + frontend)
- [ ] No test flakiness (100% pass rate on 3 runs)
- [ ] All tests have clear docstrings
- [ ] CI/CD pipeline configured

---

## Troubleshooting

### Backend: "Module not found"
```bash
cd packages/backend
poetry install
poetry run python -c "import app; print('OK')"
```

### Backend: "Database connection failed"
```bash
# Use in-memory SQLite (default)
unset DATABASE_URL
# Or verify PostgreSQL connection
echo $DATABASE_URL
```

### Frontend: "Clerk not loading"
```bash
# Check environment variables
echo $NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
echo $CLERK_SECRET_KEY

# Clear cache
rm -rf .next
pnpm dev
```

### Frontend: "Test user authentication failed"
```bash
# Verify test user exists in Clerk dashboard
# Try manual sign-in: http://localhost:3000/sign-in
```

---

## Additional Resources

- **Full Test Design:** `docs/stories/1-3-TEST-DESIGN-SUMMARY.md`
- **Execution Guide:** `packages/backend/tests/integration/TEST_EXECUTION_GUIDE.md`
- **Story Documentation:** `docs/stories/1-3-integrate-clerk-authentication-system.md`
- **Backend Tests:** `packages/backend/tests/integration/`
- **Frontend Tests:** `packages/frontend/tests/e2e/`

---

## Running Full Test Suite

```bash
# From project root
make test

# Or manually:
cd packages/backend && poetry run pytest tests/integration/ -v
cd packages/frontend && npm run test:e2e tests/e2e/auth.spec.ts
```

---

**Updated:** 2025-11-11
**Story:** 1.3 - Clerk Authentication System
**Test Status:** Design complete, ready for execution

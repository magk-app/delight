# Story 1.3 Test Design Summary

## Overview

This document provides a comprehensive overview of the automated test suite designed for Story 1.3: Clerk Authentication System.

**Status:** Test design complete, ready for implementation validation
**Date:** 2025-11-11
**Total Test Cases:** 55 (37 backend + 18 frontend)

---

## Test Coverage Summary

### Backend Tests (37 test cases)

| Component | Test File | Test Cases | Coverage Target |
|-----------|-----------|------------|-----------------|
| `get_current_user()` dependency | `test_auth.py` | 8 | 100% |
| Protected endpoints | `test_auth.py` | 3 | 100% |
| Webhook signature validation | `test_webhooks.py` | 6 | 100% |
| User created events | `test_webhooks.py` | 7 | 100% |
| User updated events | `test_webhooks.py` | 2 | 100% |
| Webhook idempotency | `test_webhooks.py` | 3 | 100% |
| Error handling | `test_webhooks.py` | 2 | 95%+ |

### Frontend Tests (18 test cases)

| Feature | Test File | Test Cases |
|---------|-----------|------------|
| Unauthenticated flows | `auth.spec.ts` | 4 |
| Sign-up flow | `auth.spec.ts` | 3 |
| Sign-in flow | `auth.spec.ts` | 3 |
| Authenticated flows | `auth.spec.ts` | 3 |
| Route protection | `auth.spec.ts` | 3 |
| Session persistence | `auth.spec.ts` | 2 |

---

## Test Architecture

### Backend Test Strategy

**Framework:** pytest + pytest-asyncio + httpx (AsyncClient)

**Key Patterns:**
- Integration tests hitting real HTTP endpoints
- Database transactions with automatic rollback
- Mock JWT tokens for authentication
- Real Svix signature generation for webhooks
- SQLite in-memory for fast tests, PostgreSQL for CI

**Test Isolation:**
- Each test runs in isolated database transaction
- Automatic rollback after test completion
- No manual cleanup required
- Tests can run in parallel

### Frontend Test Strategy

**Framework:** Playwright for E2E testing

**Key Patterns:**
- Real browser automation (Chromium, Firefox, Safari)
- Real Clerk authentication flows
- Session state persistence testing
- Network request interception for API verification

**Test Data:**
- Unique test user email per run (timestamp-based)
- Reusable test credentials from environment
- Automatic Clerk UI interaction

---

## Test Files Structure

### Backend

```
packages/backend/tests/
├── conftest.py                      # Shared fixtures (db, client, auth)
├── helpers/
│   ├── auth.py                      # JWT token generation, user creation
│   └── database.py                  # Database utilities
├── integration/
│   ├── test_auth.py                 # Authentication dependency tests (11 tests)
│   ├── test_webhooks.py             # Webhook handler tests (26 tests)
│   └── TEST_EXECUTION_GUIDE.md      # How to run tests
└── unit/
    └── test_example.py              # Unit test template
```

### Frontend

```
packages/frontend/tests/
├── e2e/
│   ├── auth.spec.ts                 # Authentication E2E tests (18 tests)
│   ├── auth.setup.ts                # Auth state setup
│   └── example.spec.ts              # E2E test examples
├── support/
│   ├── fixtures/
│   │   ├── index.ts                 # Custom fixtures
│   │   └── factories/               # Test data factories
│   └── helpers/
│       ├── auth.ts                  # Auth helpers
│       ├── clerk.ts                 # Clerk utilities
│       └── wait.ts                  # Wait/polling utilities
└── README.md
```

---

## Detailed Test Cases

### Backend: `test_auth.py`

#### TestGetCurrentUser (8 tests)

1. **test_get_current_user_with_valid_token**
   - ✅ Valid JWT → Returns authenticated user
   - Validates complete authentication flow

2. **test_get_current_user_missing_authorization_header**
   - ✅ No header → 403 Forbidden
   - Security: Proper rejection of unauthenticated requests

3. **test_get_current_user_invalid_bearer_scheme**
   - ✅ Wrong scheme (e.g., "Basic") → 401 Unauthorized
   - Security: Only accept Bearer tokens

4. **test_get_current_user_empty_token**
   - ✅ "Bearer " with no token → 401 Unauthorized
   - Edge case: Handle malformed headers

5. **test_get_current_user_malformed_token**
   - ✅ Invalid JWT format → 401 Unauthorized
   - Security: Reject garbage tokens

6. **test_get_current_user_token_missing_sub_claim**
   - ✅ JWT without 'sub' claim → 401 Unauthorized
   - Security: Require complete token structure

7. **test_get_current_user_not_in_database**
   - ✅ Valid token but unknown user → 401 Unauthorized
   - Security: Return 401 (not 404) to prevent enumeration

8. **test_get_current_user_with_special_characters_in_id**
   - ✅ clerk_user_id with special chars → Success
   - Edge case: Handle unusual but valid IDs

#### TestProtectedEndpoints (3 tests)

1. **test_get_me_endpoint_success**
   - ✅ Authenticated request → Returns user profile
   - Validates UserResponse schema

2. **test_get_me_endpoint_unauthenticated**
   - ✅ No auth → 403 Forbidden
   - Security: Endpoint properly protected

3. **test_get_me_endpoint_returns_correct_user**
   - ✅ Multi-user database → Returns only requesting user
   - Security: No data leakage between users

### Backend: `test_webhooks.py`

#### TestWebhookSignatureValidation (6 tests)

1. **test_webhook_with_valid_signature**
   - ✅ Proper Svix signature → 200 OK, user created
   - Validates complete webhook flow

2. **test_webhook_missing_svix_headers**
   - ✅ No Svix headers → 400 Bad Request
   - Security: Reject unverifiable webhooks

3. **test_webhook_invalid_signature**
   - ✅ Fake signature → 400 Bad Request
   - Security: Prevent webhook spoofing

4. **test_webhook_missing_svix_id**
   - ✅ Missing header → 400 Bad Request

5. **test_webhook_missing_svix_timestamp**
   - ✅ Missing header → 400 Bad Request

6. **test_webhook_missing_svix_signature**
   - ✅ Missing header → 400 Bad Request

#### TestUserCreatedWebhook (7 tests)

1. **test_user_created_creates_new_user**
   - ✅ user.created → User in database

2. **test_user_created_extracts_primary_email**
   - ✅ Multiple emails → First email used

3. **test_user_created_constructs_display_name**
   - ✅ first_name + last_name → "FirstName LastName"

4. **test_user_created_only_first_name**
   - ✅ Only first_name → display_name = first_name

5. **test_user_created_falls_back_to_username**
   - ✅ No names but username → display_name = username

6. **test_user_created_sets_default_timezone**
   - ✅ New user → timezone = "UTC"

7. **test_user_created_handles_missing_email**
   - ✅ No email → email = None, user still created

#### TestUserUpdatedWebhook (2 tests)

1. **test_user_updated_updates_existing_user**
   - ✅ user.updated → User fields updated

2. **test_user_updated_preserves_user_id**
   - ✅ Update → UUID unchanged

#### TestWebhookIdempotency (3 tests)

1. **test_duplicate_user_created_events**
   - ✅ Same webhook twice → Only one user created

2. **test_user_created_then_updated**
   - ✅ Create → Update → Final state correct

3. **test_multiple_updates_same_user**
   - ✅ Multiple updates → Final state reflects last

#### TestWebhookErrorHandling (2 tests)

1. **test_invalid_payload_format**
   - ✅ Malformed JSON → 400 Bad Request

2. **test_unhandled_event_type_returns_success**
   - ✅ Unknown event → 200 OK (logged)

### Frontend: `auth.spec.ts`

#### Unauthenticated User Flows (4 tests)

1. **should redirect to sign-in for protected routes**
   - ✅ Navigate to /dashboard → Redirect to /sign-in

2. **should allow access to public routes**
   - ✅ Navigate to / → Loads without redirect

3. **should load sign-in page**
   - ✅ Navigate to /sign-in → Clerk form renders

4. **should load sign-up page**
   - ✅ Navigate to /sign-up → Clerk form renders

#### Sign-Up Flow (3 tests)

1. **should complete sign-up with email and password**
   - ✅ Fill form → User created → Redirect to app

2. **should show validation error for invalid email**
   - ✅ Invalid email → Error displayed

3. **should show error for duplicate email**
   - ✅ Existing email → Clerk error message

#### Sign-In Flow (3 tests)

1. **should complete sign-in with valid credentials**
   - ✅ Valid credentials → Authenticated → Redirect

2. **should show error for invalid credentials**
   - ✅ Wrong password → Clerk error message

3. **should redirect to intended page after sign-in**
   - ✅ Protected route attempt → Sign in → Return to intended route

#### Authenticated User Flows (3 tests)

1. **should allow access to protected routes**
   - ✅ Authenticated → /dashboard loads

2. **should persist session after page refresh**
   - ✅ Refresh page → Still authenticated

3. **should sign out successfully**
   - ✅ Click sign out → Signed out → Can't access protected routes

#### Route Protection (3 tests)

1. **should protect dashboard route**
   - ✅ Unauthenticated → /dashboard → Redirect

2. **should protect API routes**
   - ✅ No auth → API call → 403 Forbidden

3. **should allow webhook routes without auth**
   - ✅ No auth → Webhook endpoint → Not 403

#### Session Persistence (2 tests)

1. **should persist session across tabs**
   - ✅ Auth in tab 1 → Tab 2 also authenticated

2. **should maintain session after navigation**
   - ✅ Multiple page navigations → No re-auth needed

---

## Test Helpers and Utilities

### Backend Helpers

**File:** `tests/helpers/auth.py`

```python
# Generate mock JWT tokens
token = create_mock_jwt_token("user_123")

# Create auth headers
headers = create_auth_headers("user_123")

# Create test users
user = await create_test_user(db, clerk_user_id="user_123", email="test@example.com")
```

**File:** `tests/integration/test_webhooks.py`

```python
# Generate valid Svix webhook signatures
signature = generate_svix_signature(payload_bytes, secret, timestamp)

# Create webhook headers with signature
headers = create_webhook_headers(payload_dict, secret)
```

### Frontend Helpers

**File:** `tests/support/helpers/auth.ts`

```typescript
// Login helper
await login(page, email, password);

// Logout helper
await logout(page);
```

---

## Mock Strategy

### What We Mock

1. **JWT Signature Verification (Backend)**
   - Current implementation: Decode without verification
   - Tests: Generate properly structured JWTs
   - Reason: Clerk JWKS verification to be added later

2. **Nothing Else!**
   - Real database (SQLite/PostgreSQL)
   - Real Svix signature verification
   - Real HTTP requests
   - Real Clerk authentication (E2E)

### Why Minimal Mocking?

- **Integration confidence:** Tests verify real system behavior
- **Catch integration bugs:** Would be missed with heavy mocking
- **Maintainability:** Less mock code to maintain
- **Performance:** Fast enough with in-memory SQLite

---

## Test Data Management

### Backend

**User Data:**
```python
MOCK_CLERK_USER = {
    "id": "user_test123abc",
    "email_addresses": [{"email_address": "test@example.com"}],
    "first_name": "Test",
    "last_name": "User",
}
```

**Cleanup:** Automatic via transaction rollback

### Frontend

**Test Credentials:**
```bash
CLERK_TEST_USER_EMAIL="test@delight.dev"
CLERK_TEST_USER_PASSWORD="TestPassword123!"
```

**Unique Users:** `test-${Date.now()}@delight.dev` for sign-up tests

**Cleanup:** Manual cleanup via Clerk dashboard or API

---

## Performance Targets

### Backend

- **Total execution:** < 5 seconds (37 tests)
- **Individual test:** < 200ms
- **Auth overhead:** < 10ms per request
- **Database setup:** < 100ms per test

### Frontend

- **Total execution:** < 60 seconds (18 tests)
- **Individual test:** < 5 seconds
- **Clerk load:** 1-2 seconds
- **Sign-in flow:** 3-5 seconds

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Story 1.3 Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: poetry install
      - run: pytest tests/integration/ --cov
    env:
      CLERK_SECRET_KEY: ${{ secrets.CLERK_SECRET_KEY }}
      CLERK_WEBHOOK_SECRET: ${{ secrets.CLERK_WEBHOOK_SECRET }}

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: pnpm install
      - run: npx playwright install --with-deps
      - run: pnpm test:e2e
    env:
      CLERK_TEST_USER_EMAIL: ${{ secrets.CLERK_TEST_USER_EMAIL }}
      CLERK_TEST_USER_PASSWORD: ${{ secrets.CLERK_TEST_USER_PASSWORD }}
```

---

## Success Criteria

- [ ] All 37 backend tests pass
- [ ] Backend code coverage ≥ 90% for auth code
- [ ] All 18 frontend E2E tests pass
- [ ] Tests complete in < 2 min (backend) + < 60 sec (frontend)
- [ ] Zero test flakiness (all tests deterministic)
- [ ] All tests documented with clear docstrings
- [ ] Test execution guide completed
- [ ] CI/CD pipeline includes all tests

---

## Running the Tests

### Quick Start

```bash
# Backend
cd packages/backend
poetry run pytest tests/integration/test_auth.py tests/integration/test_webhooks.py -v

# Frontend
cd packages/frontend
npm run test:e2e tests/e2e/auth.spec.ts
```

### Detailed Instructions

See `packages/backend/tests/integration/TEST_EXECUTION_GUIDE.md` for:
- Prerequisites and setup
- Environment variables
- Running specific tests
- Debugging tips
- CI/CD configuration
- Troubleshooting guide

---

## Next Steps

1. **Validate tests pass** - Run full test suite
2. **Review coverage** - Ensure ≥90% for auth code
3. **Fix any failures** - Debug and iterate
4. **Update story docs** - Add test results
5. **Commit to version control** - Preserve test suite
6. **Mark story complete** - Update sprint status

---

## Appendix: Test Technologies

### Backend Stack

- **pytest:** Test framework
- **pytest-asyncio:** Async test support
- **httpx:** Async HTTP client for API tests
- **SQLAlchemy:** Database ORM
- **jwt:** JWT token generation
- **svix:** Webhook signature generation

### Frontend Stack

- **Playwright:** Browser automation
- **TypeScript:** Type-safe test code
- **Clerk:** Real authentication service

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-11 | 1.0 | Initial test design complete |

---

**Prepared by:** TEA (Test Engineering Agent)
**For:** Story 1.3 - Clerk Authentication System
**Project:** Delight AI Companion Platform

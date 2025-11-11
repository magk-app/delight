# Story 1.3 Authentication Tests - Execution Guide

## Overview

This guide explains how to run the comprehensive test suite for Story 1.3: Clerk Authentication System.

## Test Files

### Backend Integration Tests

- `test_auth.py` - Authentication dependency and protected endpoints (11 tests)
- `test_webhooks.py` - Webhook signature validation and user sync (26 tests)

### Frontend E2E Tests

- `auth.spec.ts` - Complete authentication user flows (18 tests)

**Total: 55 test cases**

---

## Prerequisites

### Backend Tests

1. **Python environment**

   ```bash
   cd packages/backend
   poetry install
   ```

2. **Test database configuration**

   Tests support two database options:

   **Option A: SQLite in-memory (default, recommended for most tests)**

   - **What it is:** A temporary database that exists only in RAM during test execution
   - **Pros:**
     - Fastest option (no disk I/O)
     - No setup required (works out of the box)
     - Automatically cleaned up after tests
     - Perfect for testing business logic
   - **Cons:**
     - Not a real PostgreSQL database (some PostgreSQL-specific features won't work)
     - Data is lost when tests finish (by design)
   - **When to use:** Default choice for most integration tests

   **Option B: PostgreSQL test database (for PostgreSQL-specific testing)**

   - **What it is:** A real PostgreSQL database (separate from your dev database)
   - **Pros:**
     - Tests against actual PostgreSQL (pgvector, JSONB, etc.)
     - Can verify PostgreSQL-specific features
   - **Cons:**
     - Requires PostgreSQL installed and running
     - Slower than SQLite
     - Requires manual database setup
   - **When to use:** When testing PostgreSQL-specific features (pgvector, advanced JSONB queries, etc.)

   **How to configure:**

   The tests automatically use SQLite in-memory by default. To use PostgreSQL instead, set the `TEST_DATABASE_URL` environment variable:

   **Option 1: Add to your `.env` file** (recommended)

   ```bash
   # In packages/backend/.env
   TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/delight_test
   ```

   **Option 2: Set as environment variable** (temporary, for current shell session)

   ```bash
   # Windows PowerShell
   $env:TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/delight_test"

   # Windows CMD
   set TEST_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/delight_test

   # Linux/Mac
   export TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/delight_test"
   ```

   **Note:** The tests will use `TEST_DATABASE_URL` if set, otherwise they default to SQLite in-memory. Your regular `DATABASE_URL` (for the dev server) is separate and won't affect tests.

3. **Environment variables**

   **Using your `.env` file:**

   The application automatically loads environment variables from `packages/backend/.env` using Pydantic Settings. Simply add these to your `.env` file:

   ```bash
   # In packages/backend/.env
   CLERK_SECRET_KEY=sk_test_your_key
   CLERK_WEBHOOK_SECRET=whsec_your_secret
   DATABASE_URL=postgresql+asyncpg://...  # For dev server (not used by tests)
   TEST_DATABASE_URL=postgresql+asyncpg://...  # Optional: for PostgreSQL tests
   ```

   **Alternative: Set environment variables manually** (if you prefer not to use `.env`)

   ```bash
   # Windows PowerShell
   $env:CLERK_SECRET_KEY="sk_test_your_key"
   $env:CLERK_WEBHOOK_SECRET="whsec_your_secret"

   # Linux/Mac
   export CLERK_SECRET_KEY="sk_test_your_key"
   export CLERK_WEBHOOK_SECRET="whsec_your_secret"
   ```

   **Important:**

   - Tests use `TEST_DATABASE_URL` (if set) or default to SQLite in-memory
   - Your dev server uses `DATABASE_URL` from `.env`
   - These are separate - tests won't touch your development database

### Frontend Tests

1. **Node environment**

   ```bash
   cd packages/frontend
   pnpm install
   npx playwright install  # Install browsers
   ```

2. **Test credentials**

   ```bash
   # Create test user in Clerk dashboard first
   export CLERK_TEST_USER_EMAIL="test@delight.dev"
   export CLERK_TEST_USER_PASSWORD="YourTestPassword123!"
   ```

3. **Backend running**

   ```bash
   # Terminal 1: Backend
   cd packages/backend
   poetry run uvicorn main:app --reload

   # Terminal 2: Frontend
   cd packages/frontend
   pnpm dev
   ```

---

## Running Backend Tests

### Run All Tests

```bash
cd packages/backend
poetry run pytest tests/integration/test_auth.py tests/integration/test_webhooks.py -v
```

### Run Individual Test Files

```bash
# Auth tests only
poetry run pytest tests/integration/test_auth.py -v

# Webhook tests only
poetry run pytest tests/integration/test_webhooks.py -v
```

### Run Specific Test Class

```bash
# Just authentication tests
poetry run pytest tests/integration/test_auth.py::TestGetCurrentUser -v

# Just signature validation tests
poetry run pytest tests/integration/test_webhooks.py::TestWebhookSignatureValidation -v
```

### Run with Coverage

```bash
# Generate coverage report
poetry run pytest tests/integration/ -v \
  --cov=app.core.clerk_auth \
  --cov=app.api.v1.webhooks \
  --cov=app.api.v1.users \
  --cov=app.services.clerk_service \
  --cov-report=html \
  --cov-report=term

# Open coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

### Run with Markers

```bash
# Run only auth-related tests
poetry run pytest -m auth -v

# Run only webhook tests
poetry run pytest -m webhooks -v

# Run all integration tests
poetry run pytest -m integration -v
```

### Debug Mode

```bash
# Run with print statements visible
poetry run pytest tests/integration/test_auth.py -v -s

# Run single test with debugging
poetry run pytest tests/integration/test_auth.py::TestGetCurrentUser::test_get_current_user_with_valid_token -v -s
```

---

## Running Frontend Tests

### Run All E2E Tests

```bash
cd packages/frontend
npm run test:e2e tests/e2e/auth.spec.ts
```

### Run with UI (Interactive)

```bash
# Opens Playwright UI for debugging
npm run test:e2e:ui tests/e2e/auth.spec.ts
```

### Run Specific Test

```bash
# Run single test by name
npx playwright test auth.spec.ts -g "should complete sign-in with valid credentials"
```

### Run with Different Browsers

```bash
# Chrome only
npx playwright test auth.spec.ts --project=chromium

# Firefox only
npx playwright test auth.spec.ts --project=firefox

# All browsers
npx playwright test auth.spec.ts
```

### Debug Mode

```bash
# Run with browser visible (headed mode)
npx playwright test auth.spec.ts --headed

# Debug mode (pauses on failure)
npx playwright test auth.spec.ts --debug
```

### View Test Report

```bash
# Generate and open HTML report
npx playwright show-report
```

---

## Expected Results

### Backend Tests

```
tests/integration/test_auth.py::TestGetCurrentUser
✓ test_get_current_user_with_valid_token
✓ test_get_current_user_missing_authorization_header
✓ test_get_current_user_invalid_bearer_scheme
✓ test_get_current_user_empty_token
✓ test_get_current_user_malformed_token
✓ test_get_current_user_token_missing_sub_claim
✓ test_get_current_user_not_in_database
✓ test_get_current_user_with_special_characters_in_id

tests/integration/test_auth.py::TestProtectedEndpoints
✓ test_get_me_endpoint_success
✓ test_get_me_endpoint_unauthenticated
✓ test_get_me_endpoint_returns_correct_user

tests/integration/test_webhooks.py::TestWebhookSignatureValidation
✓ test_webhook_with_valid_signature
✓ test_webhook_missing_svix_headers
✓ test_webhook_invalid_signature
✓ test_webhook_missing_svix_id
✓ test_webhook_missing_svix_timestamp
✓ test_webhook_missing_svix_signature

tests/integration/test_webhooks.py::TestUserCreatedWebhook
✓ test_user_created_creates_new_user
✓ test_user_created_extracts_primary_email
✓ test_user_created_constructs_display_name
✓ test_user_created_only_first_name
✓ test_user_created_falls_back_to_username
✓ test_user_created_sets_default_timezone
✓ test_user_created_handles_missing_email

tests/integration/test_webhooks.py::TestUserUpdatedWebhook
✓ test_user_updated_updates_existing_user
✓ test_user_updated_preserves_user_id

tests/integration/test_webhooks.py::TestWebhookIdempotency
✓ test_duplicate_user_created_events
✓ test_user_created_then_updated
✓ test_multiple_updates_same_user

tests/integration/test_webhooks.py::TestWebhookErrorHandling
✓ test_invalid_payload_format
✓ test_unhandled_event_type_returns_success

================================ 37 passed in 3.45s ================================
```

### Frontend Tests

```
Running 18 tests using 3 workers

  ✓ Unauthenticated User Flows
    ✓ should redirect to sign-in for protected routes
    ✓ should allow access to public routes
    ✓ should load sign-in page
    ✓ should load sign-up page

  ✓ Sign-Up Flow
    ✓ should complete sign-up with email and password
    ✓ should show validation error for invalid email
    ✓ should show error for duplicate email

  ✓ Sign-In Flow
    ✓ should complete sign-in with valid credentials
    ✓ should show error for invalid credentials
    ✓ should redirect to intended page after sign-in

  ✓ Authenticated User Flows
    ✓ should allow access to protected routes
    ✓ should persist session after page refresh
    ✓ should sign out successfully

  ✓ Route Protection
    ✓ should protect dashboard route
    ✓ should protect API routes
    ✓ should allow webhook routes without auth

  ✓ Session Persistence
    ✓ should persist session across tabs
    ✓ should maintain session after navigation

  18 passed (45s)
```

---

## Troubleshooting

### Backend Issues

**Issue: Database connection errors**

```bash
# Verify database URL
echo $DATABASE_URL

# Test database connection
poetry run python scripts/test_db_connection.py
```

**Issue: Import errors**

```bash
# Reinstall dependencies
poetry install

# Check Python path
poetry run python -c "import app; print(app.__file__)"
```

**Issue: Webhook signature verification fails**

```bash
# Check webhook secret is set
echo $CLERK_WEBHOOK_SECRET

# Should start with "whsec_"
```

### Frontend Issues

**Issue: Clerk not loading**

```bash
# Check environment variables
echo $NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
echo $CLERK_SECRET_KEY

# Clear Next.js cache
rm -rf .next
pnpm dev
```

**Issue: Test user authentication fails**

```bash
# Verify test user exists in Clerk dashboard
# Check credentials in .env

# Try manual sign-in at http://localhost:3000/sign-in
```

**Issue: Port already in use**

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Use different port
PORT=3001 pnpm dev
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test-auth.yml
name: Test Authentication

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd packages/backend
          pip install poetry
          poetry install
      - name: Run tests
        env:
          CLERK_SECRET_KEY: ${{ secrets.CLERK_SECRET_KEY }}
          CLERK_WEBHOOK_SECRET: ${{ secrets.CLERK_WEBHOOK_SECRET }}
          DATABASE_URL: sqlite+aiosqlite:///:memory:
        run: |
          cd packages/backend
          poetry run pytest tests/integration/ -v --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd packages/frontend
          npm install
          npx playwright install --with-deps
      - name: Run tests
        env:
          CLERK_TEST_USER_EMAIL: ${{ secrets.CLERK_TEST_USER_EMAIL }}
          CLERK_TEST_USER_PASSWORD: ${{ secrets.CLERK_TEST_USER_PASSWORD }}
        run: |
          cd packages/frontend
          npm run test:e2e
```

---

## Performance Benchmarks

### Backend Tests

- **Total execution time:** ~3-5 seconds
- **Average per test:** ~100ms
- **Database setup/teardown:** ~50ms per test
- **Auth latency:** <10ms per request

### Frontend Tests

- **Total execution time:** ~45-60 seconds
- **Average per test:** ~2.5 seconds
- **Clerk load time:** ~1-2 seconds
- **Sign-in flow:** ~3-5 seconds

---

## Next Steps

After all tests pass:

1. **Review coverage report** - Ensure ≥90% for auth code
2. **Run manual smoke tests** - Verify UI works as expected
3. **Update story status** - Mark Story 1.3 as complete
4. **Commit test files** - Add to version control
5. **Update documentation** - Add test results to story summary

---

## Questions?

- Check test file comments for detailed test descriptions
- Review implementation files for business logic
- Consult Story 1.3 documentation: `docs/stories/1-3-integrate-clerk-authentication-system.md`

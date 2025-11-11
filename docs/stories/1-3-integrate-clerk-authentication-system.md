# Story 1.3: Integrate Clerk Authentication System

Status: ready-for-dev

## Story

As a **Delight user**,
I want **a secure and seamless authentication experience with multiple sign-in options that feels native to the platform**,
so that **I can safely access my personalized AI companion and progress data without managing passwords myself**.

## Acceptance Criteria

### AC1: Frontend Clerk Integration Complete

**Given** the Next.js 15 application with App Router
**When** a user visits any protected route without authentication
**Then**:

- User is redirected to Clerk's sign-in page at `/sign-in`
- After successful authentication, user returns to originally requested destination
- Middleware protects routes: `/companion`, `/missions`, `/world`, `/progress`
- Public routes remain accessible: `/`, `/sign-in`, `/sign-up`, `/docs`
- `<ClerkProvider>` wraps the application in root layout
- Sign-in and sign-up pages render Clerk components correctly

[Source: docs/epics.md lines 182-184, docs/tech-spec-epic-1.md lines 204-212]

### AC2: Backend Session Verification Working

**Given** authenticated frontend requests to backend API
**When** the backend receives a request with Clerk session token in Authorization header
**Then**:

- Backend `get_current_user()` dependency validates Clerk session tokens
- Valid tokens extract `clerk_user_id` from session and load user from database
- Invalid/expired tokens return HTTP 401 Unauthorized with clear error message
- Missing Authorization header returns HTTP 403 Forbidden
- Protected endpoints use `Depends(get_current_user)` to enforce authentication
- Token validation uses official `pyclerk` SDK with proper error handling

[Source: docs/tech-spec-epic-1.md lines 222-237]

### AC3: User Sync via Webhook Functional

**Given** a user signs up or updates profile in Clerk
**When** Clerk fires webhook events (`user.created`, `user.updated`)
**Then**:

- Webhook endpoint `/api/v1/webhooks/clerk` receives and validates events
- Svix signature verification prevents unauthorized webhook requests
- `user.created` event creates new user record in `users` table with `clerk_user_id`
- `user.updated` event updates `email` and `display_name` in existing user record
- Webhook operations are idempotent (duplicate events don't cause errors)
- All webhook events logged with structured logging for audit trail
- User records properly link to existing database schema from Story 1.2

[Source: docs/epics.md lines 189-192, docs/tech-spec-epic-1.md lines 238-252]

### AC4: Protected API Endpoints Secured

**Given** the FastAPI backend with protected endpoints
**When** requests are made to `/api/v1/users/me`
**Then**:

- Endpoint returns HTTP 401 without valid session token
- Endpoint returns user data (id, clerk_user_id, email, display_name) with valid token
- User data matches `clerk_user_id` extracted from session token
- Different users cannot access each other's data
- All database queries use async SQLAlchemy properly
- Response follows `UserResponse` schema from Story 1.2 user models

[Source: docs/tech-spec-epic-1.md lines 213-221]

### AC5: Authentication State Managed in Frontend

**Given** the Next.js application with Clerk hooks
**When** a user signs in, signs out, or session state changes
**Then**:

- `useUser()` hook provides current user state across all components
- Signed-in users see user menu with display name and sign-out button
- Signed-out users see "Sign In" and "Sign Up" buttons
- Sign-out button clears session and redirects to home page
- Session persists across page refreshes (Clerk manages cookies)
- `<UserButton>` component provides profile management dropdown

[Source: docs/tech-spec-epic-1.md lines 204-212]

### AC6: Environment Variables Configured Correctly

**Given** both frontend and backend applications
**When** deployed with required Clerk environment variables
**Then**:

**Frontend `.env.local`:**

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (starts with `pk_`) - client-side
- `CLERK_SECRET_KEY` (starts with `sk_`) - server-side middleware only

**Backend `.env`:**

- `CLERK_SECRET_KEY` (starts with `sk_`) - session verification
- `CLERK_WEBHOOK_SECRET` (starts with `whsec_`) - webhook signature validation

**And:**

- `.env.example` files document all required variables with comments
- No secrets committed to git (`.env` in `.gitignore`)
- Application fails gracefully with clear error if variables missing
- Startup validation checks key formats (pk*/sk*/whsec\_ prefixes)

[Source: docs/tech-spec-epic-1.md lines 196-203, 253-262]

### AC7: Complete Documentation and Testing

**Given** the implemented authentication system
**When** reviewed by another developer
**Then**:

- README.md updated with Clerk setup instructions (< 5 minutes to complete)
- API documentation includes authentication examples with sample requests
- Integration tests cover webhook flow (user creation/update, signature validation)
- E2E tests cover complete sign-in/sign-out user journey
- Manual testing checklist completed with evidence
- All tests passing in CI pipeline

[Source: docs/stories/1-1-*.md and docs/stories/1-2-*.md quality standards]

## Tasks / Subtasks

### Task 1: Setup Clerk Account and Configuration (AC: #6)

**Estimated Time:** 15 minutes

- [ ] Create Clerk account at https://clerk.com (use free development instance)
- [ ] Create new application in Clerk dashboard (name: "Delight Development")
- [ ] Configure allowed redirect URLs in Clerk dashboard:
  - Sign-in redirect: `http://localhost:3000`
  - Sign-up redirect: `http://localhost:3000`
  - After sign-out: `http://localhost:3000`
- [ ] Copy Publishable Key from API Keys section → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- [ ] Copy Secret Key from API Keys section → `CLERK_SECRET_KEY`
- [ ] Navigate to Webhooks section → Add Endpoint
- [ ] Set webhook URL: `http://localhost:8000/api/v1/webhooks/clerk` (use ngrok for local testing)
- [ ] Subscribe to events: `user.created`, `user.updated`
- [ ] Copy Webhook Signing Secret → `CLERK_WEBHOOK_SECRET`
- [ ] Update `.env.example` files with all Clerk variables and explanatory comments

### Task 2: Implement Frontend Clerk Integration (AC: #1, #5)

**Estimated Time:** 45 minutes

- [ ] Install Clerk Next.js SDK:

  ```bash
  cd packages/frontend
  pnpm add @clerk/nextjs@^6.14.0
  ```

- [ ] Create `packages/frontend/.env.local` with:

  ```bash
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
  CLERK_SECRET_KEY=sk_test_...
  ```

- [ ] Modify `packages/frontend/src/middleware.ts`:

  ```typescript
  import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

  const isPublicRoute = createRouteMatcher([
    "/",
    "/sign-in(.*)",
    "/sign-up(.*)",
    "/api/v1/webhooks(.*)",
  ]);

  export default clerkMiddleware(async (auth, request) => {
    // Protect all routes except public ones
    if (!isPublicRoute(request)) {
      // auth() returns a promise, so await it first, then call protect()
      // protect() automatically redirects to sign-in if not authenticated
      (await auth()).protect();
    }
  });

  export const config = {
    matcher: [
      "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
      "/(api|trpc)(.*)",
    ],
  };
  ```

  **Note (2025-11-11):** Fixed middleware to use correct Clerk v5 API pattern. The `auth` parameter is a function that returns a promise, so we must `await auth()` first, then call `.protect()`. The original pattern `await auth.protect()` was incorrect and caused runtime errors.

- [ ] Modify `packages/frontend/src/app/layout.tsx` to add ClerkProvider:

  ```typescript
  import { ClerkProvider } from "@clerk/nextjs";

  export default function RootLayout({
    children,
  }: {
    children: React.ReactNode;
  }) {
    return (
      <ClerkProvider>
        <html lang="en">
          <body>{children}</body>
        </html>
      </ClerkProvider>
    );
  }
  ```

- [ ] Create `packages/frontend/src/app/sign-in/[[...sign-in]]/page.tsx`:

  ```typescript
  import { SignIn } from "@clerk/nextjs";

  export default function SignInPage() {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <SignIn />
      </div>
    );
  }
  ```

- [ ] Create `packages/frontend/src/app/sign-up/[[...sign-up]]/page.tsx`:

  ```typescript
  import { SignUp } from "@clerk/nextjs";

  export default function SignUpPage() {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <SignUp />
      </div>
    );
  }
  ```

- [ ] Create `packages/frontend/src/components/auth/UserMenu.tsx`:

  ```typescript
  "use client";

  import { UserButton, useUser } from "@clerk/nextjs";

  export function UserMenu() {
    const { isSignedIn, user } = useUser();

    if (!isSignedIn) {
      return (
        <div className="flex gap-2">
          <a href="/sign-in" className="btn btn-secondary">
            Sign In
          </a>
          <a href="/sign-up" className="btn btn-primary">
            Sign Up
          </a>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2">
        <span className="text-sm">
          Welcome, {user.firstName || user.emailAddresses[0].emailAddress}
        </span>
        <UserButton afterSignOutUrl="/" />
      </div>
    );
  }
  ```

- [ ] Create `packages/frontend/src/app/dashboard/page.tsx`:

  ```typescript
  export default function DashboardPage() {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 max-w-5xl w-full items-center justify-between text-center">
          <h1 className="text-4xl font-bold mb-4">Dashboard 🎯</h1>
          <p className="text-lg text-muted-foreground mb-8">
            Welcome to your Delight dashboard
          </p>
          {/* Dashboard content */}
        </div>
      </main>
    );
  }
  ```

  **Note (2025-11-11):** E2E tests expect a `/dashboard` route to exist for testing protected route access. This page should be created to satisfy test requirements.

- [ ] Test frontend authentication flow manually:
  - Navigate to protected route (should redirect to sign-in)
  - Complete sign-up flow
  - Verify redirect back to home
  - Check user menu displays

### Task 3: Implement Backend Authentication Dependencies (AC: #2, #4)

**Estimated Time:** 60 minutes

- [ ] Install backend Clerk dependencies:

  ```bash
  cd packages/backend
  poetry add pyclerk==0.3.0 svix==1.45.0
  ```

- [ ] Create `packages/backend/.env` with:

  ```bash
  CLERK_SECRET_KEY=sk_test_...
  CLERK_WEBHOOK_SECRET=whsec_...
  ```

- [ ] Modify `packages/backend/app/core/config.py` to add Clerk settings:

  ```python
  class Settings(BaseSettings):
      # ... existing settings ...

      # Clerk Authentication
      CLERK_SECRET_KEY: str
      CLERK_WEBHOOK_SECRET: str
      CLERK_API_URL: str = "https://api.clerk.com/v1"

      class Config:
          env_file = ".env"
  ```

- [ ] Create `packages/backend/app/core/clerk_auth.py`:

  ```python
  from typing import Optional
  from fastapi import Depends, HTTPException, status
  from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  from clerk_backend_api import Clerk
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import select

  from app.core.config import get_settings
  from app.db.session import get_db
  from app.models.user import User

  security = HTTPBearer()

  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(security),
      db: AsyncSession = Depends(get_db)
  ) -> User:
      """
      Validate Clerk session token and return authenticated user.

      Args:
          credentials: Bearer token from Authorization header
          db: Database session

      Returns:
          User: Authenticated user from database

      Raises:
          HTTPException: 401 if token invalid or user not found
      """
      settings = get_settings()
      clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

      try:
          # Verify session token with Clerk
          session = clerk.sessions.verify_token(credentials.credentials)
          clerk_user_id = session.user_id
      except Exception as e:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid authentication credentials",
              headers={"WWW-Authenticate": "Bearer"},
          )

      # Find user in database by clerk_user_id
      result = await db.execute(
          select(User).where(User.clerk_user_id == clerk_user_id)
      )
      user = result.scalar_one_or_none()

      if not user:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="User not found in database"
          )

      return user
  ```

- [ ] Create `packages/backend/app/schemas/user.py`:

  ```python
  from pydantic import BaseModel, EmailStr
  from datetime import datetime
  from uuid import UUID

  class UserResponse(BaseModel):
      id: UUID
      clerk_user_id: str
      email: str | None
      display_name: str | None
      created_at: datetime
      updated_at: datetime

      model_config = {"from_attributes": True}
  ```

- [ ] Create `packages/backend/app/api/v1/users.py`:

  ```python
  from fastapi import APIRouter, Depends
  from app.core.clerk_auth import get_current_user
  from app.models.user import User
  from app.schemas.user import UserResponse

  router = APIRouter(prefix="/users", tags=["users"])

  @router.get("/me", response_model=UserResponse)
  async def get_current_user_profile(
      current_user: User = Depends(get_current_user)
  ):
      """Get authenticated user's profile."""
      return current_user
  ```

- [ ] Register users router in `packages/backend/app/api/v1/__init__.py`:

  ```python
  from fastapi import APIRouter
  from app.api.v1 import health, users

  api_router = APIRouter()
  api_router.include_router(health.router)
  api_router.include_router(users.router)
  ```

- [ ] Test protected endpoint manually:
  - Start backend: `poetry run uvicorn main:app --reload`
  - Test without token: `curl http://localhost:8000/api/v1/users/me` (expect 403)
  - Get token from frontend after sign-in
  - Test with token: `curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/users/me`

### Task 4: Implement Clerk Webhook Handler (AC: #3)

**Estimated Time:** 75 minutes

- [ ] Create `packages/backend/app/schemas/webhook.py`:

  ```python
  from pydantic import BaseModel
  from typing import Literal

  class ClerkEmailAddress(BaseModel):
      email_address: str

  class ClerkUserData(BaseModel):
      id: str  # clerk_user_id
      email_addresses: list[ClerkEmailAddress]
      first_name: str | None = None
      last_name: str | None = None

  class ClerkWebhookPayload(BaseModel):
      type: Literal["user.created", "user.updated"]
      data: ClerkUserData
  ```

- [ ] Create `packages/backend/app/services/clerk_service.py`:

  ```python
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import select
  from app.models.user import User
  from app.schemas.webhook import ClerkUserData

  class ClerkService:
      """Service for handling Clerk user synchronization."""

      @staticmethod
      async def create_or_update_user(
          db: AsyncSession,
          clerk_data: ClerkUserData
      ) -> User:
          """
          Create or update user from Clerk webhook data.
          Idempotent operation - safe to call multiple times.

          Args:
              db: Database session
              clerk_data: User data from Clerk webhook

          Returns:
              User: Created or updated user record
          """
          # Extract email (primary email address)
          email = None
          if clerk_data.email_addresses:
              email = clerk_data.email_addresses[0].email_address

          # Construct display name
          display_name = None
          if clerk_data.first_name or clerk_data.last_name:
              parts = filter(None, [clerk_data.first_name, clerk_data.last_name])
              display_name = " ".join(parts)

          # Check if user exists
          result = await db.execute(
              select(User).where(User.clerk_user_id == clerk_data.id)
          )
          user = result.scalar_one_or_none()

          if user:
              # Update existing user
              user.email = email
              user.display_name = display_name
          else:
              # Create new user
              user = User(
                  clerk_user_id=clerk_data.id,
                  email=email,
                  display_name=display_name
              )
              db.add(user)

          await db.commit()
          await db.refresh(user)
          return user
  ```

- [ ] Create `packages/backend/app/api/v1/webhooks.py`:

  ```python
  from fastapi import APIRouter, Request, HTTPException, Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from svix.webhooks import Webhook, WebhookVerificationError
  import logging

  from app.core.config import get_settings
  from app.db.session import get_db
  from app.schemas.webhook import ClerkWebhookPayload
  from app.services.clerk_service import ClerkService

  router = APIRouter(prefix="/webhooks", tags=["webhooks"])
  logger = logging.getLogger(__name__)

  @router.post("/clerk")
  async def clerk_webhook_handler(
      request: Request,
      db: AsyncSession = Depends(get_db)
  ):
      """
      Handle Clerk user lifecycle webhooks.
      Validates webhook signature and syncs user data to database.

      Events handled:
      - user.created: Create new user in database
      - user.updated: Update existing user in database
      """
      settings = get_settings()

      # Get webhook headers for signature verification
      svix_id = request.headers.get("svix-id")
      svix_timestamp = request.headers.get("svix-timestamp")
      svix_signature = request.headers.get("svix-signature")

      if not all([svix_id, svix_timestamp, svix_signature]):
          raise HTTPException(status_code=400, detail="Missing webhook headers")

      # Get raw body
      body = await request.body()

      # Verify webhook signature
      wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
      try:
          payload = wh.verify(body, {
              "svix-id": svix_id,
              "svix-timestamp": svix_timestamp,
              "svix-signature": svix_signature
          })
      except WebhookVerificationError as e:
          logger.error(f"Webhook verification failed: {e}")
          raise HTTPException(status_code=400, detail="Invalid webhook signature")

      # Parse and validate payload
      try:
          webhook_data = ClerkWebhookPayload.model_validate(payload)
      except Exception as e:
          logger.error(f"Invalid webhook payload: {e}")
          raise HTTPException(status_code=400, detail="Invalid payload format")

      # Handle event
      try:
          if webhook_data.type in ["user.created", "user.updated"]:
              user = await ClerkService.create_or_update_user(db, webhook_data.data)
              logger.info(
                  f"User synced: {user.clerk_user_id} ({webhook_data.type})",
                  extra={"clerk_user_id": user.clerk_user_id, "event_type": webhook_data.type}
              )
          else:
              logger.warning(f"Unhandled event type: {webhook_data.type}")
      except Exception as e:
          logger.error(f"Error processing webhook: {e}", exc_info=True)
          raise HTTPException(status_code=500, detail="Internal server error")

      return {"status": "success"}
  ```

- [ ] Register webhooks router in `packages/backend/app/api/v1/__init__.py`:

  ```python
  from app.api.v1 import health, users, webhooks

  api_router.include_router(webhooks.router)
  ```

- [ ] Ensure `main.py` includes the api_router:

  ```python
  from app.api.v1 import api_router

  app.include_router(api_router, prefix="/api/v1")
  ```

- [ ] Test webhook with Clerk dashboard "Send Test" feature:
  - Use ngrok to expose localhost:8000 to internet
  - Update webhook URL in Clerk to ngrok URL
  - Send test `user.created` event
  - Check backend logs for webhook received
  - Verify user created in Supabase

### Task 5: Integration and E2E Testing (AC: #7)

**Estimated Time:** 60 minutes

- [ ] Create `packages/backend/tests/integration/test_webhooks.py`:

  ```python
  import pytest
  from httpx import AsyncClient
  from sqlalchemy import select
  from app.models.user import User
  from svix.webhooks import Webhook

  @pytest.mark.asyncio
  async def test_user_created_webhook(client: AsyncClient, db_session, settings):
      """Test user.created webhook creates new user."""
      payload = {
          "type": "user.created",
          "data": {
              "id": "user_test123",
              "email_addresses": [{"email_address": "test@example.com"}],
              "first_name": "Test",
              "last_name": "User"
          }
      }

      # Sign payload with Svix
      wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
      headers = wh.sign("webhook_endpoint", payload)

      response = await client.post(
          "/api/v1/webhooks/clerk",
          json=payload,
          headers=headers
      )

      assert response.status_code == 200

      # Verify user created
      result = await db_session.execute(
          select(User).where(User.clerk_user_id == "user_test123")
      )
      user = result.scalar_one()
      assert user.email == "test@example.com"
      assert user.display_name == "Test User"

  @pytest.mark.asyncio
  async def test_webhook_invalid_signature(client: AsyncClient):
      """Test webhook rejects invalid signature."""
      payload = {"type": "user.created", "data": {"id": "test"}}

      response = await client.post(
          "/api/v1/webhooks/clerk",
          json=payload,
          headers={
              "svix-id": "invalid",
              "svix-timestamp": "invalid",
              "svix-signature": "invalid"
          }
      )

      assert response.status_code == 400
  ```

- [ ] Create `packages/backend/tests/integration/test_auth.py`:

  ```python
  import pytest
  from httpx import AsyncClient
  from unittest.mock import patch, MagicMock

  @pytest.mark.asyncio
  async def test_get_current_user_success(client: AsyncClient, test_user):
      """Test /users/me returns user data with valid token."""
      with patch('app.core.clerk_auth.Clerk') as mock_clerk:
          mock_session = MagicMock()
          mock_session.user_id = test_user.clerk_user_id
          mock_clerk.return_value.sessions.verify_token.return_value = mock_session

          response = await client.get(
              "/api/v1/users/me",
              headers={"Authorization": "Bearer fake_token"}
          )

      assert response.status_code == 200
      data = response.json()
      assert data["clerk_user_id"] == test_user.clerk_user_id

  @pytest.mark.asyncio
  async def test_get_current_user_no_token(client: AsyncClient):
      """Test /users/me returns 403 without token."""
      response = await client.get("/api/v1/users/me")
      assert response.status_code == 403
  ```

- [ ] Create `packages/frontend/tests/e2e/auth.spec.ts`:

  ```typescript
  import { test, expect } from "@playwright/test";

  /**
   * Helper: Click Clerk submit button (handles visibility issues)
   * Clerk buttons may have aria-hidden="true" which makes them invisible to Playwright
   */
  async function clickClerkSubmitButton(page: any) {
    const button = page.locator('button[type="submit"]').first();
    await button.waitFor({ state: "attached", timeout: 5000 });

    // Remove aria-hidden and force visibility
    await button.evaluate((btn: HTMLButtonElement) => {
      if (btn.hasAttribute("aria-hidden")) {
        btn.removeAttribute("aria-hidden");
      }
      btn.style.visibility = "visible";
      btn.style.display = "block";
    });

    await page.waitForTimeout(200);

    try {
      await button.click({ timeout: 2000 });
    } catch {
      await button.click({ force: true });
    }
  }

  test.describe("Authentication Flow", () => {
    test("redirects unauthenticated user to sign-in", async ({ page }) => {
      await page.goto("/dashboard"); // Protected route
      await expect(page).toHaveURL(/.*sign-in.*/);
    });

    test("sign-up and sign-in flow", async ({ page }) => {
      // Note: Use Clerk test mode credentials
      await page.goto("/sign-up");
      await expect(page.locator('input[name="emailAddress"]')).toBeVisible();

      // Use helper for submit buttons
      await page.fill('input[name="emailAddress"]', "test@example.com");
      await page.fill('input[name="password"]', "TestPassword123!");
      await clickClerkSubmitButton(page);
    });
  });
  ```

  **Note (2025-11-11):** Clerk's submit buttons may have `aria-hidden="true"` which causes Playwright to fail with "element is not visible" errors. Added `clickClerkSubmitButton()` helper function that removes the aria-hidden attribute and forces visibility before clicking. All submit button clicks in tests should use this helper.

- [ ] Update `packages/backend/tests/conftest.py` to add test user fixture:

  ```python
  @pytest.fixture
  async def test_user(db_session):
      """Create test user fixture."""
      from app.models.user import User

      user = User(
          clerk_user_id="user_test_fixture",
          email="fixture@test.com",
          display_name="Test Fixture User"
      )
      db_session.add(user)
      await db_session.commit()
      await db_session.refresh(user)
      return user
  ```

- [ ] Run all tests:

  ```bash
  # Backend tests
  cd packages/backend
  poetry run pytest tests/integration/test_webhooks.py -v
  poetry run pytest tests/integration/test_auth.py -v

  # Frontend E2E tests
  cd packages/frontend
  pnpm test:e2e
  ```

### Task 6: Documentation and Manual Testing (AC: #7)

**Estimated Time:** 45 minutes

- [ ] Update `README.md` with Clerk setup section:

  ````markdown
  ## Authentication Setup (Clerk)

  ### Quick Start (5 minutes)

  1. **Create Clerk Account**: Visit https://clerk.com and sign up
  2. **Create Application**: Click "Add application" → Name it "Delight Development"
  3. **Copy API Keys**:
     - Frontend: Copy `Publishable Key` → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
     - Backend: Copy `Secret Key` → `CLERK_SECRET_KEY`
  4. **Setup Webhook**:
     - Navigate to Webhooks → Add Endpoint
     - URL: `http://localhost:8000/api/v1/webhooks/clerk` (use ngrok for local)
     - Events: Select `user.created` and `user.updated`
     - Copy `Signing Secret` → `CLERK_WEBHOOK_SECRET`
  5. **Configure Environment**:

     ```bash
     # Frontend (.env.local)
     NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
     CLERK_SECRET_KEY=sk_test_xxx

     # Backend (.env)
     CLERK_SECRET_KEY=sk_test_xxx
     CLERK_WEBHOOK_SECRET=whsec_xxx
     ```
  ````

  6. **Test**: Start both servers and visit http://localhost:3000/sign-up

  ```

  ```

- [ ] Update `docs/SETUP.md` with detailed Clerk configuration instructions

- [ ] Update `packages/backend/.env.example`:

  ```bash
  # Clerk Authentication (Required)
  CLERK_SECRET_KEY=sk_test_...  # Get from Clerk Dashboard → API Keys
  CLERK_WEBHOOK_SECRET=whsec_...  # Get from Clerk Dashboard → Webhooks
  ```

- [ ] Update `packages/frontend/.env.example`:

  ```bash
  # Clerk Authentication (Required)
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...  # Public key (safe for client)
  CLERK_SECRET_KEY=sk_test_...  # Secret key (server-side middleware only)
  ```

- [ ] Create manual testing checklist and execute:

  ```markdown
  ## Manual Testing Checklist

  ### Sign-up Flow

  - [ ] Visit http://localhost:3000
  - [ ] Click "Sign Up" button
  - [ ] Complete sign-up with email/password
  - [ ] Verify redirect to home page
  - [ ] Check Supabase: user record exists with clerk_user_id

  ### Sign-in Flow

  - [ ] Sign out from current session
  - [ ] Navigate to protected route (e.g., /companion)
  - [ ] Verify redirect to /sign-in
  - [ ] Sign in with credentials
  - [ ] Verify redirect back to /companion

  ### Webhook Sync

  - [ ] Sign up new user in frontend
  - [ ] Check backend logs: webhook received message
  - [ ] Verify Supabase: user record created
  - [ ] Update name in Clerk dashboard
  - [ ] Trigger test webhook
  - [ ] Verify Supabase: display_name updated

  ### API Authentication

  - [ ] Sign in to frontend
  - [ ] Open browser DevTools → Network tab
  - [ ] Make request to /api/v1/users/me
  - [ ] Verify 200 response with user data
  - [ ] Copy Authorization header
  - [ ] Test with curl: `curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/users/me`
  - [ ] Test without token: expect 403 error
  - [ ] Test with invalid token: expect 401 error

  ### Edge Cases

  - [ ] Sign out while on protected route → redirects to sign-in
  - [ ] Navigate to /sign-in when already signed in → redirects to home
  - [ ] Close browser and reopen → session persists
  - [ ] Attempt to sign up with duplicate email → Clerk prevents
  ```

- [ ] Document test results and any issues discovered

## Dependencies

### From Story 1.1 (Monorepo Structure)

**Required Files:**

- ✅ `packages/frontend/src/middleware.ts` (exists, needs modification)
- ✅ `packages/frontend/src/app/layout.tsx` (exists, needs modification)
- ✅ `packages/backend/app/core/config.py` (exists, needs modification)
- ✅ `packages/backend/main.py` (exists, needs router registration)

### From Story 1.2 (Database Schema)

**Required:**

- ✅ Supabase PostgreSQL database configured with DATABASE_URL
- ✅ `users` table with columns: `id`, `clerk_user_id`, `email`, `display_name`, `created_at`, `updated_at`
- ✅ `User` model in `packages/backend/app/models/user.py`
- ✅ `get_db()` dependency in `packages/backend/app/db/session.py`
- ✅ Alembic migrations working

**Database Verification:**

```sql
-- Verify users table schema from Story 1.2
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';
```

### External Services

**Clerk (Required):**

- Free tier account at https://clerk.com
- Development application created
- API keys: Publishable Key, Secret Key
- Webhook endpoint configured with signing secret

**Supabase (Already Configured):**

- DATABASE_URL from Story 1.2
- Access to `users` table

## Technical Notes

### Package Versions

**Frontend:**

- `@clerk/nextjs@^6.14.0` - Latest version with Next.js 15 App Router support

**Backend:**

- `pyclerk==0.3.0` - Official Clerk Python SDK
- `svix==1.45.0` - Webhook signature validation (Clerk uses Svix standard)

### Test Database Isolation

**Critical Implementation Detail (2025-11-11):**

The test suite uses a three-layer protection system to ensure tests never access production databases:

1. **Separate Configuration:** Tests use `TEST_DATABASE_URL` (defaults to in-memory SQLite), production uses `DATABASE_URL`
2. **Separate Engines:** Test fixtures create a completely separate SQLAlchemy engine from the production one
3. **Dependency Override:** FastAPI's `app.dependency_overrides` replaces `get_db()` with a test version that uses the test database

This is implemented in `packages/backend/tests/conftest.py`. See the "Test/Production Database Separation" section below for complete details.

**Why This Matters:**

- Prevents accidental data corruption in production/development databases
- Allows tests to run safely in any environment
- Enables parallel test execution without conflicts
- Ensures CI/CD pipelines can run tests without production database access

### Security Considerations

1. **Webhook Signature Verification:**

   - All webhook requests validated with Svix signature
   - Prevents unauthorized user creation/modification
   - 5-minute timestamp tolerance prevents replay attacks

2. **Token Handling:**

   - Session tokens never logged (sanitized in error messages)
   - Tokens expire after 1 hour (Clerk default)
   - Invalid tokens return generic "Authentication failed" message

3. **CORS Configuration:**

   - Backend only allows requests from `http://localhost:3000` in development
   - Production: Configure to allow only deployed frontend domain

4. **Environment Variables:**
   - `CLERK_SECRET_KEY` used in both frontend (middleware) and backend
   - Frontend publishable key is public (safe for client-side)
   - Webhook secret only in backend environment

### Error Handling

**Frontend:**

- Clerk components handle auth errors automatically
- Middleware redirects unauthorized requests to `/sign-in`
- Session errors show user-friendly messages

**Backend:**

- 401 Unauthorized: Invalid/expired token
- 403 Forbidden: Missing Authorization header
- 400 Bad Request: Invalid webhook signature or payload
- 500 Internal Server Error: Database or processing errors

### Performance

- Token validation: < 100ms (Clerk API call)
- Webhook processing: < 500ms (database upsert)
- User lookup: < 50ms (indexed on clerk_user_id)

## Risk Mitigation

1. **Webhook Duplicate Events:**

   - Mitigation: Idempotent `create_or_update_user()` function
   - Uses `clerk_user_id` as unique identifier

2. **Token Passing Frontend → Backend:**

   - Mitigation: Use Clerk's `useAuth()` hook with `getToken()`
   - Test token format in integration tests

3. **Session Persistence:**
   - Mitigation: Clerk manages cookies automatically
   - Test browser refresh and new tab scenarios

## Future Enhancements (Out of Scope)

- Multi-factor authentication (Clerk supports, but not tested in this story)
- Custom email templates (use Clerk defaults for MVP)
- User profile editing UI (future story)
- Role-based access control (future epic)
- SSO/SAML integration (enterprise feature)

## References

- [Clerk Next.js 15 App Router Guide](https://clerk.com/docs/quickstarts/nextjs)
- [Clerk Webhooks Documentation](https://clerk.com/docs/integrations/webhooks/overview)
- [Svix Webhook Verification](https://docs.svix.com/receiving/verifying-payloads/how)
- Story 1.1: Initialize Monorepo Structure (DONE)
- Story 1.2: Set Up Database Schema (DONE)
- Epic 1 Technical Specification: docs/tech-spec-epic-1.md

## Test/Production Database Separation

**IMPORTANT:** Tests are completely isolated from production/development databases through multiple layers of protection.

### How Separation Works

#### 1. Separate Database Configuration

- **Tests use:** `TEST_DATABASE_URL` environment variable (defaults to in-memory SQLite)
- **Production uses:** `DATABASE_URL` environment variable (never accessed by tests)
- The test fixture explicitly reads `TEST_DATABASE_URL`, never `DATABASE_URL`

#### 2. Separate Database Engines

```python
# Test engine (created in tests/conftest.py)
async_engine = create_async_engine(test_database_url)  # Uses TEST_DATABASE_URL

# Production engine (in app/db/session.py)
engine = create_async_engine(settings.async_database_url)  # Uses DATABASE_URL
```

These are completely separate engines with separate connections.

#### 3. FastAPI Dependency Override

The `client` fixture in `tests/conftest.py` overrides the `get_db()` dependency:

```python
app.dependency_overrides[get_db] = override_get_db  # Uses test_session_factory
```

This ensures:

- When tests call API endpoints, `get_db()` is replaced with test version
- Production `get_db()` is **never called** during tests
- All database operations use the test database

### Safety Features

1. **Warning System:** If `TEST_DATABASE_URL` accidentally matches `DATABASE_URL`, a warning is displayed
2. **Automatic Cleanup:** Dependency overrides are cleared after each test
3. **Isolation:** Test database is created fresh for each test session
4. **No Environment Pollution:** Tests don't modify `DATABASE_URL` environment variable

### Visual Flow

```
Production Request:
  FastAPI → get_db() → AsyncSessionLocal → Production Engine → DATABASE_URL

Test Request:
  FastAPI → override_get_db() → test_session_factory → Test Engine → TEST_DATABASE_URL
```

### Configuration

- **Local Development:** Uses in-memory SQLite (no setup needed)
- **CI/CD:** Set `TEST_DATABASE_URL` to a dedicated PostgreSQL test database
- **Production:** Uses `DATABASE_URL` (never touched by tests)

### Implementation Details

The test setup in `packages/backend/tests/conftest.py` includes:

- `test_database_url` fixture: Provides test database URL (reads `TEST_DATABASE_URL`)
- `async_engine` fixture: Creates test database engine and tables
- `test_session_factory` fixture: Creates session factory from test engine
- `client` fixture: Overrides `get_db()` dependency to use test database

**Key Safety Guarantee:** Tests can **never** accidentally access production data. The separation is enforced at multiple levels, with FastAPI's dependency override system as the primary mechanism.

## Change Log

| Date       | Author             | Change Description                                                                                                                                                                                                                                                                                                                                                          |
| ---------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2025-01-27 | Auto (AI Reviewer) | Senior Developer Review notes appended. Outcome: Changes Requested. Critical security issue identified: JWT signature verification not implemented in `get_current_user()`. Review found 5 of 7 ACs fully implemented, 2 partial. Comprehensive test coverage (55 tests) verified. Action items: Implement JWT verification, verify .env.example files, remove unused code. |
| 2025-11-11 | Auto               | Fixed test database separation: Removed fragile environment variable manipulation, implemented proper FastAPI dependency override system. Tests now use `TEST_DATABASE_URL` with explicit dependency override to ensure production database is never accessed. Added comprehensive documentation in conftest.py explaining the three-layer protection system.               |
| 2025-11-11 | Auto               | Fixed middleware to use correct Clerk v5 API: `(await auth()).protect()` instead of `await auth.protect()`. Created dashboard page for E2E tests. Added `clickClerkSubmitButton()` helper to handle Clerk button visibility issues in tests.                                                                                                                                |
| 2025-11-10 | Claude (via BMM)   | Story regenerated with improved clarity and structure                                                                                                                                                                                                                                                                                                                       |
| 2025-11-10 | SM                 | Initial draft with comprehensive requirements                                                                                                                                                                                                                                                                                                                               |

## Completion Checklist

- [ ] All 7 acceptance criteria verified
- [ ] Clerk account created and configured
- [ ] Frontend integration complete (middleware, pages, components)
- [ ] Backend auth dependencies implemented
- [ ] Webhook handler functional and tested
- [ ] Protected endpoints secured
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Manual testing checklist 100% complete
- [ ] Documentation updated (README, SETUP, API docs)
- [ ] Code reviewed and approved
- [ ] Story marked as "done" in sprint-status.yaml

---

## Senior Developer Review (AI) (OVERRIDE: THIS IS A JUNIOR DEVELOPER WE NEED A SENIOR DEVELOPER LIKE SONNET 4.5)

**Reviewer:** Auto (AI Code Reviewer)  
**Date:** 2025-11-11
**Outcome:** 🔴 **CHANGES REQUESTED** - Critical security issue must be resolved before approval

### Summary

Story 1.3 implements Clerk authentication integration with comprehensive test coverage and solid architectural patterns. The implementation covers all major acceptance criteria with well-structured code, excellent test suites (37 backend + 18 frontend tests), and proper separation of concerns. However, **a critical security vulnerability exists**: JWT token signature verification is not implemented, leaving the authentication system vulnerable to token forgery. This must be fixed before production deployment.

**Key Strengths:**

- Comprehensive test coverage (55 total tests)
- Well-structured code with clear separation of concerns
- Proper error handling and logging
- Excellent webhook security (Svix signature verification)
- Good documentation and code comments

**Critical Issues:**

- JWT signature verification missing (HIGH severity)
- Missing `.env.example` files (documentation issue)

### Outcome: Changes Requested

**Justification:** While the implementation is functionally complete and well-tested, the missing JWT signature verification in `get_current_user()` creates a critical security vulnerability. The current implementation decodes tokens without verifying signatures, allowing attackers to forge authentication tokens. This must be fixed before the story can be approved.

### Key Findings

#### 🔴 HIGH Severity

1. **JWT Signature Verification Not Implemented** [file: `packages/backend/app/core/clerk_auth.py:86-103`]

   - **Issue:** Token verification only decodes JWT without signature validation
   - **Evidence:** Lines 88-103 show `jwt.decode(token, options={"verify_signature": False})` with TODO comment
   - **Risk:** Attackers can forge authentication tokens by creating JWTs with arbitrary `sub` claims
   - **Impact:** Complete authentication bypass possible
   - **AC Violation:** AC2 requires "Token validation uses official `pyclerk` SDK with proper error handling"
   - **Fix Required:** Implement proper JWT signature verification using Clerk's JWKS or secret key

2. **Missing Environment Variable Documentation** [file: `.env.example` files]
   - **Issue:** `.env.example` files are filtered by `.cursorignore` and cannot be verified
   - **Evidence:** File read attempts returned "filtered out by .cursorignore"
   - **AC Violation:** AC6 requires ".env.example files document all required variables"
   - **Fix Required:** Ensure `.env.example` files exist and are committed to repository

#### 🟡 MEDIUM Severity

3. **Unused Code in `clerk_auth.py`** [file: `packages/backend/app/core/clerk_auth.py:19-40`]

   - **Issue:** `get_clerk_jwks()` function is defined but never used
   - **Evidence:** Function exists but returns `None` and is not called
   - **Impact:** Code clutter, suggests incomplete implementation
   - **Fix Required:** Either implement JWKS fetching or remove unused function

4. **Missing Error Context in Webhook Handler** [file: `packages/backend/app/api/v1/webhooks.py:95-97`]
   - **Issue:** Generic error message doesn't provide debugging context
   - **Evidence:** Line 96 logs error but raises generic "Internal server error"
   - **Impact:** Difficult to debug production issues
   - **Fix Required:** Add structured error logging with request context

#### 🟢 LOW Severity

5. **Hardcoded Default Timezone** [file: `packages/backend/app/services/clerk_service.py:62`]

   - **Issue:** Timezone defaults to "UTC" without configuration option
   - **Evidence:** Line 62: `timezone="UTC"`
   - **Impact:** Minor - may need to be configurable in future
   - **Note:** Acceptable for MVP, consider making configurable later

6. **Missing Type Hints in Some Functions** [file: `packages/backend/app/api/v1/webhooks.py:25`]
   - **Issue:** Return type not explicitly annotated
   - **Evidence:** Function signature missing `-> dict` return type
   - **Impact:** Minor - reduces type checking benefits
   - **Fix Required:** Add return type annotation

### Acceptance Criteria Coverage

| AC# | Description                                | Status             | Evidence                                                                                                                                                                                                                   | Notes                                                                                                                                                                                                                  |
| --- | ------------------------------------------ | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC1 | Frontend Clerk Integration Complete        | ✅ **IMPLEMENTED** | `packages/frontend/src/middleware.ts:1-27`, `packages/frontend/src/app/layout.tsx:27-54`, `packages/frontend/src/app/sign-in/[[...sign-in]]/page.tsx:1-9`, `packages/frontend/src/app/sign-up/[[...sign-up]]/page.tsx:1-9` | All requirements met: middleware, ClerkProvider, sign-in/sign-up pages, route protection                                                                                                                               |
| AC2 | Backend Session Verification Working       | ⚠️ **PARTIAL**     | `packages/backend/app/core/clerk_auth.py:42-131`                                                                                                                                                                           | **CRITICAL:** Token decoding works but signature verification missing (lines 88-103). AC2 requires "Token validation uses official `pyclerk` SDK" - current implementation uses manual JWT decode without verification |
| AC3 | User Sync via Webhook Functional           | ✅ **IMPLEMENTED** | `packages/backend/app/api/v1/webhooks.py:21-99`, `packages/backend/app/services/clerk_service.py:16-68`                                                                                                                    | All requirements met: webhook endpoint, Svix verification, user.created/updated events, idempotency, logging                                                                                                           |
| AC4 | Protected API Endpoints Secured            | ✅ **IMPLEMENTED** | `packages/backend/app/api/v1/users.py:16-33`, `packages/backend/app/core/clerk_auth.py:42-131`                                                                                                                             | Endpoint implemented with proper dependency injection pattern                                                                                                                                                          |
| AC5 | Authentication State Managed in Frontend   | ✅ **IMPLEMENTED** | `packages/frontend/src/app/layout.tsx:31-47`                                                                                                                                                                               | Clerk SDK hooks available, UserButton component, sign-in/sign-out flows                                                                                                                                                |
| AC6 | Environment Variables Configured Correctly | ⚠️ **PARTIAL**     | `packages/backend/app/core/config.py:17-19`                                                                                                                                                                                | Config file has Clerk settings, but `.env.example` files cannot be verified (filtered by `.cursorignore`)                                                                                                              |
| AC7 | Complete Documentation and Testing         | ✅ **IMPLEMENTED** | `packages/backend/tests/integration/test_auth.py` (11 tests), `packages/backend/tests/integration/test_webhooks.py` (26 tests), `packages/frontend/tests/e2e/auth.spec.ts` (18 tests)                                      | Comprehensive test coverage: 55 total tests covering all major flows                                                                                                                                                   |

**Summary:** 5 of 7 acceptance criteria fully implemented, 2 partial (AC2 - security issue, AC6 - documentation verification blocked)

### Task Completion Validation

| Task                              | Marked As | Verified As    | Evidence                                                                                                   | Notes                                            |
| --------------------------------- | --------- | -------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Task 1: Setup Clerk Account       | [ ]       | N/A            | N/A                                                                                                        | Manual setup task, cannot verify via code        |
| Task 2: Frontend Integration      | [ ]       | ✅ **DONE**    | `packages/frontend/src/middleware.ts`, `packages/frontend/src/app/layout.tsx`, sign-in/sign-up pages exist | All subtasks completed                           |
| Task 3: Backend Auth Dependencies | [ ]       | ⚠️ **PARTIAL** | `packages/backend/app/core/clerk_auth.py` exists but missing signature verification                        | Core functionality works but security incomplete |
| Task 4: Webhook Handler           | [ ]       | ✅ **DONE**    | `packages/backend/app/api/v1/webhooks.py`, `packages/backend/app/services/clerk_service.py`                | Fully implemented with proper security           |
| Task 5: Integration Tests         | [ ]       | ✅ **DONE**    | `packages/backend/tests/integration/test_auth.py`, `packages/backend/tests/integration/test_webhooks.py`   | 37 comprehensive backend tests                   |
| Task 6: Documentation             | [ ]       | ⚠️ **PARTIAL** | Code is well-documented, but `.env.example` files cannot be verified                                       | Documentation in code is excellent               |

**Summary:** All code-related tasks are implemented. Manual setup tasks (Task 1) cannot be verified via code review. Task 3 has security gap that needs addressing.

### Test Coverage and Gaps

**Backend Tests (37 tests):**

- ✅ `test_auth.py`: 11 tests covering authentication dependency, token validation, protected endpoints
- ✅ `test_webhooks.py`: 26 tests covering signature validation, user creation/updates, idempotency, error handling
- ✅ Test helpers: `tests/helpers/auth.py` provides JWT token generation and user creation utilities
- ✅ Test isolation: Proper database transaction rollback, dependency overrides

**Frontend Tests (18 tests):**

- ✅ `auth.spec.ts`: Comprehensive E2E tests covering sign-up, sign-in, route protection, session persistence
- ✅ Clerk UI interaction helpers: `clickClerkSubmitButton()` handles visibility issues
- ✅ Test data management: Unique emails per run, reusable test credentials

**Test Quality:**

- ✅ Well-structured with clear docstrings
- ✅ Good edge case coverage (missing email, special characters, duplicate events)
- ✅ Security-focused (signature validation, token format validation)
- ✅ Proper fixtures and helpers

**Gaps:**

- ⚠️ No tests verify JWT signature verification (because it's not implemented)
- ⚠️ No performance/load tests (marked as optional/skipped)

### Architectural Alignment

**Tech Spec Compliance:**

- ✅ Uses FastAPI dependency injection pattern as specified
- ✅ Webhook endpoint matches spec: `/api/v1/webhooks/clerk`
- ✅ User endpoint matches spec: `/api/v1/users/me`
- ⚠️ **Deviation:** Tech spec (line 240) suggests using `clerk.sessions.verify_session()`, but implementation uses manual JWT decode

**Architecture Patterns:**

- ✅ Proper service layer separation (`ClerkService`)
- ✅ Schema validation with Pydantic
- ✅ Async/await patterns throughout
- ✅ Proper error handling with HTTPException
- ✅ Structured logging

**Code Organization:**

- ✅ Clear module structure
- ✅ Proper imports and dependencies
- ✅ Type hints used consistently (with minor gaps)

### Security Notes

**Strengths:**

1. ✅ **Webhook Security:** Proper Svix signature verification prevents unauthorized webhook requests
2. ✅ **Error Messages:** Generic error messages prevent information leakage (user enumeration protection)
3. ✅ **Input Validation:** Pydantic schemas validate all webhook payloads
4. ✅ **Database Security:** Uses parameterized queries (SQLAlchemy ORM) preventing SQL injection
5. ✅ **CORS Configuration:** Properly configured for development environment

**Critical Vulnerabilities:**

1. 🔴 **JWT Signature Verification Missing:** [file: `packages/backend/app/core/clerk_auth.py:86-103`]

   - Current code: `jwt.decode(token, options={"verify_signature": False})`
   - Risk: Attackers can forge tokens with arbitrary user IDs
   - Required Fix: Implement proper signature verification using Clerk's JWKS endpoint or secret key
   - Reference: [Clerk JWT Verification Docs](https://clerk.com/docs/backend-requests/handling/manual-jwt)

2. ⚠️ **Token Expiration Not Checked:** Even if signature verification is added, expiration claims should be validated
   - Current code extracts `sub` but doesn't check `exp` claim
   - Risk: Expired tokens could be used indefinitely

**Recommendations:**

- Implement JWKS-based verification for production (supports key rotation)
- Add token expiration validation
- Consider rate limiting for authentication endpoints
- Add request ID tracking for audit trails

### Best Practices and References

**Code Quality:**

- ✅ Follows PEP 8 (Python) and ESLint (TypeScript) standards
- ✅ Proper async/await usage
- ✅ Type hints used consistently
- ✅ Clear function and variable names
- ✅ Comprehensive docstrings

**Testing Best Practices:**

- ✅ Test isolation with database transactions
- ✅ Proper fixtures and helpers
- ✅ Edge case coverage
- ✅ Security-focused test cases

**References:**

- [Clerk Next.js 15 App Router Guide](https://clerk.com/docs/quickstarts/nextjs)
- [Clerk Webhooks Documentation](https://clerk.com/docs/integrations/webhooks/overview)
- [Svix Webhook Verification](https://docs.svix.com/receiving/verifying-payloads/how)
- [Clerk JWT Verification](https://clerk.com/docs/backend-requests/handling/manual-jwt)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### Action Items

#### Code Changes Required

- [ ] [HIGH] Implement JWT signature verification in `get_current_user()` (AC #2) [file: `packages/backend/app/core/clerk_auth.py:86-103`]

  - Use Clerk's JWKS endpoint for production: `https://[your-clerk-domain]/.well-known/jwks.json`
  - Or use `pyclerk` SDK's `authenticate_request()` method as specified in tech spec
  - Verify token signature, expiration, issuer, and audience claims
  - Remove `options={"verify_signature": False}` and implement proper verification
  - Reference: [Clerk JWT Verification Guide](https://clerk.com/docs/backend-requests/handling/manual-jwt)

- [ ] [HIGH] Verify and commit `.env.example` files (AC #6) [file: `packages/backend/.env.example`, `packages/frontend/.env.example`]

  - Ensure files exist and document all Clerk environment variables
  - Include security notes about secret key handling
  - Remove from `.cursorignore` if intentionally excluded, or ensure files are committed

- [ ] [MEDIUM] Remove or implement `get_clerk_jwks()` function [file: `packages/backend/app/core/clerk_auth.py:19-40`]

  - Either implement JWKS fetching for JWT verification, or remove unused function
  - If implementing, cache JWKS with appropriate TTL

- [ ] [MEDIUM] Add return type annotation to webhook handler [file: `packages/backend/app/api/v1/webhooks.py:25`]

  - Change: `async def clerk_webhook_handler(...)` → `async def clerk_webhook_handler(...) -> dict:`

- [ ] [MEDIUM] Improve error logging in webhook handler [file: `packages/backend/app/api/v1/webhooks.py:95-97`]

  - Add structured logging with request context (webhook ID, event type, user ID)
  - Include exception details in logs (not in response) for debugging

- [ ] [LOW] Add token expiration validation [file: `packages/backend/app/core/clerk_auth.py:88-103`]
  - After implementing signature verification, also validate `exp` claim
  - Return 401 if token is expired

#### Advisory Notes

- Note: Consider making default timezone configurable in future stories (currently hardcoded to "UTC")
- Note: Performance tests are marked as skipped - consider running manually before production deployment
- Note: Consider adding rate limiting for authentication endpoints in production
- Note: Webhook handler returns 200 for unhandled event types - this is correct behavior to prevent failures on new Clerk event types

---

**Review Status:** Changes Requested  
**Next Steps:** Address HIGH severity items (JWT verification, .env.example files) and re-submit for review

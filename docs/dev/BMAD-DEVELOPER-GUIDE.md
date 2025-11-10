# BMAD Developer Guide: Story Development Workflow

**Version:** 1.0.0  
**Project:** Delight  
**Last Updated:** 2025-11-10

---

## 📖 **About This Guide**

This guide provides a systematic, professional workflow for developing stories using the BMAD (Business-Managed Agile Development) methodology. Follow this workflow to:

- Build features efficiently and correctly
- Maintain high code quality
- Test thoroughly before deployment
- Document your work systematically
- Improve as a developer

**Philosophy:** Great developers aren't just fast coders—they're systematic, thorough, and disciplined. This guide helps you develop those habits.

---

## 🎯 **Table of Contents**

1. [Story Development Workflow](#story-development-workflow)
2. [BMAD Workflow Integration](#bmad-workflow-integration)
3. [Testing Guide](#testing-guide)
4. [Code Quality Standards](#code-quality-standards)
5. [Documentation Requirements](#documentation-requirements)
6. [Troubleshooting](#troubleshooting)
7. [Resources](#resources)

---

## 🔄 **Story Development Workflow**

### **Overview: The 6-Stage Process**

```
1. SELECT → 2. PREPARE → 3. DEVELOP → 4. TEST → 5. REVIEW → 6. COMPLETE
```

Each stage has specific deliverables and exit criteria. Never skip stages.

---

### **Stage 1: Story Selection & Planning**

#### **1.1 Select Your Next Story**

**Location:** `docs/sprint-status.yaml`

```yaml
# Find the first story with status "backlog" that has:
# - All prerequisites marked "done"
# - No blocking dependencies

1-1-initialize-monorepo-structure-and-core-dependencies: backlog  # ← Start here
```

**Exit Criteria:**
- ✅ Story selected
- ✅ Prerequisites verified as "done"
- ✅ No blockers identified

#### **1.2 Read & Understand the Story**

**Location:** `docs/epics.md`

Read the complete story:

```markdown
### Story X.Y: [Title]

As a [role],
I want [capability],
So that [benefit].

**Acceptance Criteria:**
Given [context]
When [action]
Then [outcome]

**Prerequisites:** [Required stories]

**Technical Notes:**
- Implementation guidance
- Architecture references
- Code examples
```

**What to Extract:**

1. **User Story** → Who benefits and why?
2. **Acceptance Criteria** → What defines "done"?
3. **Prerequisites** → What must be complete first?
4. **Technical Notes** → How should it be built?

**Exit Criteria:**
- ✅ Story fully read and understood
- ✅ Questions noted (ask before coding)
- ✅ Acceptance criteria clear

#### **1.3 Create Story Context (BMAD Workflow)**

**OPTIONAL BUT HIGHLY RECOMMENDED**

Use the BMAD workflow to break down the story:

```
@bmad/bmm/workflows/story-context
```

**What This Does:**
- Analyzes the story requirements
- Identifies all files to create/modify
- Creates implementation plan with steps
- Documents technical decisions
- Generates story context document

**Output:** `docs/stories/story-[X.Y]-context.md`

This gives you a roadmap before you start coding.

**Exit Criteria:**
- ✅ Story context created (or implementation plan documented)
- ✅ File list identified
- ✅ Technical approach decided

#### **1.4 Update Story Status**

**Location:** `docs/sprint-status.yaml`

```yaml
# Change status from "backlog" to "in-progress"
1-1-initialize-monorepo-structure-and-core-dependencies: in-progress
```

**Pro Tip:** Only have 1-2 stories "in-progress" at a time. Focus beats multitasking.

#### **1.5 Create Feature Branch**

```bash
# Create branch with story ID and short description
git checkout -b story/1-1-monorepo-setup

# Alternative naming patterns:
# git checkout -b 1-1-initialize-monorepo
# git checkout -b feature/story-1.1
```

**Commit message convention:**
```
Story [X.Y]: [Short title]

[Detailed description]

Acceptance criteria:
✅ Criterion 1
✅ Criterion 2
```

**Exit Criteria:**
- ✅ Branch created
- ✅ Working in feature branch (not main)

---

### **Stage 2: Development**

#### **2.1 Create Implementation Checklist**

Based on acceptance criteria, create a checklist:

```markdown
## Story 1.3: Integrate Clerk Authentication

### Implementation Checklist
- [ ] Install Clerk packages (frontend + backend)
- [ ] Configure Clerk project (API keys)
- [ ] Frontend: Wrap app in ClerkProvider
- [ ] Frontend: Create middleware for auth
- [ ] Backend: Create auth dependency
- [ ] Backend: Implement webhook endpoint
- [ ] Frontend: Add SignIn/SignOut components
- [ ] Test: Sign up flow
- [ ] Test: Sign in flow
- [ ] Test: Protected routes
- [ ] Test: Logout flow

### Files to Create
- packages/frontend/middleware.ts
- packages/backend/app/core/auth.py
- packages/backend/app/api/v1/webhooks/clerk.py

### Files to Modify
- packages/frontend/app/layout.tsx
- packages/backend/app/main.py
- packages/frontend/.env.local
- packages/backend/.env
```

**Exit Criteria:**
- ✅ Checklist created with all acceptance criteria
- ✅ File list identified

#### **2.2 Set Up Development Environment**

```bash
# Start required services
docker-compose up -d

# Backend (Terminal 1)
cd packages/backend
poetry shell
poetry run uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd packages/frontend
npm run dev

# Tests in watch mode (Terminal 3 - optional)
cd packages/backend
poetry run pytest-watch
```

**Exit Criteria:**
- ✅ All services running
- ✅ Dev servers accessible
- ✅ No startup errors

#### **2.3 Implement Feature (TDD Approach - Recommended)**

**Test-Driven Development Cycle:**

```
1. Write test (fails) → 2. Write code (passes) → 3. Refactor → Repeat
```

**Example:**

```python
# Step 1: Write failing test
def test_protected_endpoint_requires_auth():
    """AC: Backend validates Clerk session"""
    response = client.get("/api/v1/protected-route")
    assert response.status_code == 401  # FAILS - endpoint doesn't exist yet

# Step 2: Implement endpoint
@app.get("/api/v1/protected-route")
async def protected_route(user = Depends(get_current_user)):
    return {"message": "success"}

# Step 3: Test passes, refactor if needed
```

**Alternative: Code-First Approach**

If not using TDD:

1. Implement feature code
2. Test manually (use the app)
3. Write automated tests
4. Refactor

**Development Best Practices:**

- ✅ **Commit frequently** - Small, logical commits
- ✅ **Test as you go** - Don't wait until the end
- ✅ **Follow conventions** - snake_case (Python), camelCase (TypeScript)
- ✅ **Add error handling** - Don't assume happy path
- ✅ **Write comments** - Explain "why", not "what"

**Exit Criteria:**
- ✅ All checklist items implemented
- ✅ No console errors
- ✅ Manual testing shows it works

#### **2.4 Code Quality Check**

Before moving to testing stage:

```bash
# Backend: Format and lint
cd packages/backend
poetry run black .               # Format code
poetry run ruff check .          # Lint
poetry run mypy app              # Type checking

# Frontend: Format and lint
cd packages/frontend
npm run lint                     # ESLint
npm run format                   # Prettier (if configured)
npm run type-check              # TypeScript check
```

**Fix all warnings and errors before proceeding.**

**Exit Criteria:**
- ✅ No linting errors
- ✅ Code formatted consistently
- ✅ Type checking passes

---

### **Stage 3: Testing**

**The Testing Pyramid:**

```
        ╱╲
       ╱  ╲
      ╱ E2E ╲           Few: Complex workflows
     ╱──────╲
    ╱ Integra-╲         Some: API + DB + UI
   ╱  tion     ╲
  ╱────────────╲
 ╱    Unit      ╲      Many: Individual functions
╱────────────────╲
```

#### **3.1 Manual Testing (Required)**

**Test EVERY Acceptance Criterion manually first.**

**Create Testing Document:**

`docs/stories/story-[X.Y]-testing.md`

```markdown
# Story 1.3: Clerk Authentication - Testing Report

## Manual Testing

### AC 1: User can sign up with email/password
**Steps:**
1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Enter email: test@example.com
4. Enter password: Test123!
5. Submit form

**Expected:** Account created, redirected to dashboard
**Actual:** ✅ Account created, redirected to dashboard
**Status:** ✅ PASS
**Evidence:** Screenshot saved to `docs/stories/testing/1-3-signup.png`

### AC 2: User can sign in with Google OAuth
[Same format]
```

**Manual Testing Checklist:**

```markdown
### Happy Path Testing
- [ ] AC 1: [Description] → ✅ Pass / ❌ Fail
- [ ] AC 2: [Description] → ✅ Pass / ❌ Fail
- [ ] AC 3: [Description] → ✅ Pass / ❌ Fail

### Edge Cases
- [ ] Invalid credentials → Shows error message
- [ ] Network failure → Shows retry option
- [ ] Missing required fields → Shows validation errors
- [ ] Session expired → Redirects to login

### Cross-Browser (if UI)
- [ ] Chrome ✅
- [ ] Firefox ✅
- [ ] Safari ✅
- [ ] Mobile Chrome ✅
```

**Exit Criteria:**
- ✅ All acceptance criteria tested manually
- ✅ All tests pass
- ✅ Edge cases covered
- ✅ Testing document created

#### **3.2 Unit Testing (Recommended)**

**Backend Unit Tests**

Location: `packages/backend/tests/test_[module].py`

```python
# packages/backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthentication:
    """Tests for Story 1.3: Clerk Authentication"""
    
    def test_protected_route_without_auth_returns_401(self):
        """AC: Backend validates Clerk session"""
        response = client.get("/api/v1/protected-route")
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_protected_route_with_valid_token_returns_200(self):
        """AC: Authenticated requests grant access"""
        headers = {"Authorization": "Bearer valid-clerk-token"}
        response = client.get("/api/v1/protected-route", headers=headers)
        assert response.status_code == 200
    
    def test_webhook_creates_user_on_clerk_signup(self):
        """AC: User record created in database"""
        payload = {
            "type": "user.created",
            "data": {
                "id": "user_123",
                "email_addresses": [{"email_address": "test@example.com"}]
            }
        }
        response = client.post("/api/v1/webhooks/clerk", json=payload)
        assert response.status_code == 200
        # Verify user created in DB
        # user = db.query(User).filter_by(clerk_user_id="user_123").first()
        # assert user is not None
```

**Frontend Unit Tests**

Location: `packages/frontend/__tests__/[component].test.tsx`

```typescript
// packages/frontend/__tests__/auth.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { ClerkProvider } from '@clerk/nextjs';
import { AuthGuard } from '@/components/AuthGuard';

describe('Story 1.3: Clerk Authentication', () => {
  it('should render sign in button when not authenticated', () => {
    render(
      <ClerkProvider publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}>
        <AuthGuard>Protected Content</AuthGuard>
      </ClerkProvider>
    );
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
  
  it('should show protected content when authenticated', async () => {
    // Mock authenticated state
    // ... test implementation
  });
});
```

**Run Unit Tests:**

```bash
# Backend
cd packages/backend
poetry run pytest -v --cov=app --cov-report=html

# Frontend
cd packages/frontend
npm test -- --coverage --watchAll=false

# View coverage reports
# Backend: open packages/backend/htmlcov/index.html
# Frontend: open packages/frontend/coverage/lcov-report/index.html
```

**Exit Criteria:**
- ✅ All critical paths have unit tests
- ✅ All tests pass
- ✅ Coverage ≥70% for backend, ≥60% for frontend (or project target)

#### **3.3 Integration Testing (For Complex Stories)**

Tests that verify multiple components work together.

**Backend Integration Tests**

```python
# packages/backend/tests/integration/test_auth_flow.py
import pytest
from sqlalchemy.orm import Session

class TestAuthIntegration:
    """Integration tests for authentication flow"""
    
    def test_complete_signup_flow(self, db: Session):
        """Test complete user signup and authentication"""
        # 1. Trigger Clerk webhook (user.created)
        webhook_response = client.post("/api/v1/webhooks/clerk", json={...})
        assert webhook_response.status_code == 200
        
        # 2. Verify user created in DB
        user = db.query(User).filter_by(clerk_user_id="user_123").first()
        assert user is not None
        
        # 3. Attempt authenticated request
        response = client.get("/api/v1/user/profile", headers={...})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
```

**Frontend E2E Tests (Playwright)**

Location: `packages/frontend/e2e/auth.spec.ts`

```typescript
// packages/frontend/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Story 1.3: Authentication Flow', () => {
  test('complete signup and login flow', async ({ page }) => {
    // 1. Navigate to app
    await page.goto('http://localhost:3000');
    
    // 2. Click sign up
    await page.click('text=Sign Up');
    
    // 3. Fill form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'Test123!');
    
    // 4. Submit
    await page.click('button[type="submit"]');
    
    // 5. Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // 6. Verify authenticated state
    await expect(page.locator('text=Welcome')).toBeVisible();
  });
});
```

**Run Integration Tests:**

```bash
# Backend integration tests
cd packages/backend
poetry run pytest tests/integration/ -v

# Frontend E2E tests
cd packages/frontend
npm run test:e2e
# Or with UI: npx playwright test --ui
```

**Exit Criteria:**
- ✅ Critical user journeys tested end-to-end
- ✅ All integration tests pass
- ✅ API + DB + UI work together

#### **3.4 Testing Checklist Summary**

```markdown
## Testing Completion Checklist

### Manual Testing
- [ ] All acceptance criteria tested manually
- [ ] Happy path verified
- [ ] Edge cases tested
- [ ] Error handling verified
- [ ] Testing document created

### Automated Testing
- [ ] Unit tests written for critical functions
- [ ] Integration tests written (if applicable)
- [ ] E2E tests written (for UI flows)
- [ ] All tests passing
- [ ] Coverage targets met

### Quality Checks
- [ ] No console errors
- [ ] No unhandled exceptions
- [ ] Performance acceptable
- [ ] Accessibility checked (if UI)
- [ ] Mobile responsive (if UI)
```

---

### **Stage 4: Code Review & Self-Review**

#### **4.1 Self-Review Checklist**

Before marking story as "done", review your own code:

```markdown
## Self-Review Checklist

### Code Quality
- [ ] Code follows project conventions
  - [ ] Backend: snake_case, PEP 8, type hints
  - [ ] Frontend: camelCase, ESLint rules, TypeScript strict
- [ ] No TODO comments left in code
- [ ] No console.log() or debug statements
- [ ] No commented-out code
- [ ] No hardcoded values (use config/env vars)

### Error Handling
- [ ] Try-catch blocks for async operations
- [ ] User-friendly error messages
- [ ] Errors logged appropriately
- [ ] Graceful degradation implemented

### Performance
- [ ] No N+1 queries (database)
- [ ] Appropriate indexes added
- [ ] Images optimized (if applicable)
- [ ] No memory leaks

### Security
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] SQL injection prevented (use ORM)
- [ ] XSS prevented (sanitize inputs)

### Testing
- [ ] All acceptance criteria tested
- [ ] Unit tests written
- [ ] Integration tests written (if needed)
- [ ] All tests passing
- [ ] Coverage targets met

### Documentation
- [ ] README updated (if needed)
- [ ] API endpoints documented
- [ ] New env vars documented
- [ ] Complex logic commented

### Integration
- [ ] Works with existing features
- [ ] No breaking changes
- [ ] Database migrations applied
- [ ] Backwards compatible (if versioned API)
```

**Pro Tip:** Take a 15-minute break before self-review. Fresh eyes catch more issues.

#### **4.2 Use BMAD Code Review Workflow (Optional)**

For collaborative projects:

```
@bmad/bmm/workflows/code-review
```

**What This Does:**
- Analyzes code changes
- Checks against best practices
- Identifies potential issues
- Generates review report

**Exit Criteria:**
- ✅ Self-review checklist complete
- ✅ All items checked off
- ✅ No blockers identified

#### **4.3 Update Story Status**

**Location:** `docs/sprint-status.yaml`

```yaml
# If working solo:
1-3-integrate-clerk-authentication-system: done

# If on a team:
1-3-integrate-clerk-authentication-system: review  # Wait for team review
```

---

### **Stage 5: Documentation & Commit**

#### **5.1 Update Documentation**

**Files to Update:**

1. **README.md** (if new setup required)
2. **API Documentation** (if new endpoints)
3. **Environment Variables** (if new vars added)

**Example: Update README for New Env Vars**

```markdown
## Environment Variables

### Backend (`packages/backend/.env`)

```bash
# Authentication (Story 1.3)
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_WEBHOOK_SECRET=your_clerk_webhook_secret
```

#### **5.2 Create Story Summary**

**Location:** `docs/stories/story-[X.Y]-summary.md`

```markdown
# Story 1.3: Clerk Authentication - Implementation Summary

**Status:** ✅ Complete  
**Developer:** Jack  
**Date:** 2025-11-10  
**Time Spent:** 6 hours

## What Was Built

- Clerk authentication integration with Next.js App Router
- Protected API routes with Clerk session verification
- User sync webhook endpoint (user.created, user.updated, user.deleted)
- Sign in/out UI components with OAuth support

## Files Created

- `packages/frontend/middleware.ts` - Auth middleware
- `packages/frontend/app/(auth)/sign-in/page.tsx` - Sign in page
- `packages/backend/app/core/auth.py` - Auth dependencies
- `packages/backend/app/api/v1/webhooks/clerk.py` - Webhook handler

## Files Modified

- `packages/frontend/app/layout.tsx` - Added ClerkProvider
- `packages/backend/app/main.py` - Added webhook routes
- `packages/frontend/.env.local` - Added Clerk keys
- `packages/backend/.env` - Added Clerk secrets

## Testing Results

### Manual Testing
- ✅ All acceptance criteria verified
- ✅ Edge cases tested (invalid credentials, expired session)
- ✅ Cross-browser tested (Chrome, Firefox, Safari)

### Automated Testing
- ✅ Unit tests: 8 passing
- ✅ Integration tests: 3 passing
- ✅ Coverage: Backend 82%, Frontend 67%

## Technical Decisions

**Why Clerk over custom JWT?**
- Reduces development time by 2-3 stories
- Provides OAuth, 2FA, magic links out-of-the-box
- Better security (managed service)
- Cost: Free tier covers MVP

**Webhook Architecture:**
- Clerk sends webhooks on user events → our backend syncs to DB
- Idempotent processing (handles duplicate webhooks)
- Validates webhook signatures for security

## Known Issues

None

## Next Steps

- Story 1.5: Set up deployment pipeline
- Story 2.1: Implement memory schema (requires auth)

## Lessons Learned

- Clerk middleware must be in root middleware.ts (not in app dir)
- Webhook signature validation is critical for security
- Type definitions from @clerk/nextjs are excellent
```

#### **5.3 Update Project Change Log**

**Location:** `.cursor-changes`

```markdown
## 2025-11-10: Story 1.3 Complete - Clerk Authentication

### Summary
Implemented Clerk authentication system with OAuth support, user sync webhooks, and protected routes.

### Changes Made
- Added Clerk authentication middleware
- Implemented user sync webhook
- Created sign in/out UI components
- Added authentication tests

### Technical Details
- Frontend: @clerk/nextjs with App Router
- Backend: clerk-backend-sdk for session verification
- Database: Users table with clerk_user_id

### Metrics
- Files modified: 8
- Tests added: 11 (8 unit, 3 integration)
- Time taken: ~6 hours
- Coverage: Backend 82%, Frontend 67%

### Version Impact
Story 1.3 complete → Epic 1 progress: 3/5 stories done (60%)
```

#### **5.4 Commit Your Work**

```bash
# Stage all changes
git add .

# Commit with detailed message
git commit -m "Story 1.3: Integrate Clerk authentication system

Implemented Clerk authentication with the following features:
- OAuth providers (Google, GitHub)
- Email/password authentication
- Magic link support
- User sync webhook for database
- Protected route middleware
- Sign in/out UI components

Technical details:
- Frontend: ClerkProvider + middleware.ts for route protection
- Backend: Session verification dependency + webhook handler
- Database: Users table stores clerk_user_id as primary identifier

Testing:
- ✅ All acceptance criteria verified
- ✅ 8 unit tests passing
- ✅ 3 integration tests passing
- ✅ Backend coverage: 82%
- ✅ Frontend coverage: 67%

Files changed:
- Created: middleware.ts, auth.py, clerk.py, sign-in page
- Modified: layout.tsx, main.py, env files

Closes Story 1.3
Refs Epic 1: User Onboarding & Foundation"

# Push to remote
git push origin story/1-3-clerk-auth
```

**Commit Message Best Practices:**

- ✅ Start with story ID: "Story X.Y: [Title]"
- ✅ First line: Short summary (< 72 chars)
- ✅ Blank line after summary
- ✅ Body: What, why, how
- ✅ Include test results
- ✅ List files changed
- ✅ Reference story/epic

**Exit Criteria:**
- ✅ All documentation updated
- ✅ Story summary created
- ✅ Change log updated
- ✅ Changes committed with detailed message

---

### **Stage 6: Completion & Merge**

#### **6.1 Final Verification**

```markdown
## Pre-Merge Checklist

### Code
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Linting clean
- [ ] No console errors

### Documentation
- [ ] Story summary created
- [ ] README updated (if needed)
- [ ] API docs updated (if needed)
- [ ] Change log updated

### Integration
- [ ] Merges cleanly with main
- [ ] No conflicts
- [ ] Works with latest main branch

### Sprint Tracking
- [ ] sprint-status.yaml updated to "done"
- [ ] Next story identified
```

#### **6.2 Mark Story as Done**

**Location:** `docs/sprint-status.yaml`

```yaml
# Update status
1-3-integrate-clerk-authentication-system: done

# Verify epic progress
# Epic 1 stories:
# 1-1: done
# 1-2: done
# 1-3: done  ← Just completed
# 1-4: deferred
# 1-5: backlog
```

#### **6.3 Merge to Main**

```bash
# If working solo (simple merge):
git checkout main
git pull origin main
git merge story/1-3-clerk-auth
git push origin main

# If on a team (create PR):
git push origin story/1-3-clerk-auth
# Then create PR on GitHub/GitLab
# Request review from team
# Merge after approval
```

**After Merge:**

```bash
# Clean up branch
git branch -d story/1-3-clerk-auth
git push origin --delete story/1-3-clerk-auth

# Return to main
git checkout main
git pull origin main
```

#### **6.4 Celebrate! 🎉**

Take a moment to:
- ✅ Acknowledge what you built
- ✅ Note what you learned
- ✅ Celebrate the win (even small ones matter!)

**Exit Criteria:**
- ✅ Story merged to main
- ✅ Branch cleaned up
- ✅ Ready for next story

---

## 🎮 **BMAD Workflow Integration**

### **Available BMAD Workflows for Developers**

#### **1. Story Context Workflow**

**When to use:** Before starting implementation

```
@bmad/bmm/workflows/story-context
```

**What it does:**
- Analyzes story requirements
- Identifies files to create/modify
- Creates implementation roadmap
- Documents technical decisions

**Output:** `docs/stories/story-[X.Y]-context.md`

#### **2. Developer Workflow**

**When to use:** During story development

```
@bmad/bmm/agents/dev
```

**What it does:**
- Guides through implementation
- Answers technical questions
- Reviews code quality
- Helps with debugging

**Menu options:**
- Check workflow status
- Create story context
- Mark story as done
- Get implementation help

#### **3. Code Review Workflow**

**When to use:** Before marking story as "done"

```
@bmad/bmm/workflows/code-review
```

**What it does:**
- Reviews code changes
- Checks best practices
- Identifies issues
- Generates review report

#### **4. Story Done Workflow**

**When to use:** After completing all testing

```
@bmad/bmm/workflows/story-done
```

**What it does:**
- Verifies all acceptance criteria met
- Confirms tests passing
- Updates story status
- Generates completion report

### **BMAD-Enhanced Development Flow**

```
1. SELECT STORY
   ↓
2. @bmad/bmm/workflows/story-context
   (Generate implementation plan)
   ↓
3. IMPLEMENT
   (Use @bmad/bmm/agents/dev for guidance)
   ↓
4. TEST
   (Manual + automated)
   ↓
5. @bmad/bmm/workflows/code-review
   (Get review feedback)
   ↓
6. @bmad/bmm/workflows/story-done
   (Mark complete)
   ↓
7. MERGE & CELEBRATE
```

---

## 📋 **Testing Guide**

### **Testing Pyramid in Practice**

```
     E2E Tests (Few)
     └─ Test: Complete user journeys
     └─ Tools: Playwright
     └─ When: Critical flows only
     
  Integration Tests (Some)
  └─ Test: Multiple components together
  └─ Tools: pytest, React Testing Library
  └─ When: API + DB + UI interactions
  
Unit Tests (Many)
└─ Test: Individual functions
└─ Tools: pytest, Jest
└─ When: Every module, function, component
```

### **What to Test**

#### **Always Test:**
- ✅ All acceptance criteria (manual minimum)
- ✅ Happy path (everything works)
- ✅ Error cases (what breaks)
- ✅ Edge cases (boundary conditions)

#### **Backend Tests:**
```python
# Unit: Individual functions
def test_hash_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)

# Integration: API endpoints
def test_create_user_endpoint():
    response = client.post("/api/v1/users", json={...})
    assert response.status_code == 201

# Integration: Database operations
def test_user_created_in_db():
    create_user("test@example.com")
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user is not None
```

#### **Frontend Tests:**
```typescript
// Unit: Component rendering
it('renders button with correct text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});

// Integration: User interaction
it('submits form on click', async () => {
  render(<SignUpForm />);
  await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
  await userEvent.click(screen.getByText('Submit'));
  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});

// E2E: Complete flow
it('completes signup flow', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### **Testing Commands Reference**

```bash
# Backend
cd packages/backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py

# Run specific test
poetry run pytest tests/test_auth.py::test_login

# Watch mode (rerun on change)
poetry run pytest-watch

# Frontend
cd packages/frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test auth.test.tsx

# Watch mode
npm test -- --watch

# E2E tests
npm run test:e2e

# E2E with UI
npx playwright test --ui
```

---

## ✅ **Code Quality Standards**

### **Backend (Python/FastAPI)**

#### **Style Guide: PEP 8**

```python
# Good ✅
def calculate_user_score(user_id: int, mission_count: int) -> float:
    """Calculate DCI score for a user.
    
    Args:
        user_id: The user's database ID
        mission_count: Number of completed missions
        
    Returns:
        Daily Consistency Index score (0-100)
    """
    base_score = mission_count * 10
    return min(base_score, 100.0)

# Bad ❌
def calcScore(uid, mc):  # No types, unclear names
    bs = mc * 10
    return bs if bs < 100 else 100  # No docstring
```

#### **Type Hints (Required)**

```python
from typing import Optional, List
from pydantic import BaseModel

# All function signatures must have types
async def get_user(user_id: int) -> Optional[User]:
    ...

# Use Pydantic for request/response models
class UserCreate(BaseModel):
    email: str
    timezone: str = "UTC"
```

#### **Error Handling**

```python
from fastapi import HTTPException

# Good ✅
async def get_mission(mission_id: int) -> Mission:
    mission = await db.query(Mission).filter_by(id=mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

# Bad ❌
async def get_mission(mission_id: int) -> Mission:
    return await db.query(Mission).filter_by(id=mission_id).first()  # Could return None!
```

### **Frontend (TypeScript/React)**

#### **Style Guide: ESLint + Airbnb**

```typescript
// Good ✅
interface MissionCardProps {
  mission: Mission;
  onComplete: (id: string) => void;
  isActive?: boolean;
}

export const MissionCard: React.FC<MissionCardProps> = ({ 
  mission, 
  onComplete,
  isActive = false 
}) => {
  const handleClick = useCallback(() => {
    onComplete(mission.id);
  }, [mission.id, onComplete]);
  
  return (
    <div className="mission-card">
      <h3>{mission.title}</h3>
      <button onClick={handleClick}>Complete</button>
    </div>
  );
};

// Bad ❌
export const MissionCard = (props: any) => {  // No interface, any type
  return <div onClick={() => props.onComplete(props.mission.id)}>  // Inline function
    <h3>{props.mission.title}</h3>
  </div>
}
```

#### **Hooks Best Practices**

```typescript
// Good ✅
const MissionList: React.FC = () => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    let cancelled = false;
    
    const fetchMissions = async () => {
      try {
        const data = await api.getMissions();
        if (!cancelled) {
          setMissions(data);
        }
      } catch (error) {
        console.error('Failed to fetch missions:', error);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    
    fetchMissions();
    
    return () => {
      cancelled = true;  // Cleanup
    };
  }, []);  // Dependencies listed
  
  // ... render
};

// Bad ❌
const MissionList = () => {
  const [missions, setMissions] = useState([]);  // No type
  
  useEffect(() => {
    api.getMissions().then(setMissions);  // No error handling, no cleanup
  });  // Missing dependencies array!
  
  // ... render
};
```

### **Code Quality Tools**

#### **Backend Tools**

```bash
# Formatter: Black
poetry add --dev black
poetry run black .

# Linter: Ruff (fast, modern)
poetry add --dev ruff
poetry run ruff check .

# Type checker: mypy
poetry add --dev mypy
poetry run mypy app

# Pre-commit hook
poetry add --dev pre-commit
# Create .pre-commit-config.yaml
```

#### **Frontend Tools**

```bash
# Linter: ESLint
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Formatter: Prettier
npm install --save-dev prettier eslint-config-prettier

# Type checker: tsc
npm run type-check  # Configured in package.json
```

---

## 📚 **Documentation Requirements**

### **What to Document**

#### **Code Documentation**

```python
# Backend: Docstrings for all public functions/classes
def calculate_dci(user_id: int, date: datetime) -> float:
    """Calculate Daily Consistency Index for a user on a specific date.
    
    The DCI is calculated based on:
    1. Missions completed (weighted by duration)
    2. Streak bonus (capped at 2.0x multiplier)
    3. Value category balance (bonus for well-rounded progress)
    
    Args:
        user_id: The user's database ID
        date: The date to calculate DCI for
        
    Returns:
        DCI score between 0 and 100
        
    Raises:
        ValueError: If date is in the future
        
    Example:
        >>> calculate_dci(user_id=123, date=datetime(2025, 11, 10))
        85.3
    """
    pass
```

```typescript
// Frontend: JSDoc for complex functions
/**
 * Fetches and caches mission data with exponential backoff retry.
 * 
 * @param userId - The user's unique identifier
 * @param options - Optional fetch configuration
 * @param options.useCache - Whether to use cached data (default: true)
 * @param options.maxRetries - Maximum retry attempts (default: 3)
 * @returns Promise resolving to mission array
 * @throws {ApiError} If all retries fail
 * 
 * @example
 * ```typescript
 * const missions = await fetchMissions('user_123', { useCache: false });
 * ```
 */
async function fetchMissions(
  userId: string,
  options?: FetchOptions
): Promise<Mission[]> {
  // ...
}
```

#### **Story Documentation**

Always create for completed stories:

**1. Story Summary** (`docs/stories/story-[X.Y]-summary.md`)
- What was built
- Files created/modified
- Testing results
- Technical decisions
- Lessons learned

**2. Testing Report** (`docs/stories/story-[X.Y]-testing.md`)
- Manual test results
- Automated test results
- Coverage metrics
- Known issues

#### **Project Documentation**

Update when relevant:

**1. README.md**
- New setup steps
- New dependencies
- New environment variables
- New commands

**2. API Documentation**
- New endpoints (method, path, params, response)
- Authentication requirements
- Example requests/responses

**3. Change Log** (`.cursor-changes`)
- High-level summary of changes
- Version impact
- Metrics (files, tests, time)

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue: Tests Failing After Merge**

```bash
# Solution 1: Update dependencies
cd packages/backend && poetry install
cd packages/frontend && npm install

# Solution 2: Reset database
docker-compose down -v
docker-compose up -d
poetry run alembic upgrade head

# Solution 3: Clear caches
rm -rf packages/frontend/.next
rm -rf packages/backend/__pycache__
```

#### **Issue: Git Conflicts**

```bash
# Solution: Rebase on latest main
git checkout main
git pull origin main
git checkout story/your-branch
git rebase main

# Resolve conflicts manually in editor
# Then:
git add .
git rebase --continue
```

#### **Issue: Dev Server Won't Start**

```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :8000
# Mac/Linux:
lsof -i :8000

# Kill the process or use different port
poetry run uvicorn app.main:app --reload --port 8001
```

#### **Issue: Can't Connect to Database**

```bash
# Check Docker containers
docker-compose ps

# View logs
docker-compose logs postgres

# Restart services
docker-compose restart postgres

# Check connection string in .env
echo $DATABASE_URL
```

---

## 📖 **Resources**

### **Project Documentation**
- Architecture: `docs/ARCHITECTURE.md`
- Epic Breakdown: `docs/epics.md`
- Sprint Status: `docs/sprint-status.yaml`
- Tech Specs: `docs/tech-spec-epic-[N].md`

### **BMAD Documentation**
- BMAD Index: `bmad/README.md`
- Developer Agent: `.cursor/rules/bmad/bmm/agents/dev.mdc`
- Workflows: `bmad/bmm/workflows/`

### **External Resources**
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs
- Clerk Docs: https://clerk.com/docs
- LangChain Docs: https://python.langchain.com
- Playwright Docs: https://playwright.dev

### **Testing Resources**
- pytest: https://docs.pytest.org
- Jest: https://jestjs.io/docs
- React Testing Library: https://testing-library.com/react
- Playwright: https://playwright.dev/docs/intro

---

## 🎓 **Developer Growth Path**

### **Level 1: Apprentice Developer**
- ✅ Follow workflow completely
- ✅ Write basic tests
- ✅ Complete stories with guidance
- ✅ Ask questions frequently

**Goal:** Build confidence, establish habits

### **Level 2: Competent Developer**
- ✅ Follow workflow independently
- ✅ Write comprehensive tests
- ✅ Complete stories without guidance
- ✅ Help others with questions

**Goal:** Consistency, quality, speed

### **Level 3: Proficient Developer**
- ✅ Adapt workflow to story needs
- ✅ Design test strategies
- ✅ Complete complex stories
- ✅ Review others' code

**Goal:** Judgment, leadership, mentorship

### **Level 4: Expert Developer**
- ✅ Improve workflow processes
- ✅ Set testing standards
- ✅ Architect features
- ✅ Teach and mentor

**Goal:** Innovation, excellence, impact

**Remember:** Everyone starts at Level 1. Growth comes from repetition, reflection, and pushing beyond comfort zones.

---

## ✨ **Final Words**

**This guide is your roadmap to becoming a better developer.**

The workflow is systematic because:
- ✅ **Systems beat willpower** - Habits compound over time
- ✅ **Quality beats speed** - Doing it right saves time later
- ✅ **Testing beats hope** - Confidence comes from verification
- ✅ **Documentation beats memory** - Your future self will thank you

**Follow the process. Trust the process. Improve the process.**

Every story you complete is a step forward. Every test you write is an investment. Every lesson you learn is progress.

**You've got this! 🚀**

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-10  
**Maintained By:** Delight Team  
**License:** Internal Use Only


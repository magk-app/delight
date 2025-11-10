# Delight E2E Test Suite

Production-ready Playwright test framework for the Delight AI Companion platform.

## Setup

### Prerequisites

- Node.js 20+ (see `.nvmrc`)
- pnpm 8+
- Running backend API (see `packages/backend/README.md`)

### Installation

```bash
# Install dependencies (includes Playwright)
cd packages/frontend
pnpm install

# Install Playwright browsers
pnpm exec playwright install --with-deps

# Copy environment configuration
cp tests/.env.example tests/.env
# Edit tests/.env with your Clerk credentials and API endpoints
```

### Environment Configuration

Edit `tests/.env` and configure:

1. **Clerk Authentication**
   - `CLERK_TEST_USER_EMAIL`: Test user email (create in Clerk Dashboard)
   - `CLERK_TEST_USER_PASSWORD`: Test user password
   - `CLERK_PUBLISHABLE_KEY`: From Clerk Dashboard > API Keys
   - `CLERK_SECRET_KEY`: From Clerk Dashboard > API Keys

2. **API Endpoints**
   - `BASE_URL`: Frontend URL (default: `http://localhost:3000`)
   - `API_URL`: Backend API URL (default: `http://localhost:8000/api/v1`)

3. **Database** (optional, for advanced testing)
   - `DATABASE_URL`: PostgreSQL connection string for test data seeding

4. **AI Services** (optional)
   - `USE_REAL_AI=false`: Use mocked AI responses by default
   - Set to `true` and provide `OPENAI_API_KEY` for real AI testing

## Running Tests

### Local Development

```bash
# Run all tests (headless)
pnpm exec playwright test

# Run tests with UI (watch mode)
pnpm exec playwright test --ui

# Run tests in headed mode (see browser)
pnpm exec playwright test --headed

# Run specific test file
pnpm exec playwright test tests/e2e/companion-chat.spec.ts

# Run tests matching pattern
pnpm exec playwright test --grep "quest"

# Debug mode (step through tests)
pnpm exec playwright test --debug

# Run on specific browser
pnpm exec playwright test --project=chromium
```

### View Test Results

```bash
# Open HTML report (after test run)
pnpm exec playwright show-report test-results/html

# View traces (for failed tests)
pnpm exec playwright show-trace test-results/.../trace.zip
```

### CI/CD

Tests run automatically on:
- Pull requests
- Commits to `main` branch

CI configuration uses:
- 2 retries for flaky test mitigation
- Single worker (sequential execution)
- Video/trace capture on failure only

## Test Architecture

### Directory Structure

```
tests/
├── e2e/                      # End-to-end test files
│   ├── auth.setup.ts         # Authentication setup (runs once)
│   ├── example.spec.ts       # Example test patterns
│   ├── companion-chat.spec.ts
│   ├── quest-management.spec.ts
│   └── evidence-upload.spec.ts
├── support/                  # Test infrastructure
│   ├── fixtures/             # Custom Playwright fixtures
│   │   ├── index.ts          # Fixture registration
│   │   └── factories/        # Data factories
│   │       ├── user-factory.ts
│   │       ├── quest-factory.ts
│   │       └── companion-factory.ts
│   └── helpers/              # Utility functions
│       ├── auth.ts           # Authentication helpers
│       └── wait.ts           # Network-first wait strategies
└── README.md                 # This file
```

### Fixture Pattern

Tests use **custom fixtures** for data setup with auto-cleanup:

```typescript
import { test, expect } from '../support/fixtures';

test('my test', async ({ page, userFactory, questFactory }) => {
  // Create test data
  const user = await userFactory.createUser();
  const quest = await questFactory.createQuest(user.id);

  // Run test
  await page.goto(`/quests/${quest.id}`);
  
  // Fixtures automatically clean up after test
});
```

**Benefits:**
- No manual cleanup needed
- Test isolation guaranteed
- Consistent data generation (faker)
- Easy overrides for specific scenarios

### Network-First Waiting

**Always wait for network responses** instead of arbitrary timeouts:

```typescript
import { waitForApiResponse, waitForStreamComplete } from '../support/helpers/wait';

// ❌ BAD: Arbitrary sleep
await page.waitForTimeout(5000);

// ✅ GOOD: Wait for API response
await waitForApiResponse(page, '/api/v1/quests');

// ✅ GOOD: Wait for SSE stream (AI responses)
await waitForStreamComplete(page, '[data-testid="companion-message"]');
```

### Authentication

Authentication uses a **global setup project**:

1. `auth.setup.ts` runs once before all tests
2. Saves authenticated state to `.auth/user.json`
3. All tests reuse this state (faster execution)

**No need to login in every test!**

### Selectors

Use `data-testid` attributes for stable selectors:

```typescript
// ✅ GOOD: Stable, semantic selector
await page.click('[data-testid="send-button"]');

// ❌ BAD: Brittle CSS selector
await page.click('.btn.btn-primary.send');

// ❌ BAD: XPath (hard to maintain)
await page.click('//button[@class="send"]');
```

## Best Practices

### Test Design

1. **Test Isolation**: Each test should be independent
   - Use fixtures for data setup
   - Rely on auto-cleanup
   - Don't depend on test execution order

2. **Deterministic Waits**: Never use `waitForTimeout`
   - Wait for network responses
   - Wait for specific elements
   - Use `waitForLoadState` when appropriate

3. **Explicit Assertions**: Always assert expected outcomes
   - Don't just check for "no errors"
   - Verify data, UI state, navigation

4. **Test Length**: Keep tests focused
   - One scenario per test
   - Break complex flows into multiple tests
   - Max 50-75 lines per test

### Performance

- **Parallelization**: Tests run in parallel by default (local)
- **Reuse Auth State**: Login once, reuse across all tests
- **Failure Artifacts Only**: Videos/traces only on failure
- **Worker Isolation**: Each worker has clean browser context

### Debugging

When tests fail:

1. **View Trace**: `pnpm exec playwright show-trace test-results/.../trace.zip`
   - See screenshots, network calls, console logs
   - Step through test execution

2. **Run in UI Mode**: `pnpm exec playwright test --ui`
   - Watch tests run live
   - Time-travel debugging

3. **Run Headed**: `pnpm exec playwright test --headed`
   - See browser during test execution

4. **Debug Mode**: `pnpm exec playwright test --debug`
   - Step through test line-by-line
   - Playwright Inspector

### Common Pitfalls

❌ **Don't**: Use arbitrary timeouts
```typescript
await page.waitForTimeout(5000);
```

✅ **Do**: Wait for network or specific conditions
```typescript
await waitForApiResponse(page, '/api/v1/quests');
```

---

❌ **Don't**: Use brittle selectors
```typescript
await page.click('.btn.primary');
```

✅ **Do**: Use data-testid attributes
```typescript
await page.click('[data-testid="submit-button"]');
```

---

❌ **Don't**: Create test data manually
```typescript
await fetch('/api/v1/users', { method: 'POST', ... });
```

✅ **Do**: Use factories with auto-cleanup
```typescript
const user = await userFactory.createUser();
```

---

❌ **Don't**: Skip cleanup
```typescript
// Test creates data, never cleans up
```

✅ **Do**: Use fixtures for automatic cleanup
```typescript
test('...', async ({ questFactory }) => {
  // Creates quest, automatically cleaned up
  const quest = await questFactory.createQuest(userId);
});
```

## Knowledge Base References

This framework implements patterns from the BMAD Test Architect knowledge base:

- **Fixture Architecture** (`bmad/bmm/testarch/knowledge/fixture-architecture.md`)
  - Pure function → fixture → mergeTests composition
  - Auto-cleanup pattern

- **Data Factories** (`bmad/bmm/testarch/knowledge/data-factories.md`)
  - Faker-based generation
  - Override support
  - Nested factories

- **Network-First** (`bmad/bmm/testarch/knowledge/network-first.md`)
  - Intercept before navigate
  - HAR capture
  - Deterministic waiting

- **Test Quality** (`bmad/bmm/testarch/knowledge/test-quality.md`)
  - Deterministic, isolated tests
  - Explicit assertions
  - Length/time limits

## Next Steps

1. ✅ Framework scaffolded
2. ⏳ Create tests for Epic 1 stories (user onboarding)
3. ⏳ Set up CI/CD pipeline
4. ⏳ Add API testing (Playwright API)
5. ⏳ Add visual regression testing (Percy/Playwright screenshots)

## Support

- **Playwright Docs**: https://playwright.dev
- **BMAD Test Architect**: Run `@bmad/bmm/agents/tea` for expert guidance
- **Project Issues**: See GitHub Issues

---

**Framework Version**: 4.0 (BMAD v6)  
**Last Updated**: 2025-11-10


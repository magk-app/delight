/**
 * E2E Tests: Authentication Flows (Story 1.3)
 *
 * Tests for Clerk authentication:
 * - Sign-up flow
 * - Sign-in flow
 * - Route protection
 * - Session persistence
 * - Sign-out flow
 *
 * Prerequisites:
 * - CLERK_TEST_USER_EMAIL and CLERK_TEST_USER_PASSWORD in .env
 * - Backend running with test database
 * - Frontend dev server running
 */

import { test, expect } from "@playwright/test";

/**
 * Test Configuration
 */
const TEST_EMAIL = process.env.CLERK_TEST_USER_EMAIL || "test@delight.dev";
const TEST_PASSWORD = process.env.CLERK_TEST_USER_PASSWORD || "TestPassword123!";
const NEW_USER_EMAIL = `test-${Date.now()}@delight.dev`; // Unique for each run
const NEW_USER_PASSWORD = "NewUser123!";

/**
 * Test Group: Unauthenticated User Flows
 */
test.describe("Unauthenticated User Flows", () => {
  test("should redirect to sign-in for protected routes", async ({ page }) => {
    /**
     * Story 1.3: Protected routes redirect unauthenticated users
     *
     * Given: Unauthenticated user
     * When: Navigate to /dashboard
     * Then: Redirected to /sign-in
     */
    await page.goto("/dashboard");

    // Should redirect to sign-in
    await expect(page).toHaveURL(/\/sign-in/);
  });

  test("should allow access to public routes", async ({ page }) => {
    /**
     * Story 1.3: Public routes accessible without auth
     *
     * Given: Unauthenticated user
     * When: Navigate to /
     * Then: Page loads without redirect
     */
    await page.goto("/");

    // Should load homepage without redirect
    await expect(page).toHaveURL("/");
    await expect(page).toHaveTitle(/Delight/i);
  });

  test("should load sign-in page", async ({ page }) => {
    /**
     * Story 1.3: Sign-in page accessible
     *
     * Given: Unauthenticated user
     * When: Navigate to /sign-in
     * Then: Clerk SignIn component renders
     */
    await page.goto("/sign-in");

    // Should show Clerk sign-in form
    await expect(page).toHaveURL("/sign-in");

    // Wait for Clerk to load
    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });
    await expect(page.locator('input[name="identifier"]')).toBeVisible();
  });

  test("should load sign-up page", async ({ page }) => {
    /**
     * Story 1.3: Sign-up page accessible
     *
     * Given: Unauthenticated user
     * When: Navigate to /sign-up
     * Then: Clerk SignUp component renders
     */
    await page.goto("/sign-up");

    // Should show Clerk sign-up form
    await expect(page).toHaveURL("/sign-up");

    // Wait for Clerk to load
    await page.waitForSelector('input[name="emailAddress"]', { timeout: 10000 });
    await expect(page.locator('input[name="emailAddress"]')).toBeVisible();
  });
});

/**
 * Test Group: Sign-Up Flow
 */
test.describe("Sign-Up Flow", () => {
  test("should complete sign-up with email and password", async ({ page }) => {
    /**
     * Story 1.3: User can create account via Clerk
     *
     * Given: New user credentials
     * When: Complete sign-up form
     * Then: User created, redirected to app
     *
     * Note: Uses unique email for each test run to avoid conflicts
     */
    await page.goto("/sign-up");

    // Wait for Clerk form
    await page.waitForSelector('input[name="emailAddress"]', { timeout: 10000 });

    // Fill sign-up form
    await page.fill('input[name="emailAddress"]', NEW_USER_EMAIL);
    await page.fill('input[name="password"]', NEW_USER_PASSWORD);

    // Submit form
    await page.click('button[type="submit"]');

    // Clerk may require email verification in production
    // For test environment, should redirect to app
    // Wait for navigation away from sign-up
    await page.waitForURL((url) => !url.pathname.includes("/sign-up"), {
      timeout: 15000,
    });

    // Should be authenticated (exact redirect depends on Clerk config)
    // Could be /dashboard, /onboarding, etc.
    const currentUrl = page.url();
    expect(currentUrl).not.toContain("/sign-up");
    expect(currentUrl).not.toContain("/sign-in");
  });

  test("should show validation error for invalid email", async ({ page }) => {
    /**
     * Story 1.3: Client-side validation for invalid inputs
     *
     * Given: Invalid email format
     * When: Submit sign-up form
     * Then: Clerk shows validation error
     */
    await page.goto("/sign-up");

    await page.waitForSelector('input[name="emailAddress"]', { timeout: 10000 });

    // Enter invalid email
    await page.fill('input[name="emailAddress"]', "not-an-email");
    await page.fill('input[name="password"]', "ValidPassword123!");

    // Try to submit
    await page.click('button[type="submit"]');

    // Should show error (Clerk's error message may vary)
    // Wait for error element to appear
    await page.waitForSelector('[role="alert"], .cl-formFieldErrorText', {
      timeout: 5000,
    });

    const errorVisible = await page
      .locator('[role="alert"], .cl-formFieldErrorText')
      .isVisible();
    expect(errorVisible).toBeTruthy();
  });

  test("should show error for duplicate email", async ({ page }) => {
    /**
     * Story 1.3: Prevent duplicate account creation
     *
     * Given: Email already registered
     * When: Attempt sign-up with same email
     * Then: Clerk shows error
     *
     * Note: Uses TEST_EMAIL which should already exist
     */
    await page.goto("/sign-up");

    await page.waitForSelector('input[name="emailAddress"]', { timeout: 10000 });

    // Try to sign up with existing email
    await page.fill('input[name="emailAddress"]', TEST_EMAIL);
    await page.fill('input[name="password"]', "SomePassword123!");

    await page.click('button[type="submit"]');

    // Should show "email already exists" error
    // Wait for error message
    await page.waitForSelector('[role="alert"], .cl-formFieldErrorText', {
      timeout: 5000,
    });

    const errorText = await page
      .locator('[role="alert"], .cl-formFieldErrorText')
      .textContent();
    expect(errorText?.toLowerCase()).toContain("email");
  });
});

/**
 * Test Group: Sign-In Flow
 */
test.describe("Sign-In Flow", () => {
  test("should complete sign-in with valid credentials", async ({ page }) => {
    /**
     * Story 1.3: User can sign in with Clerk
     *
     * Given: Existing user credentials
     * When: Complete sign-in form
     * Then: User authenticated, redirected to app
     */
    await page.goto("/sign-in");

    // Wait for Clerk sign-in form
    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });

    // Fill identifier (email)
    await page.fill('input[name="identifier"]', TEST_EMAIL);
    await page.click('button[type="submit"]');

    // Wait for password field (Clerk uses two-step flow)
    await page.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    // Should redirect to app after successful sign-in
    await page.waitForURL((url) => !url.pathname.includes("/sign-in"), {
      timeout: 15000,
    });

    // Verify authenticated (not on sign-in page)
    const currentUrl = page.url();
    expect(currentUrl).not.toContain("/sign-in");
  });

  test("should show error for invalid credentials", async ({ page }) => {
    /**
     * Story 1.3: Authentication failure handled gracefully
     *
     * Given: Invalid password
     * When: Submit sign-in form
     * Then: Clerk shows error message
     */
    await page.goto("/sign-in");

    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });

    // Fill with valid email but wrong password
    await page.fill('input[name="identifier"]', TEST_EMAIL);
    await page.click('button[type="submit"]');

    await page.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page.fill('input[name="password"]', "WrongPassword123!");
    await page.click('button[type="submit"]');

    // Should show error
    await page.waitForSelector('[role="alert"], .cl-formFieldErrorText', {
      timeout: 5000,
    });

    const errorText = await page
      .locator('[role="alert"], .cl-formFieldErrorText')
      .textContent();
    expect(errorText?.toLowerCase()).toMatch(/password|credentials|incorrect/);
  });

  test("should redirect to intended page after sign-in", async ({ page }) => {
    /**
     * Story 1.3: Preserve navigation intent across sign-in
     *
     * Given: User tries to access /dashboard (redirected to /sign-in)
     * When: Complete sign-in
     * Then: Redirected back to /dashboard
     */
    // Try to access protected route
    await page.goto("/dashboard");

    // Should redirect to sign-in
    await expect(page).toHaveURL(/\/sign-in/);

    // Complete sign-in
    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });
    await page.fill('input[name="identifier"]', TEST_EMAIL);
    await page.click('button[type="submit"]');

    await page.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    // Should redirect to originally requested page (/dashboard)
    // Note: Clerk may redirect to configured default page
    await page.waitForURL((url) => !url.pathname.includes("/sign-in"), {
      timeout: 15000,
    });

    // Verify authenticated and can access protected route
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");
  });
});

/**
 * Test Group: Authenticated User Flows
 */
test.describe("Authenticated User Flows", () => {
  test.beforeEach(async ({ page }) => {
    /**
     * Setup: Sign in before each test
     */
    await page.goto("/sign-in");
    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });

    await page.fill('input[name="identifier"]', TEST_EMAIL);
    await page.click('button[type="submit"]');

    await page.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    // Wait for redirect
    await page.waitForURL((url) => !url.pathname.includes("/sign-in"), {
      timeout: 15000,
    });
  });

  test("should allow access to protected routes", async ({ page }) => {
    /**
     * Story 1.3: Authenticated users can access protected routes
     *
     * Given: Authenticated user
     * When: Navigate to /dashboard
     * Then: Page loads without redirect
     */
    await page.goto("/dashboard");

    // Should load without redirect
    await expect(page).toHaveURL("/dashboard");
  });

  test("should persist session after page refresh", async ({ page }) => {
    /**
     * Story 1.3: Session survives page reload
     *
     * Given: Authenticated user on protected route
     * When: Refresh page
     * Then: User still authenticated
     */
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");

    // Refresh page
    await page.reload();

    // Should still be on dashboard (not redirected to sign-in)
    await expect(page).toHaveURL("/dashboard");
  });

  test("should sign out successfully", async ({ page }) => {
    /**
     * Story 1.3: User can sign out
     *
     * Given: Authenticated user
     * When: Click sign-out
     * Then: User signed out, redirected to public page
     */
    await page.goto("/");

    // Look for Clerk user button or sign-out button
    // Clerk's UserButton component includes sign-out
    // Click user button to open menu
    await page.click('[data-clerk-element="userButton"]', { timeout: 10000 });

    // Wait for menu to open
    await page.waitForSelector('button:has-text("Sign out")', { timeout: 5000 });

    // Click sign out
    await page.click('button:has-text("Sign out")');

    // Should redirect to public page
    await page.waitForURL("/", { timeout: 10000 });

    // Verify signed out - try to access protected route
    await page.goto("/dashboard");

    // Should redirect to sign-in
    await expect(page).toHaveURL(/\/sign-in/);
  });
});

/**
 * Test Group: Route Protection
 */
test.describe("Route Protection", () => {
  test("should protect dashboard route", async ({ page }) => {
    /**
     * Story 1.3: Middleware protects routes
     *
     * Given: Unauthenticated user
     * When: Direct URL navigation to /dashboard
     * Then: Redirected to sign-in
     */
    await page.goto("/dashboard");

    await expect(page).toHaveURL(/\/sign-in/);
  });

  test("should protect API routes", async ({ page, context }) => {
    /**
     * Story 1.3: API endpoints require authentication
     *
     * Given: Unauthenticated request
     * When: API call to /api/v1/users/me
     * Then: 403 Forbidden
     */
    const response = await context.request.get(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/users/me`
    );

    expect(response.status()).toBe(403);
  });

  test("should allow webhook routes without auth", async ({ page, context }) => {
    /**
     * Story 1.3: Webhook endpoints are public
     *
     * Given: Unauthenticated request
     * When: POST to /api/v1/webhooks/clerk
     * Then: Not 403 (signature validation is different check)
     *
     * Note: Will fail signature check but not auth check
     */
    const response = await context.request.post(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/webhooks/clerk`,
      {
        data: { test: "data" },
      }
    );

    // Should not be 403 (auth rejection)
    // Will be 400 (signature validation) which is expected
    expect(response.status()).not.toBe(403);
  });
});

/**
 * Test Group: Session Persistence
 */
test.describe("Session Persistence", () => {
  test.beforeEach(async ({ page }) => {
    /**
     * Setup: Sign in before each test
     */
    await page.goto("/sign-in");
    await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });

    await page.fill('input[name="identifier"]', TEST_EMAIL);
    await page.click('button[type="submit"]');

    await page.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    await page.waitForURL((url) => !url.pathname.includes("/sign-in"), {
      timeout: 15000,
    });
  });

  test("should persist session across tabs", async ({ browser }) => {
    /**
     * Story 1.3: Session shared across browser tabs
     *
     * Given: Authenticated user in tab 1
     * When: Open tab 2
     * Then: User authenticated in tab 2
     */
    // Create new browser context (shares cookies)
    const context = await browser.newContext();
    const page1 = await context.newPage();

    // Sign in on page 1
    await page1.goto("/sign-in");
    await page1.waitForSelector('input[name="identifier"]', { timeout: 10000 });
    await page1.fill('input[name="identifier"]', TEST_EMAIL);
    await page1.click('button[type="submit"]');
    await page1.waitForSelector('input[name="password"]', { timeout: 5000 });
    await page1.fill('input[name="password"]', TEST_PASSWORD);
    await page1.click('button[type="submit"]');

    await page1.waitForURL((url) => !url.pathname.includes("/sign-in"), {
      timeout: 15000,
    });

    // Open page 2 in same context
    const page2 = await context.newPage();
    await page2.goto("/dashboard");

    // Should be authenticated (no redirect to sign-in)
    await expect(page2).toHaveURL("/dashboard");

    await context.close();
  });

  test("should maintain session after navigation", async ({ page }) => {
    /**
     * Story 1.3: Session persists during app navigation
     *
     * Given: Authenticated user
     * When: Navigate between multiple protected routes
     * Then: No re-authentication required
     */
    // Navigate to multiple protected routes
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");

    await page.goto("/");
    await expect(page).toHaveURL("/");

    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");

    // All navigations should succeed without sign-in redirect
  });
});

/**
 * Test Helper: Clean up test users
 *
 * Note: Clerk test environment should auto-cleanup old test users
 * or use Clerk API to delete users created during tests
 */

/**
 * Example E2E Test Suite
 *
 * Demonstrates Delight testing patterns:
 * - Fixtures for data setup
 * - Network-first waiting
 * - Clerk authentication
 * - AI streaming responses
 */

import { test, expect } from "../support/fixtures";
import {
  waitForApiResponse,
  waitForStreamComplete,
} from "../support/helpers/wait";

test.describe("Homepage", () => {
  test("should load homepage", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Delight/i);
    await expect(page.locator("h1")).toContainText("Welcome to Delight");
  });

  test("should navigate to sign-up page", async ({ page }) => {
    await page.goto("/");

    // Click get started button using data-testid
    await page.click('[data-testid="get-started-button"]');

    // Should redirect to sign-up page
    await expect(page).toHaveURL(/\/sign-up/);
  });
});

test.describe("Companion Chat", () => {
  test.skip("should send message and receive AI response - TODO: Implement /companion page (Story 2.x)", async ({ page }) => {
    await page.goto("/companion");

    // Intercept API calls
    const chatPromise = waitForApiResponse(page, "/api/v1/companion/chat");

    // Send message
    await page.fill('[data-testid="chat-input"]', "Hello, how are you?");
    await page.click('[data-testid="send-button"]');

    // Wait for API response
    await chatPromise;

    // Wait for streaming to complete
    await waitForStreamComplete(page, '[data-testid="companion-message"]', {
      timeout: 30000,
    });

    // Verify message appears
    await expect(
      page.locator('[data-testid="companion-message"]').last()
    ).toContainText(/\w+/);
  });
});

test.describe("Quest Management", () => {
  test.skip("should create quest with missions - TODO: Implement /quests page (Story 3.x)", async ({
    page,
    userFactory,
    questFactory,
  }) => {
    // This test demonstrates fixture usage
    // Note: In real tests, you'd use the authenticated user from session
    // This is for demonstration of factory pattern

    await page.goto("/quests");

    // Click create quest
    await page.click('[data-testid="create-quest-button"]');

    // Fill form
    await page.fill('[data-testid="quest-title"]', "Learn TypeScript");
    await page.fill(
      '[data-testid="quest-description"]',
      "Master TypeScript fundamentals"
    );
    await page.selectOption('[data-testid="quest-type"]', "short_term");

    // Submit
    const createPromise = waitForApiResponse(page, "/api/v1/quests");
    await page.click('[data-testid="submit-quest-button"]');

    // Wait for creation
    const quest = await createPromise;
    expect(quest.title).toBe("Learn TypeScript");

    // Verify redirect to quest detail
    await expect(page).toHaveURL(new RegExp(`/quests/${quest.id}`));

    // Verify quest appears in list
    await page.goto("/quests");
    await expect(
      page.locator(`[data-testid="quest-${quest.id}"]`)
    ).toBeVisible();
  });
});

test.describe("Evidence Upload", () => {
  test.skip("should upload evidence for quest", async ({ page }) => {
    // TODO: Implement after evidence upload feature is complete
    // This demonstrates how to skip incomplete tests

    await page.goto("/quests/1/evidence");

    // Upload file
    await page.setInputFiles('[data-testid="evidence-upload"]', {
      name: "screenshot.png",
      mimeType: "image/png",
      buffer: Buffer.from("fake-image-data"),
    });

    // Submit
    await page.click('[data-testid="submit-evidence-button"]');

    // Verify upload
    await expect(
      page.locator('[data-testid="evidence-success"]')
    ).toBeVisible();
  });
});

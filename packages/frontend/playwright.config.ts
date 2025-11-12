import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E Testing Configuration
 *
 * Configured for Delight AI Companion platform:
 * - Real-time AI streaming (SSE)
 * - Clerk authentication
 * - Complex user flows (quests, missions, evidence)
 *
 * See: tests/README.md for setup and usage
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // Timeouts
  timeout: 60 * 1000, // Test timeout: 60s (allows for AI response times)
  expect: {
    timeout: 15 * 1000, // Assertion timeout: 15s
  },

  use: {
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 15 * 1000, // Action timeout: 15s
    navigationTimeout: 30 * 1000, // Navigation timeout: 30s
  },

  // Test results
  outputDir: "test-results",
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["junit", { outputFile: "test-results/junit.xml" }],
    ["list"],
  ],

  // Multi-browser testing
  projects: [
    // Setup project for authentication (optional)
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
    },

    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // Use auth state if available, otherwise run unauthenticated
        ...(process.env.CLERK_TEST_USER_PASSWORD && {
          storageState: "tests/support/.auth/user.json",
        }),
      },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      use: {
        ...devices["Desktop Firefox"],
        ...(process.env.CLERK_TEST_USER_PASSWORD && {
          storageState: "tests/support/.auth/user.json",
        }),
      },
      dependencies: ["setup"],
    },
    {
      name: "webkit",
      use: {
        ...devices["Desktop Safari"],
        ...(process.env.CLERK_TEST_USER_PASSWORD && {
          storageState: "tests/support/.auth/user.json",
        }),
      },
      dependencies: ["setup"],
    },
  ],

  // Local dev server
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes for backend + frontend startup
    // Suppress Next.js 15 async headers warnings from Clerk (Clerk v5.7.5 + Next.js 15 known issue)
    // These are warnings only, not errors - tests will still run correctly
    stderr: "pipe", // Changed from default to reduce noise
  },
});

/**
 * Authentication Helpers
 *
 * Handles Clerk authentication for E2E tests.
 * Stores auth state for reuse across tests.
 */

import { Page } from "@playwright/test";

/**
 * Login with Clerk credentials
 * Stores auth state in .auth/user.json for reuse
 */
export async function login(
  page: Page,
  email: string,
  password: string
): Promise<void> {
  await page.goto("/sign-in");

  // Wait for Clerk sign-in form
  await page.waitForSelector('input[name="identifier"]', { timeout: 10000 });

  // Fill in credentials
  await page.fill('input[name="identifier"]', email);
  await page.click('button[type="submit"]');

  // Wait for password field
  await page.waitForSelector('input[name="password"]', { timeout: 5000 });
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for redirect to app (indicates successful login)
  await page.waitForURL("**/dashboard", { timeout: 10000 });
}

/**
 * Logout
 */
export async function logout(page: Page): Promise<void> {
  await page.goto("/");

  // Click user menu
  await page.click('[data-testid="user-menu"]');

  // Click sign out
  await page.click('[data-testid="sign-out-button"]');

  // Wait for redirect to home
  await page.waitForURL("/", { timeout: 5000 });
}

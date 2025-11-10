/**
 * Authentication Setup
 * 
 * Runs before all tests to authenticate once and save state.
 * Other tests reuse this auth state for faster execution.
 * 
 * Setup project dependency in playwright.config.ts
 */

import { test as setup, expect } from '@playwright/test';
import { login } from '../support/helpers/auth';
import path from 'path';
import fs from 'fs';

const authFile = 'tests/support/.auth/user.json';

setup('authenticate', async ({ page }) => {
  const email = process.env.CLERK_TEST_USER_EMAIL || 'test@example.com';
  const password = process.env.CLERK_TEST_USER_PASSWORD;

  if (!password) {
    console.warn('⚠️  CLERK_TEST_USER_PASSWORD not set - skipping auth setup');
    return;
  }

  // Ensure .auth directory exists
  const authDir = path.dirname(authFile);
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  // Login
  await login(page, email, password);

  // Verify we're authenticated
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();

  // Save authenticated state
  await page.context().storageState({ path: authFile });

  console.log('✅ Authentication setup complete');
});


/**
 * Wait Helpers
 * 
 * Network-first waiting strategies for deterministic tests.
 * 
 * Knowledge Base: bmad/bmm/testarch/knowledge/network-first.md
 */

import { Page } from '@playwright/test';

/**
 * Wait for API response
 * Use this instead of arbitrary sleeps
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  options: { timeout?: number } = {}
): Promise<any> {
  const response = await page.waitForResponse(
    (resp) => {
      const url = resp.url();
      return typeof urlPattern === 'string' 
        ? url.includes(urlPattern)
        : urlPattern.test(url);
    },
    { timeout: options.timeout || 15000 }
  );

  return await response.json();
}

/**
 * Wait for SSE stream to complete
 * For AI companion responses
 */
export async function waitForStreamComplete(
  page: Page,
  selector: string,
  options: { timeout?: number } = {}
): Promise<void> {
  // Wait for loading indicator to appear
  await page.waitForSelector(`${selector} [data-testid="loading"]`, {
    state: 'visible',
    timeout: 2000,
  }).catch(() => {
    // Loading might be too fast, ignore
  });

  // Wait for loading indicator to disappear
  await page.waitForSelector(`${selector} [data-testid="loading"]`, {
    state: 'hidden',
    timeout: options.timeout || 30000,
  });
}

/**
 * Wait for network idle
 * Use sparingly - prefer explicit network waits
 */
export async function waitForNetworkIdle(
  page: Page,
  options: { timeout?: number; idleTime?: number } = {}
): Promise<void> {
  await page.waitForLoadState('networkidle', {
    timeout: options.timeout || 30000,
  });

  // Additional idle time to ensure stability
  if (options.idleTime) {
    await page.waitForTimeout(options.idleTime);
  }
}


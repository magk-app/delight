/**
 * UUID Generation Utility
 *
 * Browser-compatible UUID generation with fallback for environments
 * where crypto.randomUUID() is not available.
 */

/**
 * Generates a UUID v4 using crypto.randomUUID() if available,
 * otherwise falls back to a manual implementation.
 */
export function generateUUID(): string {
  // Check if crypto.randomUUID is available (modern browsers, Node 16+)
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    try {
      return crypto.randomUUID();
    } catch (error) {
      // Fall through to manual implementation if randomUUID fails
      console.warn("crypto.randomUUID() failed, using fallback:", error);
    }
  }

  // Fallback: Manual UUID v4 implementation
  // Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

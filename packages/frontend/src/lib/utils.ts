import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes
 * Combines clsx for conditional classes and tailwind-merge for Tailwind class conflicts
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format duration in minutes to a human-readable string
 * @param minutes - Duration in minutes
 * @returns Formatted duration string (e.g., "15 min", "1h 30m", "2h")
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Get Tailwind color class based on DCI (Daily Consistency Index) score
 * Uses DCI_THRESHOLDS constants: EXCELLENT (0.9), STRONG (0.8), STEADY (0.6), FRAGILE (0.3)
 * @param score - DCI score between 0 and 1
 * @returns Tailwind text color class
 */
export function getDCIStatusColor(score: number): string {
  if (score >= 0.9) {
    return "text-green-600"; // Excellent (>= 0.9)
  } else if (score >= 0.8) {
    return "text-blue-600"; // Strong (>= 0.8)
  } else if (score >= 0.6) {
    return "text-yellow-600"; // Steady (>= 0.6)
  } else {
    return "text-red-600"; // Fragile (< 0.6)
  }
}

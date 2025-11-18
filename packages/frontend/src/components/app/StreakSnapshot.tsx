/**
 * StreakSnapshot - Shows current streak information
 */

'use client';

import { mockStreakSummary } from '@/lib/mock/data';
import { VALUE_CATEGORY_INFO } from '@/lib/constants';

export function StreakSnapshot() {
  const streak = mockStreakSummary;

  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">Streak Status</h3>

      {/* Overall Streak */}
      <div className="mb-6 text-center">
        <div className="mb-2 text-5xl font-bold text-primary">{streak.overallStreak}</div>
        <div className="text-sm text-gray-600">Day Streak</div>
        <div className="mt-1 text-xs text-gray-500">
          Longest: {streak.longestStreak} days
        </div>
      </div>

      {/* Category Streaks */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700">By Category</h4>
        {Object.entries(streak.categoryStreaks).map(([category, days]) => {
          const info = VALUE_CATEGORY_INFO[category as keyof typeof VALUE_CATEGORY_INFO];
          return (
            <div key={category} className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span>{info.icon}</span>
                <span className="text-sm text-gray-700">{info.label}</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">
                {days > 0 ? `${days} days` : '-'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

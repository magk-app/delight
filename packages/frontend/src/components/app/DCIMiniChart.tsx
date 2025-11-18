/**
 * DCIMiniChart - Mini visualization of DCI over the last 7 days
 */

'use client';

import Link from 'next/link';
import { mockDCISnapshot, mockDCIHistory } from '@/lib/mock/data';
import { getDCIStatusColor } from '@/lib/utils';

export function DCIMiniChart() {
  const dci = mockDCISnapshot;
  const history = mockDCIHistory;

  // Simple sparkline visualization
  const maxScore = Math.max(...history.map((h) => h.score));
  const minScore = Math.min(...history.map((h) => h.score));
  const range = maxScore - minScore || 1;

  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">Daily Consistency Index</h3>

      {/* Current DCI Score */}
      <div className="mb-4 text-center">
        <div className={`mb-1 text-4xl font-bold ${getDCIStatusColor(dci.score)}`}>
          {Math.round(dci.score * 100)}%
        </div>
        <div className="text-sm font-medium text-gray-600">{dci.status}</div>
      </div>

      {/* 7-Day Sparkline */}
      <div className="mb-4">
        <div className="flex h-16 items-end justify-between space-x-1">
          {history.map((point, i) => {
            const height = ((point.score - minScore) / range) * 100;
            const isToday = i === history.length - 1;

            return (
              <div
                key={point.date}
                className="flex-1 relative group"
                style={{ height: '100%' }}
              >
                <div
                  className={`absolute bottom-0 w-full rounded-t transition-all ${
                    isToday ? 'bg-primary' : 'bg-primary/40'
                  } hover:bg-primary`}
                  style={{ height: `${Math.max(height, 10)}%` }}
                >
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block">
                    <div className="rounded bg-gray-900 px-2 py-1 text-xs text-white whitespace-nowrap">
                      {point.date.substring(5)}: {Math.round(point.score * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* View Details Link */}
      <Link
        href="/progress"
        className="block text-center text-sm font-medium text-primary hover:text-primary/80"
      >
        View detailed analytics →
      </Link>
    </div>
  );
}

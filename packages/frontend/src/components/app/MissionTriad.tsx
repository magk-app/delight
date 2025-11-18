/**
 * MissionTriad - Today's three prioritized missions
 * Shows high, medium, and low priority missions in a triad layout
 */

'use client';

import Link from 'next/link';
import { mockMissionTriad } from '@/lib/mock/data';
import { VALUE_CATEGORY_INFO } from '@/lib/constants';
import { formatDuration } from '@/lib/utils';
import type { Mission } from '@/lib/types';

function MissionCard({ mission, priority }: { mission: Mission; priority: string }) {
  const categoryInfo = VALUE_CATEGORY_INFO[mission.valueCategory];

  const priorityColors = {
    high: 'border-red-200 bg-red-50',
    medium: 'border-yellow-200 bg-yellow-50',
    low: 'border-green-200 bg-green-50',
  };

  const priorityLabels = {
    high: 'High Priority',
    medium: 'Medium Priority',
    low: 'Easy Win',
  };

  return (
    <div
      className={`rounded-lg border-2 p-6 transition-all hover:shadow-md ${priorityColors[priority as keyof typeof priorityColors]}`}
    >
      {/* Priority Label */}
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-600">
          {priorityLabels[priority as keyof typeof priorityLabels]}
        </span>
        <span className="text-2xl" title={categoryInfo.label}>
          {categoryInfo.icon}
        </span>
      </div>

      {/* Mission Title */}
      <h3 className="mb-2 text-lg font-semibold text-gray-900">{mission.title}</h3>

      {/* Mission Description */}
      <p className="mb-4 text-sm text-gray-600 line-clamp-2">{mission.description}</p>

      {/* Mission Meta */}
      <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-gray-700">
        <div className="flex items-center space-x-1">
          <span>⏱️</span>
          <span>{formatDuration(mission.estimatedMinutes)}</span>
        </div>
        <div className="flex items-center space-x-1">
          <span>⚡</span>
          <span className="capitalize">{mission.energyLevel}</span>
        </div>
        {mission.goal && (
          <div className="flex items-center space-x-1">
            <span>🎯</span>
            <span className="truncate">{mission.goal.title}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button className="flex-1 rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 transition-colors">
          Start Mission
        </button>
        <button className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          Defer
        </button>
      </div>
    </div>
  );
}

export function MissionTriad() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Today's Mission Triad</h2>
        <Link
          href="/missions"
          className="text-sm font-medium text-primary hover:text-primary/80"
        >
          View all missions →
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <MissionCard mission={mockMissionTriad.high} priority="high" />
        <MissionCard mission={mockMissionTriad.medium} priority="medium" />
        <MissionCard mission={mockMissionTriad.low} priority="low" />
      </div>
    </div>
  );
}

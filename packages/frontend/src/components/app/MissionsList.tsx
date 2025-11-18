/**
 * MissionsList - Table/grid view of all missions with filtering
 */

'use client';

import { mockMissions } from '@/lib/mock/data';
import { VALUE_CATEGORY_INFO, MISSION_STATUS } from '@/lib/constants';
import { formatDuration } from '@/lib/utils';

export function MissionsList() {
  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      {/* Table Header */}
      <div className="grid grid-cols-6 gap-4 p-4 bg-gray-50 border-b text-sm font-medium text-gray-700">
        <div className="col-span-2">Mission</div>
        <div>Goal</div>
        <div>Category</div>
        <div>Time</div>
        <div>Status</div>
      </div>

      {/* Missions */}
      <div className="divide-y">
        {mockMissions.map((mission) => {
          const categoryInfo = VALUE_CATEGORY_INFO[mission.valueCategory];

          return (
            <div
              key={mission.id}
              className="grid grid-cols-6 gap-4 p-4 hover:bg-gray-50 transition-colors cursor-pointer"
            >
              {/* Mission Title & Description */}
              <div className="col-span-2">
                <h4 className="font-medium text-gray-900 mb-1">{mission.title}</h4>
                <p className="text-sm text-gray-600 line-clamp-1">{mission.description}</p>
              </div>

              {/* Goal */}
              <div className="flex items-center text-sm text-gray-700">
                {mission.goal?.title || '-'}
              </div>

              {/* Category */}
              <div className="flex items-center space-x-1.5">
                <span className="text-lg">{categoryInfo.icon}</span>
                <span className="text-sm text-gray-700">{categoryInfo.label}</span>
              </div>

              {/* Time */}
              <div className="flex items-center text-sm text-gray-700">
                {formatDuration(mission.estimatedMinutes)}
              </div>

              {/* Status */}
              <div className="flex items-center">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    mission.status === MISSION_STATUS.COMPLETED
                      ? 'bg-green-100 text-green-700'
                      : mission.status === MISSION_STATUS.IN_PROGRESS
                      ? 'bg-blue-100 text-blue-700'
                      : mission.status === MISSION_STATUS.DEFERRED
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {mission.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

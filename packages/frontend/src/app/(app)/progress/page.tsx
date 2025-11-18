/**
 * Progress & DCI Dashboard - Visualize consistency and analytics
 * Shows: DCI score, streak details, mission distribution, highlight reels
 */

'use client';

import {
  mockDCISnapshot,
  mockDCIHistory,
  mockStreakSummary,
  mockHighlightReels,
  mockMissions,
} from '@/lib/mock/data';
import { getDCIStatusColor } from '@/lib/utils';
import { VALUE_CATEGORY_INFO } from '@/lib/constants';
import { useState } from 'react';

export default function ProgressPage() {
  const dci = mockDCISnapshot;
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');

  // Calculate mission distribution by value category
  const categoryDistribution = mockMissions.reduce(
    (acc, mission) => {
      if (mission.status === 'completed') {
        acc[mission.valueCategory] = (acc[mission.valueCategory] || 0) + 1;
      }
      return acc;
    },
    {} as Record<string, number>
  );

  const totalCompleted = Object.values(categoryDistribution).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Progress Analytics</h1>
        <p className="mt-1 text-sm text-gray-600">
          Track your consistency and growth over time
        </p>
      </div>

      {/* DCI Card - Large */}
      <div className="rounded-lg border bg-white p-8 shadow-sm">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Daily Consistency Index
          </h2>
          <div className={`text-7xl font-bold mb-2 ${getDCIStatusColor(dci.score)}`}>
            {Math.round(dci.score * 100)}%
          </div>
          <div className="text-xl font-medium text-gray-600 mb-6">{dci.status}</div>

          {/* Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
            <div>
              <div className="text-sm text-gray-600 mb-1">Streak Factor</div>
              <div className="text-2xl font-semibold text-gray-900">
                {Math.round(dci.breakdown.streakFactor * 100)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Completion Rate</div>
              <div className="text-2xl font-semibold text-gray-900">
                {Math.round(dci.breakdown.completionRate * 100)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Engagement</div>
              <div className="text-2xl font-semibold text-gray-900">
                {Math.round(dci.breakdown.engagementDepth * 100)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Response Rate</div>
              <div className="text-2xl font-semibold text-gray-900">
                {Math.round(dci.breakdown.responseRate * 100)}%
              </div>
            </div>
          </div>
        </div>

        {/* DCI Chart */}
        <div className="mt-8 pt-6 border-t">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">Trend</h3>
            <div className="flex gap-2">
              {(['7d', '30d', '90d'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                    timeRange === range
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>

          {/* Line Chart */}
          <div className="h-48 flex items-end justify-between space-x-1">
            {mockDCIHistory.map((point, i) => {
              const maxScore = 1.0;
              const minScore = 0;
              const height = ((point.score - minScore) / (maxScore - minScore)) * 100;

              return (
                <div key={point.date} className="flex-1 relative group">
                  <div className="absolute bottom-0 w-full flex flex-col items-center">
                    <div
                      className="w-full bg-primary/60 rounded-t transition-all hover:bg-primary"
                      style={{ height: `${Math.max(height * 1.5, 10)}px` }}
                    />
                    <div className="mt-2 text-xs text-gray-600 rotate-45 origin-left whitespace-nowrap">
                      {point.date.substring(5)}
                    </div>

                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 hidden group-hover:block">
                      <div className="bg-gray-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap">
                        {point.date}: {Math.round(point.score * 100)}%
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Streak Panel */}
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Streak Status</h3>

          <div className="text-center mb-6">
            <div className="text-5xl font-bold text-primary mb-2">
              {mockStreakSummary.overallStreak}
            </div>
            <div className="text-sm text-gray-600">Current Streak</div>
            <div className="text-xs text-gray-500 mt-1">
              Longest: {mockStreakSummary.longestStreak} days
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">By Category</h4>
            {Object.entries(mockStreakSummary.categoryStreaks).map(([category, days]) => {
              const info = VALUE_CATEGORY_INFO[category as keyof typeof VALUE_CATEGORY_INFO];
              return (
                <div key={category}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-2">
                      <span>{info.icon}</span>
                      <span className="text-sm text-gray-700">{info.label}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">
                      {days > 0 ? `${days} days` : '-'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: 14 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-2 w-full rounded-full ${
                          i < days ? 'bg-primary' : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mission Distribution */}
        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Missions by Value Category
          </h3>

          <div className="space-y-4">
            {Object.entries(categoryDistribution).map(([category, count]) => {
              const info = VALUE_CATEGORY_INFO[category as keyof typeof VALUE_CATEGORY_INFO];
              const percentage = (count / totalCompleted) * 100;

              return (
                <div key={category}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span>{info.icon}</span>
                      <span className="text-sm font-medium text-gray-700">{info.label}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">
                      {count} ({Math.round(percentage)}%)
                    </span>
                  </div>
                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: info.color,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 pt-4 border-t text-center">
            <div className="text-2xl font-bold text-gray-900">{totalCompleted}</div>
            <div className="text-sm text-gray-600">Total Missions Completed</div>
          </div>
        </div>
      </div>

      {/* Highlight Reels */}
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Highlight Reels</h3>

        <div className="space-y-4">
          {mockHighlightReels.map((reel) => (
            <div key={reel.id} className="p-4 rounded-lg border border-primary/20 bg-primary/5">
              <h4 className="font-semibold text-gray-900 mb-3">{reel.title}</h4>

              <ul className="space-y-1 mb-4">
                {reel.content.accomplishments.map((item, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    {item}
                  </li>
                ))}
              </ul>

              <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                {Object.entries(reel.content.stats).map(([key, value]) => (
                  <div key={key}>
                    <span className="font-medium">{value}</span> {key.replace(/([A-Z])/g, ' $1')}
                  </div>
                ))}
              </div>

              {reel.content.quote && (
                <p className="text-sm italic text-gray-700 border-l-4 border-primary pl-3">
                  "{reel.content.quote}"
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* TODO Comment */}
      <div className="text-xs text-gray-500 italic">
        // TODO: Wire to /api/v1/progress/* for real analytics calculations
      </div>
    </div>
  );
}

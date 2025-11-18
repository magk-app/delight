/**
 * GoalsList - List of user's goals with filtering and detail view
 */

'use client';

import { useState } from 'react';
import { mockGoals, mockMissions } from '@/lib/mock/data';
import { VALUE_CATEGORY_INFO, GOAL_STATUS } from '@/lib/constants';
import type { Goal } from '@/lib/types';

export function GoalsList() {
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(mockGoals[0]);
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredGoals =
    statusFilter === 'all'
      ? mockGoals
      : mockGoals.filter((g) => g.status === statusFilter);

  const relatedMissions = selectedGoal
    ? mockMissions.filter((m) => m.goalId === selectedGoal.id)
    : [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left: Goals List */}
      <div className="space-y-4">
        {/* Filters */}
        <div className="flex gap-2">
          <button
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              statusFilter === 'all'
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setStatusFilter(GOAL_STATUS.ACTIVE)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              statusFilter === GOAL_STATUS.ACTIVE
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setStatusFilter(GOAL_STATUS.COMPLETED)}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              statusFilter === GOAL_STATUS.COMPLETED
                ? 'bg-primary text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed
          </button>
        </div>

        {/* Goals */}
        <div className="space-y-2">
          {filteredGoals.map((goal) => {
            const categoryInfo = VALUE_CATEGORY_INFO[goal.valueCategory];
            const isSelected = selectedGoal?.id === goal.id;

            return (
              <button
                key={goal.id}
                onClick={() => setSelectedGoal(goal)}
                className={`w-full text-left p-4 rounded-lg border transition-all ${
                  isSelected
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{goal.title}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <span>{categoryInfo.icon}</span>
                      <span>{categoryInfo.label}</span>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 capitalize">
                    {goal.status}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: Goal Detail */}
      {selectedGoal && (
        <div className="lg:col-span-2 space-y-6">
          {/* Goal Header */}
          <div className="rounded-lg border bg-white p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {selectedGoal.title}
                </h2>
                <p className="text-gray-600">{selectedGoal.description}</p>
              </div>
              <button className="text-sm font-medium text-primary hover:text-primary/80">
                Edit Goal
              </button>
            </div>

            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">Category:</span>
                <span className="font-medium">
                  {VALUE_CATEGORY_INFO[selectedGoal.valueCategory].label}
                </span>
              </div>
              {selectedGoal.targetDate && (
                <div className="flex items-center space-x-2">
                  <span className="text-gray-600">Target:</span>
                  <span className="font-medium">
                    {new Date(selectedGoal.targetDate).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Missions for this Goal */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Missions ({relatedMissions.length})
            </h3>
            <div className="space-y-2">
              {relatedMissions.length === 0 ? (
                <p className="text-sm text-gray-600 text-center py-8">
                  No missions yet. Start by breaking down your goal with Eliza.
                </p>
              ) : (
                relatedMissions.map((mission) => (
                  <div
                    key={mission.id}
                    className="p-4 rounded-lg border bg-white hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">{mission.title}</h4>
                        <div className="flex items-center space-x-3 text-sm text-gray-600">
                          <span>⏱️ {mission.estimatedMinutes}min</span>
                          <span>⚡ {mission.energyLevel}</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            mission.status === 'completed'
                              ? 'bg-green-100 text-green-700'
                              : mission.status === 'in_progress'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {mission.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

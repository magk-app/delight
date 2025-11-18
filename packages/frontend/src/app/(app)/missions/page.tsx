/**
 * Missions Page - Goals and mission management interface
 * Features: Goals tab, Missions tab, Priority triad, Mission execution drawer
 */

'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GoalsList } from '@/components/app/GoalsList';
import { MissionsList } from '@/components/app/MissionsList';
import { MissionTriad } from '@/components/app/MissionTriad';

export default function MissionsPage() {
  const [activeTab, setActiveTab] = useState('missions');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Goals & Missions</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your goals and daily missions
          </p>
        </div>
        <button className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 transition-colors">
          + New Goal
        </button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="missions">Missions</TabsTrigger>
          <TabsTrigger value="goals">Goals</TabsTrigger>
        </TabsList>

        {/* Missions Tab */}
        <TabsContent value="missions" className="space-y-6 mt-6">
          {/* Priority Triad */}
          <div>
            <h2 className="mb-4 text-xl font-semibold text-gray-900">Priority Triad</h2>
            <MissionTriad />
          </div>

          {/* All Missions */}
          <div>
            <h2 className="mb-4 text-xl font-semibold text-gray-900">All Missions</h2>
            <MissionsList />
          </div>
        </TabsContent>

        {/* Goals Tab */}
        <TabsContent value="goals" className="space-y-6 mt-6">
          <GoalsList />
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * Dashboard Hub - Main landing page for authenticated users
 * Shows: Greeting, Mission Triad, Streak snapshot, DCI mini chart, Quick jump tiles
 */

import { GreetingCard } from '@/components/app/GreetingCard';
import { MissionTriad } from '@/components/app/MissionTriad';
import { StreakSnapshot } from '@/components/app/StreakSnapshot';
import { DCIMiniChart } from '@/components/app/DCIMiniChart';
import { QuickJumpTiles } from '@/components/app/QuickJumpTiles';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Greeting Card */}
      <GreetingCard />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Mission Triad */}
        <div className="lg:col-span-2">
          <MissionTriad />
        </div>

        {/* Right Column - Stats */}
        <div className="space-y-6">
          <StreakSnapshot />
          <DCIMiniChart />
        </div>
      </div>

      {/* Quick Jump Tiles */}
      <QuickJumpTiles />
    </div>
  );
}

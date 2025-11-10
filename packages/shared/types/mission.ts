/**
 * Mission and Goal-related TypeScript types
 */

export type MissionStatus = "pending" | "active" | "completed" | "abandoned";
export type GoalDimension = "growth" | "health" | "craft" | "connection";

export interface Mission {
  id: string;
  user_id: string;
  goal_id: string;
  title: string;
  description: string;
  dimension: GoalDimension;
  duration_minutes: number;
  status: MissionStatus;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  dimension: GoalDimension;
  status: "active" | "paused" | "completed" | "abandoned";
  priority: number;
  created_at: string;
  updated_at: string;
}

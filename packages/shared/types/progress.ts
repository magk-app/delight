/**
 * Progress and Analytics-related TypeScript types
 */

export interface ProgressStreak {
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string;
  updated_at: string;
}

export interface DailyConsistencyIndex {
  user_id: string;
  date: string;
  dci_score: number;
  missions_completed: number;
  dimensions_touched: number;
  total_minutes: number;
}

export interface HighlightReel {
  id: string;
  user_id: string;
  date_range_start: string;
  date_range_end: string;
  title: string;
  achievements: Array<{
    mission_id: string;
    title: string;
    evidence_url: string | null;
  }>;
  created_at: string;
}

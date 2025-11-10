/**
 * Narrative and World-related TypeScript types
 */

export type NarrativeScenario =
  | "modern"
  | "fantasy"
  | "scifi"
  | "cyberpunk"
  | "zombie";
export type ZoneType =
  | "arena"
  | "observatory"
  | "commons"
  | "workshop"
  | "sanctuary";

export interface NarrativeState {
  id: string;
  user_id: string;
  scenario: NarrativeScenario;
  current_chapter: number;
  essence_balance: number;
  unlocked_zones: ZoneType[];
  created_at: string;
  updated_at: string;
}

export interface StoryEvent {
  id: string;
  user_id: string;
  event_type:
    | "quest_completion"
    | "character_interaction"
    | "zone_unlock"
    | "milestone";
  title: string;
  description: string;
  essence_earned: number;
  created_at: string;
}

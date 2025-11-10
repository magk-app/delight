/**
 * Character and Companion-related TypeScript types
 */

export type CharacterRole =
  | "companion"
  | "craft_mentor"
  | "health_guide"
  | "wisdom_keeper";

export interface Character {
  id: string;
  name: string;
  role: CharacterRole;
  description: string;
  personality_traits: string[];
  avatar_url: string | null;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  character_id: string;
  role: "user" | "assistant";
  content: string;
  emotional_context: string | null;
  created_at: string;
}

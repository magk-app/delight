/**
 * User-related TypeScript types
 */

export interface User {
  id: string;
  clerk_user_id: string;
  email: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  user_id: string;
  theme: "light" | "dark" | "system";
  narrative_scenario: "modern" | "fantasy" | "scifi" | "cyberpunk" | "zombie";
  notification_enabled: boolean;
  notification_channels: {
    email: boolean;
    sms: boolean;
    push: boolean;
  };
  created_at: string;
  updated_at: string;
}

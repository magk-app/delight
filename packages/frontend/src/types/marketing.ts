export interface Character {
  id: string;
  name: string;
  role: string;
  description: string;
  domain: 'growth' | 'health' | 'craft' | 'connection';
  sampleQuote: string;
  avatarColor: string;
}

export interface NarrativeResponse {
  title: string;
  content: string;
  tags: string[];
}

export enum WorldType {
  MODERN = 'Modern Metropolis',
  CYBER = 'Cyberpunk Megacity',
  FANTASY = 'Ancient Guild',
  SCI_FI = 'Orbital Station'
}

export interface Mission {
  title: string;
  type: 'focus' | 'quick' | 'deep';
  duration: string;
  energyLevel: number;
}

import { WorldType, NarrativeResponse } from '@/types/marketing';

// Mock narrative generation for demo purposes
// In production, this would call the backend API with OpenAI integration
export const generateNarrative = async (
  goal: string,
  world: WorldType
): Promise<NarrativeResponse> => {
  // Simulate API delay for realistic feel
  await new Promise(resolve => setTimeout(resolve, 800));

  // Generate contextual narrative based on world type
  const narratives: Record<WorldType, (goal: string) => NarrativeResponse> = {
    [WorldType.CYBER]: (g) => ({
      title: 'The Neon Protocol',
      content: `The neural interface flickers as you upload your objective: "${g}". In the sprawling megacity, every goal becomes a data packet to decrypt. Your handler assigns you a covert op—break this mission into executable subroutines. The Corporation watches, but you move in the shadows.`,
      tags: ['Stealth', 'Execution', 'Tech'],
    }),
    [WorldType.MODERN]: (g) => ({
      title: 'The Urban Quest',
      content: `You stand at the crossroads of a bustling metropolis with one clear intention: "${g}". The city rewards those who take deliberate steps. Your companion maps out the first move—a focused mission to turn this ambition into tangible progress. The streets are yours to navigate.`,
      tags: ['Focus', 'Momentum', 'Action'],
    }),
    [WorldType.FANTASY]: (g) => ({
      title: 'The Guild Chronicle',
      content: `The ancient scroll unfurls before you, revealing your quest: "${g}". The Guild Masters have convened. This undertaking requires more than mere intention—it demands strategy, resilience, and small victories. Your first trial begins at dawn.`,
      tags: ['Honor', 'Strategy', 'Growth'],
    }),
    [WorldType.SCI_FI]: (g) => ({
      title: 'Transmission Received',
      content: `Mission parameters uploaded: "${g}". Station Command acknowledges. In the void of space, ambitions become orbital mechanics—each micro-burn propels you closer to your destination. Your AI co-pilot calculates the optimal trajectory. First maneuver: engage thrusters.`,
      tags: ['Precision', 'Systems', 'Progress'],
    }),
  };

  return narratives[world](goal);
};

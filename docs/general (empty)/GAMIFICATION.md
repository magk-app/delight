# Gamification System Design

## Overview

Delight transforms productivity into an engaging RPG experience. Every task becomes a quest, completion earns XP, and users progress through an ever-expanding game world. This document outlines the complete gamification system architecture.

## Core RPG Elements

### 1. Character System

#### Character Data Model

```typescript
interface Character {
  userId: string;
  name: string;
  level: number;
  currentXP: number;
  totalXP: number;

  // Stats (influenced by task completion patterns)
  stats: {
    strength: number; // Physical/manual tasks
    intelligence: number; // Mental/creative tasks
    focus: number; // Concentration tasks
    charisma: number; // Communication/social tasks
    endurance: number; // Long-term project completion
  };

  // Visual customization
  avatar: {
    type: "warrior" | "mage" | "rogue" | "cleric" | "custom";
    skinTone: string;
    hairStyle: string;
    hairColor: string;
    outfit: string;
    accessories: string[];
  };

  // Equipped items
  equipment: {
    weapon?: EquipmentItem;
    armor?: EquipmentItem;
    accessory?: EquipmentItem;
  };

  // Inventory
  inventory: InventoryItem[];

  // Progression
  title: string; // "Novice Adventurer", "Task Master", "Legend"
  achievements: Achievement[];
  streakDays: number;
  lastActiveDate: Date;
}
```

#### Leveling System

```typescript
function calculateXPForLevel(level: number): number {
  // Exponential progression: Level 2 = 100 XP, Level 3 = 250 XP, etc.
  return Math.floor(100 * Math.pow(1.5, level - 1));
}

function calculateLevel(totalXP: number): number {
  let level = 1;
  let xpNeeded = 0;

  while (xpNeeded <= totalXP) {
    level++;
    xpNeeded += calculateXPForLevel(level);
  }

  return level - 1;
}

async function awardXP(
  userId: string,
  xpAmount: number,
  reason: string
): Promise<{ newLevel: boolean; level: number }> {
  const character = await db.select().from("characters").where({ userId });

  const oldLevel = character.level;
  const newTotalXP = character.totalXP + xpAmount;
  const newLevel = calculateLevel(newTotalXP);

  await db
    .update("characters")
    .set({
      currentXP: character.currentXP + xpAmount,
      totalXP: newTotalXP,
      level: newLevel,
    })
    .where({ userId });

  // Log XP gain
  await db.insert("xp_log", {
    user_id: userId,
    amount: xpAmount,
    reason,
    timestamp: new Date(),
  });

  // Check for level up
  if (newLevel > oldLevel) {
    await handleLevelUp(userId, newLevel);
    return { newLevel: true, level: newLevel };
  }

  return { newLevel: false, level: newLevel };
}
```

### 2. Quest System

#### Quest Data Model

```typescript
interface Quest {
  questId: string;
  userId: string;

  // Quest metadata
  title: string;
  description: string;
  narrative: string; // AI-generated story

  // Quest type
  type: "daily" | "weekly" | "milestone" | "epic" | "side";
  difficulty: "easy" | "medium" | "hard" | "legendary";

  // Associated tasks
  taskIds: string[]; // Can be single or multi-task quest

  // Rewards
  rewards: {
    xp: number;
    items?: InventoryItem[];
    title?: string;
  };

  // Progress tracking
  status: "available" | "in_progress" | "completed" | "failed" | "expired";
  progress: number; // 0-100
  startedAt?: Date;
  completedAt?: Date;
  expiresAt?: Date;

  // Quest chain
  partOfChain?: string; // Quest chain ID
  nextQuest?: string; // Next quest in chain
}
```

#### Quest Generation

```typescript
async function generateQuestNarrative(
  task: Task,
  userPreferences: UserPreferences
): Promise<string> {
  const theme = userPreferences.gameTheme || "fantasy-rpg";

  const prompt = `
Generate an engaging quest narrative for this productivity task.

Theme: ${theme}
Task: ${task.title}
Description: ${task.description || "No additional details"}
Difficulty: ${task.difficulty}
Deadline: ${task.dueDate}

Create a short (2-3 sentences) quest description that:
1. Transforms the task into an adventure
2. Uses theme-appropriate language
3. Makes it sound exciting and achievable

Quest narrative:
`;

  const narrative = await llm.complete(prompt, {
    temperature: 0.9, // Higher creativity
    maxTokens: 150,
  });

  return narrative.trim();
}

// Example output:
// Task: "Finish budget report"
// Narrative: "The kingdom's treasury lies in disarray! Ancient scrolls of
// expenditure must be deciphered and organized before the Council of Elders
// convenes at week's end. Only a skilled accountant-adventurer can restore
// order to the realm's finances!"
```

#### Daily Quests

```typescript
async function generateDailyQuests(userId: string): Promise<Quest[]> {
  const userTasks = await db
    .select()
    .from("tasks")
    .where({ user_id: userId, status: "todo" })
    .limit(5);

  const dailyQuests: Quest[] = [];

  // Generate 3 daily quests
  for (let i = 0; i < 3 && i < userTasks.length; i++) {
    const task = userTasks[i];
    const narrative = await generateQuestNarrative(
      task,
      await getUserPreferences(userId)
    );

    dailyQuests.push({
      questId: `daily_${Date.now()}_${i}`,
      userId,
      title: task.title,
      description: task.description || "",
      narrative,
      type: "daily",
      difficulty: task.difficulty || "medium",
      taskIds: [task.id],
      rewards: {
        xp: calculateQuestXP(task.difficulty || "medium"),
        items: maybeGrantItem(0.3), // 30% chance of item drop
      },
      status: "available",
      progress: 0,
      expiresAt: endOfDay(new Date()),
    });
  }

  return dailyQuests;
}

function calculateQuestXP(difficulty: string): number {
  const baseXP = {
    easy: 25,
    medium: 50,
    hard: 100,
    legendary: 250,
  };

  return baseXP[difficulty] || 50;
}
```

### 3. World Building

#### World Map Structure

```typescript
interface WorldRegion {
  regionId: string;
  name: string;
  description: string;
  theme: "forest" | "mountain" | "desert" | "ocean" | "city" | "dungeon";

  // Unlock requirements
  unlockRequirements: {
    minLevel: number;
    requiredQuests?: string[];
    requiredAchievements?: string[];
  };

  // Content
  availableQuests: string[];
  bosses: Boss[];

  // Visual data
  mapPosition: { x: number; y: number };
  connections: string[]; // Connected region IDs
  isUnlocked: boolean;
}

interface Boss {
  bossId: string;
  name: string;
  description: string;
  level: number;

  // Boss is defeated by completing a major milestone
  linkedMilestone: string; // Project ID or epic quest ID

  // Rewards
  rewards: {
    xp: number;
    items: InventoryItem[];
    unlockRegions?: string[];
  };

  status: "locked" | "available" | "defeated";
}
```

#### Procedural World Generation

```typescript
async function generateNewRegion(
  userId: string,
  unlockTrigger: string
): Promise<WorldRegion> {
  const userLevel = await getUserLevel(userId);
  const unlockedRegionsCount = await getUnlockedRegionsCount(userId);

  const prompt = `
Generate a new world region for a productivity RPG game.

User level: ${userLevel}
Regions already unlocked: ${unlockedRegionsCount}
Theme: Fantasy RPG

Create a region with:
1. A unique name
2. A brief description (2-3 sentences)
3. A theme (forest, mountain, desert, ocean, city, dungeon)
4. 3-5 quest ideas appropriate for the level

Respond in JSON format.
`;

  const generated = await llm.complete(prompt);
  const regionData = JSON.parse(generated);

  const newRegion: WorldRegion = {
    regionId: `region_${unlockedRegionsCount + 1}`,
    name: regionData.name,
    description: regionData.description,
    theme: regionData.theme,
    unlockRequirements: {
      minLevel: userLevel,
      requiredQuests: [unlockTrigger],
    },
    availableQuests: [],
    bosses: [],
    mapPosition: calculateMapPosition(unlockedRegionsCount),
    connections: findConnectedRegions(unlockedRegionsCount),
    isUnlocked: true,
  };

  await db.insert("world_regions", newRegion);

  // Notify user
  await notifyUser(userId, {
    type: "region_unlocked",
    region: newRegion,
  });

  return newRegion;
}
```

### 4. Social Features

#### Friend System

```typescript
interface Friendship {
  userId1: string;
  userId2: string;
  status: "pending" | "accepted" | "blocked";
  createdAt: Date;

  // Shared stats
  sharedQuests: number;
  mutualEncouragement: number;
}

interface Team {
  teamId: string;
  name: string;
  description: string;
  members: TeamMember[];
  createdAt: Date;

  // Team stats
  totalXP: number;
  level: number;
  completedTeamQuests: number;
}

interface TeamMember {
  userId: string;
  role: "leader" | "member";
  joinedAt: Date;
  contributionXP: number;
}
```

#### Leaderboards

```typescript
interface Leaderboard {
  type: "global" | "friends" | "team";
  timeframe: "daily" | "weekly" | "monthly" | "all_time";
  entries: LeaderboardEntry[];
}

interface LeaderboardEntry {
  rank: number;
  userId: string;
  username: string;
  avatar: string;
  score: number; // XP or tasks completed
  level: number;
  change: number; // +/- since last update
}

async function getLeaderboard(
  type: "global" | "friends" | "team",
  timeframe: "daily" | "weekly" | "monthly" | "all_time",
  userId?: string
): Promise<Leaderboard> {
  let query = db.select().from("characters");

  // Filter by timeframe
  if (timeframe !== "all_time") {
    const since = getTimeframeCutoff(timeframe);
    query = query.where("last_xp_gain", ">=", since);
  }

  // Filter by relationship
  if (type === "friends" && userId) {
    const friendIds = await getFriendIds(userId);
    query = query.whereIn("user_id", friendIds);
  }

  // Get top 100
  const results = await query.orderBy("total_xp", "desc").limit(100);

  return {
    type,
    timeframe,
    entries: results.map((r, index) => ({
      rank: index + 1,
      userId: r.user_id,
      username: r.username,
      avatar: r.avatar,
      score: r.total_xp,
      level: r.level,
      change: 0, // Calculate from previous snapshot
    })),
  };
}
```

#### Accountability Partners

```typescript
interface AccountabilityPartnership {
  partnershipId: string;
  user1Id: string;
  user2Id: string;

  // Settings
  dailyCheckIn: boolean;
  shareProgress: boolean;
  mutualGoals: string[];

  // Stats
  encouragementsSent: number;
  sharedStreakDays: number;

  createdAt: Date;
}

async function sendEncouragement(
  fromUserId: string,
  toUserId: string,
  message: string
): Promise<void> {
  // Check if they're partners
  const partnership = await db
    .select()
    .from("accountability_partnerships")
    .where((builder) =>
      builder
        .where({ user1_id: fromUserId, user2_id: toUserId })
        .orWhere({ user1_id: toUserId, user2_id: fromUserId })
    )
    .first();

  if (!partnership) {
    throw new Error("Not accountability partners");
  }

  // Send notification
  await notifyUser(toUserId, {
    type: "encouragement",
    from: fromUserId,
    message,
  });

  // Increment counter
  await db
    .update("accountability_partnerships")
    .increment("encouragements_sent", 1)
    .where({ partnership_id: partnership.partnershipId });
}
```

### 5. Rewards & Economy

#### Item System

```typescript
interface InventoryItem {
  itemId: string;
  name: string;
  description: string;
  type: "weapon" | "armor" | "accessory" | "consumable" | "cosmetic";
  rarity: "common" | "uncommon" | "rare" | "epic" | "legendary";

  // Effects (if equipment)
  effects?: {
    statBonus?: Partial<Character["stats"]>;
    xpMultiplier?: number; // e.g., 1.1 for 10% bonus
  };

  // Visual
  icon: string;

  // Acquisition
  acquiredAt: Date;
  acquiredFrom: string; // Quest ID or boss ID
}

const ITEM_DROP_RATES = {
  common: 0.5, // 50% chance
  uncommon: 0.3, // 30% chance
  rare: 0.15, // 15% chance
  epic: 0.04, // 4% chance
  legendary: 0.01, // 1% chance
};

function rollItemDrop(baseChance: number = 0.3): InventoryItem | null {
  if (Math.random() > baseChance) {
    return null; // No drop
  }

  // Determine rarity
  const roll = Math.random();
  let rarity: InventoryItem["rarity"] = "common";

  if (roll <= ITEM_DROP_RATES.legendary) {
    rarity = "legendary";
  } else if (roll <= ITEM_DROP_RATES.legendary + ITEM_DROP_RATES.epic) {
    rarity = "epic";
  } else if (
    roll <=
    ITEM_DROP_RATES.legendary + ITEM_DROP_RATES.epic + ITEM_DROP_RATES.rare
  ) {
    rarity = "rare";
  } else if (roll <= 0.5) {
    rarity = "uncommon";
  }

  // Generate item based on rarity
  return generateRandomItem(rarity);
}
```

#### Achievements

```typescript
interface Achievement {
  achievementId: string;
  name: string;
  description: string;
  icon: string;

  // Unlock criteria
  criteria: {
    type: "tasks_completed" | "streak" | "level" | "xp" | "quests" | "social";
    threshold: number;
  };

  // Rewards
  rewards: {
    xp: number;
    title?: string;
    items?: InventoryItem[];
  };

  // Rarity
  rarity: "common" | "rare" | "epic" | "legendary";

  // Tracking
  unlockedBy: string[]; // User IDs
  percentageUnlocked: number;
}

const ACHIEVEMENTS: Achievement[] = [
  {
    achievementId: "first_steps",
    name: "First Steps",
    description: "Complete your first task",
    icon: "🎯",
    criteria: { type: "tasks_completed", threshold: 1 },
    rewards: { xp: 10 },
    rarity: "common",
    unlockedBy: [],
    percentageUnlocked: 0,
  },
  {
    achievementId: "centurion",
    name: "Centurion",
    description: "Complete 100 tasks",
    icon: "💯",
    criteria: { type: "tasks_completed", threshold: 100 },
    rewards: { xp: 500, title: "The Centurion" },
    rarity: "rare",
    unlockedBy: [],
    percentageUnlocked: 0,
  },
  {
    achievementId: "legendary_streak",
    name: "Legendary Dedication",
    description: "Maintain a 100-day streak",
    icon: "🔥",
    criteria: { type: "streak", threshold: 100 },
    rewards: { xp: 1000, title: "The Unstoppable" },
    rarity: "legendary",
    unlockedBy: [],
    percentageUnlocked: 0,
  },
];

async function checkAchievements(userId: string): Promise<Achievement[]> {
  const user = await getUser(userId);
  const newAchievements: Achievement[] = [];

  for (const achievement of ACHIEVEMENTS) {
    // Skip if already unlocked
    if (achievement.unlockedBy.includes(userId)) {
      continue;
    }

    // Check criteria
    let unlocked = false;

    switch (achievement.criteria.type) {
      case "tasks_completed":
        unlocked = user.tasksCompleted >= achievement.criteria.threshold;
        break;
      case "streak":
        unlocked = user.streakDays >= achievement.criteria.threshold;
        break;
      case "level":
        unlocked = user.level >= achievement.criteria.threshold;
        break;
      case "xp":
        unlocked = user.totalXP >= achievement.criteria.threshold;
        break;
    }

    if (unlocked) {
      // Award achievement
      await awardAchievement(userId, achievement);
      newAchievements.push(achievement);
    }
  }

  return newAchievements;
}
```

---

## AI-Enhanced Gamification

### Dynamic Narrative Generation

```typescript
async function generateDynamicStory(
  userId: string,
  recentActivity: Activity[]
): Promise<string> {
  const character = await getCharacter(userId);
  const worldState = await getWorldState(userId);

  const prompt = `
You are a narrative AI for a productivity RPG game. Generate a short story update 
based on the user's recent activity.

Character: ${character.name}, Level ${character.level} ${character.title}
Recent achievements: ${recentActivity.map((a) => a.description).join(", ")}
Current world state: ${worldState.currentRegion}

Write a 3-4 sentence narrative that:
1. Acknowledges their recent accomplishments
2. Hints at future challenges
3. Maintains the ${character.avatar.type} character theme
4. Keeps them motivated

Story update:
`;

  return await llm.complete(prompt, { temperature: 0.8 });
}

// Example output:
// "As you vanquish the dreaded Budget Dragon, the realm trembles with your
// victory! Word of your fiscal prowess spreads through the kingdom, and the
// Merchant Guild now seeks your counsel. But beware, adventurer—rumors speak
// of an even greater challenge: the Quarterly Report Hydra rises in the east..."
```

### Adaptive Difficulty

```typescript
async function adjustGameDifficulty(userId: string): Promise<void> {
  const stats = await getRecentPerformanceStats(userId);

  // If user completing tasks too easily, increase challenge
  if (
    stats.completionRate > 0.9 &&
    stats.averageTime < stats.estimatedTime * 0.7
  ) {
    await suggestHarderTasks(userId);
    await increaseQuestDifficulty(userId);
  }

  // If user struggling, provide assistance
  if (stats.completionRate < 0.5) {
    await offerPowerUps(userId); // Focus boost, time extension, etc.
    await simplifyQuestRequirements(userId);
  }
}

async function suggestHarderTasks(userId: string): Promise<void> {
  const prompt = `
The user has been completing tasks very efficiently. Suggest 3 more challenging 
tasks that would stretch their abilities without overwhelming them.

Current skill level: Advanced
Recent completions: ${await getRecentCompletions(userId)}

Suggestions:
`;

  const suggestions = await llm.complete(prompt);

  await notifyUser(userId, {
    type: "challenge_suggested",
    message: "You're on fire! Ready for a greater challenge?",
    suggestions,
  });
}
```

### Procedural Content

```typescript
async function generateWorldExpansion(
  userId: string,
  milestoneType: string
): Promise<WorldRegion> {
  const theme = await getUserGameTheme(userId);

  const prompt = `
Generate a new region for the user's world after completing a ${milestoneType}.

Theme: ${theme}
Current regions: ${(await getWorldRegions(userId))
    .map((r) => r.name)
    .join(", ")}

Create:
1. Region name
2. Description (2-3 sentences)
3. Terrain type
4. 3 unique quest ideas
5. 1 boss encounter idea

JSON format:
`;

  const generated = await llm.complete(prompt);
  const regionData = JSON.parse(generated);

  // Create region in database
  return await createWorldRegion(userId, regionData);
}
```

---

## Visual Design

### Theme System

```typescript
interface GameTheme {
  themeId: string;
  name: string;
  description: string;

  // Color scheme
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };

  // UI elements
  uiStyle: "pixel-art" | "hand-drawn" | "modern" | "minimal";

  // Sound effects
  sfx: {
    taskComplete: string;
    levelUp: string;
    itemAcquired: string;
    questAccepted: string;
  };

  // Unlocked status
  unlockRequirements?: {
    level?: number;
    achievement?: string;
    premium?: boolean;
  };
}

const DEFAULT_THEMES: GameTheme[] = [
  {
    themeId: "fantasy-rpg",
    name: "Fantasy RPG",
    description: "Classic medieval fantasy with dragons and magic",
    colors: {
      primary: "#8B4513",
      secondary: "#FFD700",
      accent: "#DC143C",
      background: "#2C1810",
      text: "#F5DEB3",
    },
    uiStyle: "pixel-art",
    sfx: {
      taskComplete: "sword_slash.mp3",
      levelUp: "level_up_fanfare.mp3",
      itemAcquired: "item_get.mp3",
      questAccepted: "quest_accepted.mp3",
    },
  },
  {
    themeId: "sci-fi",
    name: "Sci-Fi Explorer",
    description: "Futuristic space exploration with alien worlds",
    colors: {
      primary: "#00CED1",
      secondary: "#7B68EE",
      accent: "#FF1493",
      background: "#0A0E27",
      text: "#E0FFFF",
    },
    uiStyle: "modern",
    sfx: {
      taskComplete: "laser_zap.mp3",
      levelUp: "warp_drive.mp3",
      itemAcquired: "scanner_beep.mp3",
      questAccepted: "mission_briefing.mp3",
    },
  },
];
```

### UI Components

```tsx
// Example React component for quest display
import React from "react";

interface QuestCardProps {
  quest: Quest;
  onAccept: (questId: string) => void;
}

export const QuestCard: React.FC<QuestCardProps> = ({ quest, onAccept }) => {
  return (
    <div className="quest-card" data-difficulty={quest.difficulty}>
      <div className="quest-header">
        <h3>{quest.title}</h3>
        <span className="difficulty-badge">{quest.difficulty}</span>
      </div>

      <div className="quest-narrative">{quest.narrative}</div>

      <div className="quest-rewards">
        <div className="reward-item">
          <span className="xp-icon">⭐</span>
          <span>{quest.rewards.xp} XP</span>
        </div>

        {quest.rewards.items && (
          <div className="reward-item">
            <span className="item-icon">🎁</span>
            <span>Possible Loot</span>
          </div>
        )}
      </div>

      <div className="quest-progress">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${quest.progress}%` }}
          />
        </div>
        <span>{quest.progress}% Complete</span>
      </div>

      {quest.status === "available" && (
        <button
          className="accept-quest-btn"
          onClick={() => onAccept(quest.questId)}
        >
          Accept Quest
        </button>
      )}
    </div>
  );
};
```

---

## Integration with AI Assistant

### Quest Assignment

When a task is created, automatically generate a quest:

```typescript
async function createTaskWithQuest(
  userId: string,
  taskData: TaskInput
): Promise<{ task: Task; quest: Quest }> {
  // Create task
  const task = await db.insert("tasks", {
    ...taskData,
    user_id: userId,
    created_at: new Date(),
  });

  // Generate quest narrative
  const narrative = await generateQuestNarrative(
    task,
    await getUserPreferences(userId)
  );

  // Create quest
  const quest = await db.insert("quests", {
    quest_id: `quest_${task.id}`,
    user_id: userId,
    title: task.title,
    description: task.description,
    narrative,
    type: determineQuestType(task),
    difficulty: task.difficulty || "medium",
    task_ids: [task.id],
    rewards: {
      xp: calculateQuestXP(task.difficulty || "medium"),
    },
    status: "available",
    progress: 0,
  });

  return { task, quest };
}
```

### Progress Updates

Update quest progress as tasks are completed:

```typescript
async function updateQuestProgress(questId: string): Promise<void> {
  const quest = await db
    .select()
    .from("quests")
    .where({ quest_id: questId })
    .first();

  if (!quest) return;

  // Check task completion
  const tasks = await db.select().from("tasks").whereIn("id", quest.task_ids);
  const completedTasks = tasks.filter((t) => t.status === "completed").length;
  const progress = (completedTasks / tasks.length) * 100;

  await db.update("quests").set({ progress }).where({ quest_id: questId });

  // If all tasks complete, complete quest
  if (progress === 100) {
    await completeQuest(questId);
  }
}

async function completeQuest(questId: string): Promise<void> {
  const quest = await db
    .select()
    .from("quests")
    .where({ quest_id: questId })
    .first();

  // Award XP
  await awardXP(
    quest.user_id,
    quest.rewards.xp,
    `Completed quest: ${quest.title}`
  );

  // Award items (if any)
  if (quest.rewards.items) {
    for (const item of quest.rewards.items) {
      await addItemToInventory(quest.user_id, item);
    }
  }

  // Update quest status
  await db
    .update("quests")
    .set({
      status: "completed",
      completed_at: new Date(),
    })
    .where({ quest_id: questId });

  // Check for achievements
  const newAchievements = await checkAchievements(quest.user_id);

  // Notify user
  await notifyUser(quest.user_id, {
    type: "quest_completed",
    quest,
    newAchievements,
  });

  // Generate story update
  const storyUpdate = await generateQuestCompletionStory(quest);
  await notifyUser(quest.user_id, {
    type: "story_update",
    content: storyUpdate,
  });
}
```

---

## Performance & Scalability

### Caching Game State

```typescript
class GameStateCache {
  private redis: RedisClient;

  async getCharacter(userId: string): Promise<Character | null> {
    const cached = await this.redis.get(`character:${userId}`);

    if (cached) {
      return JSON.parse(cached);
    }

    // Load from database
    const character = await db
      .select()
      .from("characters")
      .where({ user_id: userId })
      .first();

    // Cache for 1 hour
    await this.redis.setex(
      `character:${userId}`,
      3600,
      JSON.stringify(character)
    );

    return character;
  }

  async invalidateCharacter(userId: string): Promise<void> {
    await this.redis.del(`character:${userId}`);
  }
}
```

---

## Next Steps

1. **Design visual assets**: Create or commission pixel art for characters, items, UI elements
2. **Implement core game loop**: XP, leveling, quests
3. **Build quest generation system**: Integrate with AI for narratives
4. **Create social features**: Friends, teams, leaderboards
5. **Develop world map**: Procedural generation + visualization
6. **Testing**: Balance XP rates, quest difficulty, item drop rates

---

_Last Updated: November 7, 2025_

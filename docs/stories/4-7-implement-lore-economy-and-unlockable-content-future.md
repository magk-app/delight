# Story 4.7: Implement Lore Economy and Unlockable Content (Future)

**Story ID:** 4.7
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P2 (Future Enhancement)
**Estimated Effort:** 8-10 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** user,
**I want** to unlock deeper lore and world-building through consistent effort,
**So that** long-term commitment feels rewarding beyond just streaks.

---

## Context

### Problem Statement

Essence (narrative currency) is earned but not yet spent. Lore economy creates a progression system where users unlock:
- Extended character backstories
- World history codex entries
- Alternate scenario themes
- Cosmetic customizations

This rewards long-term engagement and creates additional goals beyond missions.

### Dependencies

- **Prerequisite Stories:**
  - 4.1 (Narrative Schema) ✅ - Essence tracking exists
  - 4.3 (Hidden Quests) ✅ - Essence rewards
  - Codex UI components (new)

---

## Acceptance Criteria

### AC1: Lore Entries Database Schema

**Given** the database exists
**When** I create lore entries table
**Then** it contains:
- id, scenario_id, category, title, content, unlock_cost, rarity
- Categories: "character_backstory", "world_history", "location_lore", "item_lore"
- Rarity levels: common (50 Essence), rare (200), legendary (500)

### AC2: Codex Interface Displays Available Lore

**Given** I have Essence to spend
**When** I open the Codex
**Then** I see:
- Locked lore entries with unlock costs
- Unlocked lore with rich formatting
- Categories for browsing (Characters, World, Locations, Items)
- Essence balance prominently displayed

### AC3: Lore Unlocking Mechanic

**Given** I have sufficient Essence
**When** I click "Unlock" on a lore entry
**Then**:
- Essence is deducted from balance
- Entry is unlocked and saved to user_unlocks table
- Content is revealed with beautiful formatting
- Unlock animation plays (treasure chest opening, etc.)

### AC4: Character Backstory Unlocks

**Given** I unlock a character backstory
**When** I read it
**Then** I learn:
- Character's origin story
- Motivations and fears
- Past relationships and events
- Connection to the world's history

**And** character mentions unlock in future dialogue

---

## Tasks / Subtasks

### Task 1: Create Lore Database Schema
- [ ] **1.1** Create lore_entries table
- [ ] **1.2** Create user_unlocks table (user_id, lore_entry_id, unlocked_at)
- [ ] **1.3** Seed lore entries for Modern Reality scenario
- [ ] **1.4** Add migration

### Task 2: Create Codex UI Components
- [ ] **2.1** Design Codex page (`/codex`)
- [ ] **2.2** Create LoreCard component (locked/unlocked states)
- [ ] **2.3** Create LoreReader component (beautiful formatting)
- [ ] **2.4** Add category navigation
- [ ] **2.5** Add Essence balance display

### Task 3: Implement Unlocking Mechanic
- [ ] **3.1** Create API endpoint: `POST /api/v1/lore/{lore_id}/unlock`
- [ ] **3.2** Implement Essence deduction logic
- [ ] **3.3** Save unlock to user_unlocks table
- [ ] **3.4** Return unlocked content
- [ ] **3.5** Add unlock animation to UI

### Task 4: Seed Lore Content
- [ ] **4.1** Write character backstories for Lyra, Thorne, Elara
- [ ] **4.2** Write world history entries
- [ ] **4.3** Write location lore for Arena, Observatory, Commons
- [ ] **4.4** Write artifact lore for special items

---

## Dev Notes

**Lore Categories:**

1. **Character Backstories** (200-500 Essence each):
   - Lyra's origin as a street artist
   - Thorne's past as competitive athlete
   - Elara's journey from student to professor

2. **World History** (100-300 Essence each):
   - The founding of the Arena
   - The Observatory's ancient purpose
   - The Commons' role in community building

3. **Location Lore** (150 Essence each):
   - Hidden details about each zone
   - Famous events that occurred there
   - Secrets and easter eggs

4. **Item Lore** (50-500 Essence each):
   - Origins of artifacts
   - Legendary wielders of items
   - Hidden properties

**Essence Economy Balance:**
- Hidden quests award 500-1000 Essence
- Daily missions award 15-50 Essence
- Average user earns ~200 Essence/week
- Lore entries cost 50-500 Essence
- Balance: 1-2 unlocks per week for active users

**Example Lore Entry:**

```json
{
  "id": "lyra_backstory_childhood",
  "category": "character_backstory",
  "character": "Lyra",
  "title": "Lyra's Childhood: The Street Artist",
  "content": "Long before Lyra became a master of craft...",
  "unlock_cost": 250,
  "rarity": "rare",
  "prerequisites": ["met_lyra", "relationship_level_3"],
  "rewards_on_unlock": {
    "relationship_boost": {"Lyra": 1},
    "title": "Lyra's Confidant"
  }
}
```

**References:**
- Epics File: `docs/epics.md` (Story 4.7, lines 1245-1307)
- Gamification patterns: Unlockable content, progression systems

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Implement after MVP narrative system and Essence economy are validated

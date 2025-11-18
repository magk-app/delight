# Story 4.6: Add Branching Narratives Based on User Choices (Future)

**Story ID:** 4.6
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P2 (Future Enhancement)
**Estimated Effort:** 10-12 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** user,
**I want** my choices to influence the story direction,
**So that** the narrative feels personalized and consequential.

---

## Context

### Problem Statement

Current narrative is linear - story beats generate based on achievements but don't branch based on user decisions. Adding branching narratives:
- Creates decision points within story beats
- Tracks user choices in narrative state
- Generates different story paths based on choices
- Makes story feel more interactive and personalized

### Dependencies

- **Prerequisite Stories:**
  - 4.1 (Narrative Schema) ✅ - story_progress.decisions array exists
  - 4.2 (Narrative Agent) ✅ - extends generate_content node
  - 4.4 (Story UI) ✅ - adds choice UI components

---

## Acceptance Criteria

### AC1: Decision Points in Story Beats

**Given** a story beat presents a decision
**When** the beat is displayed
**Then** user sees:
- Story text leading to decision point
- 2-3 meaningful choice options
- Brief preview of consequences
- Visual treatment (buttons or cards)

### AC2: Choice Tracking in Narrative State

**Given** user makes a choice
**When** the choice is submitted
**Then** it is stored in `narrative_state.story_progress.decisions`:
```json
{
  "decision_id": "choice_mentor_focus",
  "chapter": 1,
  "prompt": "Focus on Craft with Lyra or Health with Thorne?",
  "choice": "craft",
  "chosen_at": "2025-11-15T10:00:00Z",
  "consequences": ["stronger_lyra_relationship", "delayed_thorne_introduction"]
}
```

### AC3: Future Beats Reflect Past Choices

**Given** user has made choices
**When** new story beats generate
**Then** the narrative agent:
- Queries decision history from story_progress
- Includes choice context in GPT-4o prompt
- Generates beats consistent with past choices
- References consequences naturally in story

---

## Tasks / Subtasks

### Task 1: Extend Narrative Agent for Choices
- [ ] **1.1** Modify scenario templates to include decision points
- [ ] **1.2** Update generate_content node to detect choice beats
- [ ] **1.3** Add decision tracking to update_state node
- [ ] **1.4** Implement consequence propagation logic

### Task 2: Create Choice UI Components
- [ ] **2.1** Design ChoicePrompt component (2-3 options)
- [ ] **2.2** Add consequence preview tooltips
- [ ] **2.3** Implement choice submission handler
- [ ] **2.4** Add choice confirmation modal

### Task 3: Update Scenario Templates
- [ ] **3.1** Add branch points to Modern Reality scenario
- [ ] **3.2** Define choice options and consequences
- [ ] **3.3** Create branching story beat templates
- [ ] **3.4** Test different choice paths

---

## Dev Notes

**Choice Design Principles:**
- Choices should be meaningful (not cosmetic)
- Consequences should be visible in future beats
- No "wrong" choices - all paths valuable
- Limit to 2-3 options (avoid choice paralysis)

**Example Decision Point:**
```json
{
  "beat_type": "decision_point",
  "prompt": "Lyra offers to teach you advanced craft techniques, but Thorne says you need to focus on your health first. What do you prioritize?",
  "options": [
    {
      "id": "choice_craft",
      "label": "Learn from Lyra (Craft focus)",
      "consequence_preview": "Deepen relationship with Lyra, unlock craft mastery path"
    },
    {
      "id": "choice_health",
      "label": "Train with Thorne (Health focus)",
      "consequence_preview": "Build resilience, unlock health mastery path"
    },
    {
      "id": "choice_balance",
      "label": "Find a balanced approach",
      "consequence_preview": "Moderate progress in both, maintain flexibility"
    }
  ]
}
```

**References:**
- Epics File: `docs/epics.md` (Story 4.6, lines 1197-1241)
- Tech Spec: Branching narrative patterns

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Implement after MVP narrative system is validated

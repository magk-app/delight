# Story 4.4: Create Story Viewing Interface (MVP)

**Story ID:** 4.4
**Epic:** 4 - Narrative Engine
**Status:** drafted
**Priority:** P1 (User-Facing Narrative)
**Estimated Effort:** 8-10 hours
**Assignee:** Claude Dev Agent
**Created:** 2025-11-18

---

## User Story

**As a** user,
**I want** to read my personalized story as it unfolds,
**So that** I feel like my efforts are building toward something meaningful.

---

## Context

### Problem Statement

The narrative engine generates beautiful story beats, but users need an immersive interface to experience them. This story creates the MVP story viewing interface that:

1. **Displays story beats** in chronological order with beautiful typography
2. **Shows chapter/act progression** with visual indicators
3. **Provides navigation** between chapters and story sections
4. **Creates immersion** with theme-appropriate styling and animations
5. **Integrates with world state** to show character relationships, locations discovered, items acquired

The interface must feel like opening a book, not checking a to-do list. Typography, spacing, and animations create emotional engagement.

### Why This Approach?

**From Epics (epics.md lines 1097-1143):**

Story viewing must be:
- ✅ **Beautiful**: Serif fonts, generous spacing, fade-in animations
- ✅ **Immersive**: Theme-appropriate colors and styling
- ✅ **Navigable**: Easy chapter browsing, bookmarking
- ✅ **Informative**: Shows world state (characters, locations, items)

**From Tech Spec (tech-spec-epic-4.md):**
- Next.js page under `/narrative` route
- Framer Motion for smooth animations
- Server Components for initial load performance
- API endpoints for story data fetching

---

## Acceptance Criteria

### AC1: Narrative Page Route Exists with Beautiful Layout

**Given** I am logged in
**When** I navigate to `/narrative`
**Then** I see a beautiful story viewing interface with:
- Full-width immersive layout (no sidebars)
- Serif font for story text (e.g., Merriweather, Lora, or Crimson Pro)
- Theme-appropriate background (parchment texture for medieval, clean white for modern)
- Header with current chapter title and act indicator
- Navigation controls for browsing chapters

**Verification:**
- Visit http://localhost:3000/narrative
- Story interface loads with beautiful typography

### AC2: Story Beats Displayed in Chronological Order

**Given** I have narrative beats generated
**When** I view the narrative page
**Then** I see all my story beats displayed:
- **Newest first** (reverse chronological order)
- Each beat shows: title, text, character badges, timestamp
- Fade-in animation as beats appear
- Generous spacing between beats (3-4 rem)

**And** each beat is visually distinct with:
- Ornamental separators between beats
- Character avatars or icons for characters involved
- Emotional tone indicator (color accent or icon)

**Verification:**
```typescript
// In narrative page component
const beats = await fetchStoryBeats(userId);
beats.forEach(beat => {
  assert(beat.title);
  assert(beat.text);
  assert(beat.created_at);
});
```

### AC3: Chapter Navigation and Act Progression Indicators

**Given** my story spans multiple chapters and acts
**When** I view the narrative page
**Then** I see:
- **Current chapter indicator**: "Chapter 3: Facing Obstacles"
- **Act indicator**: "Act 2: Rising Challenge"
- **Chapter navigation**: Dropdown or tabs to view previous chapters
- **Progress indicator**: Visual bar showing progression through current act

**And** I can navigate to previous chapters:
- Click chapter selector
- View beats from that chapter only
- Return to latest chapter easily

**Verification:**
```typescript
<ChapterNav
  currentChapter={3}
  currentAct={2}
  chapters={[1, 2, 3, 4]}
  onChapterSelect={(ch) => loadBeats(ch)}
/>
```

### AC4: World State Summary Panel Shows Progress

**Given** I have made progress in the narrative
**When** I view the narrative page
**Then** I see a world state summary panel showing:

**Locations Discovered:**
- Icons for each discovered location (Arena, Observatory, Commons)
- Grayed-out icons for undiscovered locations (teaser)

**Characters Met:**
- Character portraits with relationship levels
- Visual relationship bars (0-10)
- "Not yet met" for undiscovered characters

**Items Acquired:**
- Essence balance: "450 Essence"
- Active title: "The Relentless"
- Artifacts: List of acquired items with icons

**Quests Unlocked:**
- Count of hidden quests unlocked
- Link to view quest details

**Verification:**
```typescript
<WorldStateSummary
  locations={{arena: true, observatory: false}}
  characters={{Lyra: {level: 3}, Thorne: {level: 1}}}
  essence={450}
  activeTitle="The Relentless"
/>
```

### AC5: Beautiful Typography and Immersive Styling

**Given** I am viewing story beats
**When** I read the story text
**Then** the typography creates immersion:
- **Font**: Serif (Merriweather, Lora, or Crimson Pro)
- **Size**: 18-20px for story text
- **Line height**: 1.8-2.0 for readability
- **Max width**: 650-750px (optimal reading width)
- **Letter spacing**: Slightly increased for elegance

**And** the theme styling matches scenario:
- **Modern theme**: Clean, minimalist, white background, sans-serif headers
- **Medieval theme**: Parchment texture, ornate separators, gothic headers
- **Sci-Fi theme**: Dark background, neon accents, futuristic fonts

**Verification:**
- Typography passes readability tests
- Text width never exceeds 750px
- Line height feels generous

### AC6: Fade-In Animations for New Beats

**Given** a new story beat is generated
**When** I visit the narrative page
**Then** the new beat appears with:
- Fade-in animation (opacity 0 → 1 over 0.5s)
- Slide-up effect (translateY 20px → 0)
- Smooth Framer Motion transitions

**And** previously viewed beats don't re-animate
- Mark beats as "viewed" in local storage or database
- Only animate new beats since last visit

**Verification:**
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  {beat.text}
</motion.div>
```

### AC7: API Endpoint Returns Story Data

**Given** the backend is running
**When** I call `GET /api/v1/narrative/story`
**Then** the API returns:
```json
{
  "scenario": {
    "id": "uuid",
    "name": "The Mirror's Edge",
    "theme": "modern"
  },
  "current_state": {
    "act": 1,
    "chapter": 3,
    "days_in_story": 45
  },
  "story_beats": [
    {
      "id": "beat-uuid",
      "chapter": 3,
      "title": "Lyra's Challenge",
      "text": "...",
      "emotional_tone": "inspiring",
      "characters_involved": ["Lyra"],
      "created_at": "2025-11-17T10:00:00Z"
    }
  ],
  "world_state": {
    "locations_discovered": ["arena", "commons"],
    "characters_met": ["Eliza", "Lyra"],
    "essence_balance": 450,
    "active_title": "The Relentless",
    "artifacts": [...]
  }
}
```

**Verification:**
```bash
curl http://localhost:8000/api/v1/narrative/story \
  -H "Authorization: Bearer $TOKEN"
```

### AC8: Responsive Design for Mobile and Desktop

**Given** I access the narrative page on any device
**When** I view the story
**Then** the interface adapts:
- **Desktop (≥1024px)**: Side panel for world state, full-width story
- **Tablet (768-1023px)**: Collapsed side panel, focused story view
- **Mobile (<768px)**: Full-width story, world state in expandable drawer

**And** typography scales appropriately:
- Base font size adjusts for screen size
- Line width optimized for reading on mobile

**Verification:**
- Test on multiple screen sizes
- Text remains readable at all sizes

---

## Tasks / Subtasks

### Task 1: Create Narrative Page Route (AC: #1)

- [ ] **1.1** Create `frontend/src/app/narrative/page.tsx`
- [ ] **1.2** Set up page layout:
  - Full-width container
  - Header with chapter/act info
  - Main story content area
  - Side panel for world state (desktop)
- [ ] **1.3** Add Clerk authentication check
- [ ] **1.4** Fetch user's story data on page load

### Task 2: Create StoryBeat Component (AC: #2, #5, #6)

- [ ] **2.1** Create `frontend/src/components/narrative/StoryBeat.tsx`
- [ ] **2.2** Implement beat display:
  - Title (h2, serif font)
  - Story text (p, serif font, generous spacing)
  - Character badges (icons/avatars)
  - Timestamp (subtle, bottom-right)
  - Emotional tone indicator (color accent)
- [ ] **2.3** Add Framer Motion animations:
  - Fade-in on mount
  - Slide-up effect
  - Only animate if new beat
- [ ] **2.4** Style with Tailwind CSS:
  - Serif font class
  - Max width 750px
  - Line height 1.8
  - Generous padding/margins

### Task 3: Create ChapterNav Component (AC: #3)

- [ ] **3.1** Create `frontend/src/components/narrative/ChapterNav.tsx`
- [ ] **3.2** Implement chapter selector:
  - Dropdown or tab interface
  - Current chapter highlighted
  - Act indicator
- [ ] **3.3** Add progress bar:
  - Visual indicator of act progression
  - Shows chapter count in current act
- [ ] **3.4** Handle chapter selection:
  - Filter beats by chapter
  - Smooth transition animation

### Task 4: Create WorldStateSummary Component (AC: #4)

- [ ] **4.1** Create `frontend/src/components/narrative/WorldStateSummary.tsx`
- [ ] **4.2** Display locations discovered:
  - Icon grid (Arena, Observatory, Commons)
  - Discovered locations colored, undiscovered grayed
  - Hover shows location name
- [ ] **4.3** Display characters met:
  - Character portraits/avatars
  - Relationship level bars
  - "Not yet met" for undiscovered characters
- [ ] **4.4** Display items:
  - Essence balance (large, prominent)
  - Active title badge
  - Artifact list (icons with tooltips)
- [ ] **4.5** Display unlocked quests count

### Task 5: Implement Theme Styling (AC: #5)

- [ ] **5.1** Create theme configuration:
  - Modern: Clean, white bg, sans-serif headers
  - Medieval: Parchment texture, ornate separators
  - Sci-Fi: Dark bg, neon accents
- [ ] **5.2** Add custom Tailwind CSS classes:
  - Serif font family (Merriweather via Google Fonts)
  - Theme-specific color palettes
- [ ] **5.3** Apply theme dynamically based on scenario.theme
- [ ] **5.4** Add theme switcher (optional, for testing)

### Task 6: Create API Endpoint (AC: #7)

- [ ] **6.1** Add to `backend/app/api/v1/narrative.py`:
  - `GET /api/v1/narrative/story`
- [ ] **6.2** Implement handler:
  - Load user's narrative_state
  - Load scenario_template
  - Query story_beats for user
  - Build world_state summary from narrative_state
- [ ] **6.3** Add Pydantic response schema:
  - `StoryResponse` with scenario, current_state, story_beats, world_state
- [ ] **6.4** Add authentication middleware
- [ ] **6.5** Add error handling

### Task 7: Implement Responsive Design (AC: #8)

- [ ] **7.1** Add responsive breakpoints:
  - Desktop: ≥1024px (side panel visible)
  - Tablet: 768-1023px (collapsed side panel)
  - Mobile: <768px (drawer for world state)
- [ ] **7.2** Adjust typography for mobile:
  - Slightly smaller font size
  - Maintained line height
- [ ] **7.3** Test on multiple screen sizes
- [ ] **7.4** Add mobile navigation drawer for world state

### Task 8: Add Framer Motion Animations (AC: #6)

- [ ] **8.1** Install Framer Motion: `npm install framer-motion`
- [ ] **8.2** Wrap StoryBeat in motion.div
- [ ] **8.3** Add animation variants:
  - initial: {opacity: 0, y: 20}
  - animate: {opacity: 1, y: 0}
  - transition: {duration: 0.5}
- [ ] **8.4** Track viewed beats:
  - Store beat IDs in localStorage
  - Only animate new beats

### Task 9: Create Custom Fonts and Typography (AC: #5)

- [ ] **9.1** Add Google Fonts to `layout.tsx`:
  - Merriweather (serif, for story text)
  - Inter (sans-serif, for UI elements)
- [ ] **9.2** Configure Tailwind CSS:
  - Add custom font families
  - Set default serif class
- [ ] **9.3** Create typography utility classes:
  - `.story-text` - Serif, 18px, line-height 1.8
  - `.story-title` - Serif, 24px, bold
  - `.chapter-heading` - Sans-serif, 32px, bold

### Task 10: Add Loading and Empty States (AC: All)

- [ ] **10.1** Add loading skeleton:
  - Show placeholder beats while loading
  - Shimmer animation
- [ ] **10.2** Add empty state:
  - "Your story begins when you complete your first missions"
  - Illustration or icon
  - CTA to view missions
- [ ] **10.3** Add error state:
  - "Failed to load your story"
  - Retry button

### Task 11: Create Unit Tests (AC: All)

- [ ] **11.1** Create `frontend/src/components/narrative/__tests__/`
- [ ] **11.2** Test StoryBeat component:
  - Renders beat data correctly
  - Applies animations
  - Handles character badges
- [ ] **11.3** Test ChapterNav component:
  - Chapter selection works
  - Progress indicator accurate
- [ ] **11.4** Test WorldStateSummary component:
  - Displays world state correctly
  - Handles missing data

### Task 12: Create E2E Tests (AC: All)

- [ ] **12.1** Create Playwright test: `tests/e2e/narrative.spec.ts`
- [ ] **12.2** Test narrative page load:
  - Page renders
  - Story beats display
  - World state shows
- [ ] **12.3** Test navigation:
  - Chapter switching works
  - Animations trigger
- [ ] **12.4** Test responsive design:
  - Mobile layout works
  - World state drawer functional

### Task 13: Documentation (AC: All)

- [ ] **13.1** Document component props and usage
- [ ] **13.2** Add Storybook stories for components (optional)
- [ ] **13.3** Create `docs/epic-4/NARRATIVE-UI-GUIDE.md`:
  - Component overview
  - Theme customization
  - Animation patterns
- [ ] **13.4** Update API documentation

---

## Dev Notes

### Typography and Reading Experience

Beautiful typography creates emotional engagement:

```css
/* Story text styling */
.story-text {
  font-family: 'Merriweather', Georgia, serif;
  font-size: 18px;
  line-height: 1.8;
  max-width: 650px;
  margin: 0 auto;
  color: #1a1a1a;
  letter-spacing: 0.01em;
}

/* Story title */
.story-title {
  font-family: 'Merriweather', Georgia, serif;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #000;
}

/* Chapter heading */
.chapter-heading {
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 2rem;
}
```

### Theme Configuration

```typescript
// frontend/src/lib/themes/narrative.ts

export const narrativeThemes = {
  modern: {
    background: '#ffffff',
    textColor: '#1a1a1a',
    accentColor: '#3b82f6',
    fontSerif: 'Merriweather',
    fontSans: 'Inter',
    beatSeparator: 'solid-line'
  },
  medieval: {
    background: '#f4f1ea', // Parchment
    textColor: '#2d2416',
    accentColor: '#8b4513',
    fontSerif: 'Crimson Pro',
    fontSans: 'Cinzel',
    beatSeparator: 'ornate-border'
  },
  scifi: {
    background: '#0a0e1a',
    textColor: '#e0e0e0',
    accentColor: '#00ffff',
    fontSerif: 'Orbitron',
    fontSans: 'Rajdhani',
    beatSeparator: 'neon-line'
  }
};
```

### Framer Motion Animation Patterns

```typescript
// frontend/src/components/narrative/StoryBeat.tsx

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function StoryBeat({ beat }) {
  const [isViewed, setIsViewed] = useState(false);

  useEffect(() => {
    // Check if beat was previously viewed
    const viewedBeats = JSON.parse(localStorage.getItem('viewedBeats') || '[]');
    setIsViewed(viewedBeats.includes(beat.id));

    // Mark as viewed
    if (!viewedBeats.includes(beat.id)) {
      viewedBeats.push(beat.id);
      localStorage.setItem('viewedBeats', JSON.stringify(viewedBeats));
    }
  }, [beat.id]);

  return (
    <motion.article
      initial={isViewed ? false : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="story-beat"
    >
      <h2 className="story-title">{beat.title}</h2>
      <div className="story-text">
        {beat.text.split('\n\n').map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>
      <div className="beat-metadata">
        {beat.characters_involved.map(char => (
          <CharacterBadge key={char} name={char} />
        ))}
        <time>{formatDate(beat.created_at)}</time>
      </div>
    </motion.article>
  );
}
```

### API Integration

```typescript
// frontend/src/lib/api/narrative.ts

export async function fetchStoryBeats(userId: string) {
  const response = await fetch(`/api/v1/narrative/story`, {
    headers: {
      'Authorization': `Bearer ${getClerkToken()}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch story');
  }

  return response.json();
}
```

### Learnings from Previous Stories

**From Story 2.5 (Companion Chat UI - assumed):**
- Next.js App Router patterns
- Clerk authentication integration
- Component organization

**From Story 4.2 (Narrative Agent):**
- StoryBeat data structure
- Emotional tone types
- Character involvement

**From Story 4.1 (Narrative Schema):**
- World state structure
- Scenario themes
- Chapter/act organization

### Project Structure Notes

**New Files Created:**

```
packages/frontend/
├── src/
│   ├── app/
│   │   └── narrative/
│   │       └── page.tsx                      # NEW: Narrative page route
│   ├── components/
│   │   └── narrative/
│   │       ├── StoryBeat.tsx                 # NEW: Beat display component
│   │       ├── ChapterNav.tsx                # NEW: Chapter navigation
│   │       ├── WorldStateSummary.tsx         # NEW: World state panel
│   │       └── __tests__/                    # NEW: Component tests
│   └── lib/
│       ├── api/
│       │   └── narrative.ts                   # NEW: API client
│       └── themes/
│           └── narrative.ts                   # NEW: Theme config
└── tests/
    └── e2e/
        └── narrative.spec.ts                  # NEW: E2E tests
```

### Relationship to Epic 4 Stories

This story (4.4) **displays**:
- **Story 4.2**: Generated story beats
- **Story 4.3**: Unlocked hidden quests
- **Story 4.1**: World state (locations, characters, items)

**Dependencies Flow:**

```
Story 4.1 (Narrative Schema)
    ↓
Story 4.2 (Narrative Agent)
    ↓
Story 4.3 (Hidden Quests)
    ↓
Story 4.4 (Story UI) ← THIS STORY
    = Living Narrative Experience! 📖
```

### References

**Source Documents:**
- **Epic 4 Tech Spec**: `docs/tech-spec-epic-4.md`
- **Epics File**: `docs/epics.md` (Story 4.4, lines 1097-1143)
- **Architecture**: `docs/ARCHITECTURE.md` (Frontend patterns)

**Technical Documentation:**
- **Next.js 15**: https://nextjs.org/docs
- **Framer Motion**: https://www.framer.com/motion/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## Definition of Done

- [ ] ✅ `/narrative` page route created and accessible
- [ ] ✅ Story beats display with beautiful typography
- [ ] ✅ Chapter navigation functional
- [ ] ✅ World state summary panel shows locations, characters, items
- [ ] ✅ Theme styling implemented (at least Modern theme)
- [ ] ✅ Fade-in animations working
- [ ] ✅ API endpoint returns story data correctly
- [ ] ✅ Responsive design works on mobile/tablet/desktop
- [ ] ✅ Loading and empty states handled
- [ ] ✅ Unit tests pass for all components
- [ ] ✅ E2E tests pass for narrative page
- [ ] ✅ Typography is readable and beautiful
- [ ] ✅ Documentation complete
- [ ] ✅ No secrets committed
- [ ] ✅ Story status updated to `done` in `docs/sprint-status.yaml`

---

## Implementation Notes

### Estimated Timeline
- **Task 1-2** (Page + StoryBeat): 2 hours
- **Task 3-4** (Navigation + World State): 2 hours
- **Task 5** (Theme Styling): 1.5 hours
- **Task 6** (API Endpoint): 1 hour
- **Task 7** (Responsive Design): 1 hour
- **Task 8** (Animations): 1 hour
- **Task 9** (Typography): 1 hour
- **Task 10** (States): 30 minutes
- **Task 11-12** (Tests): 2 hours
- **Task 13** (Documentation): 1 hour

**Total:** 13.5 hours (adjust to 10 hours focusing on MVP features)

---

**Last Updated:** 2025-11-18
**Story Status:** drafted
**Next Steps:** Create context file, implement UI components with beautiful typography

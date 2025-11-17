# Epic 5: Progress & Analytics

**Epic Goal:** Build momentum storytelling through streaks, highlight reels, and the Daily Consistency Index (DCI) dashboard so users see their progress compounding over time.

**Architecture Components:** Progress service, analytics pipeline, PostgreSQL for metrics, frontend dashboards

### Story 5.1: Implement Streak Tracking System

As a **user**,  
I want **to build and maintain streaks for consistent work**,  
So that **I feel motivated to show up daily**.

**Acceptance Criteria:**

**Given** I'm working on missions  
**When** I complete at least one mission on consecutive days  
**Then** my streak counter increments

**And** I can see my current streak:

- Total days count
- Start date
- Value category streaks (health/craft/growth/connection separately)

**And** when I miss a day:

- Streak resets (or uses "streak freeze" if available)
- I'm notified compassionately (not shaming)

**And** streak milestones are celebrated:

- 7 days, 14 days, 30 days, 100 days, 365 days
- Badge/achievement unlocked
- Eliza congratulates me

**Prerequisites:** Story 3.4 (mission completion tracking)

**Technical Notes:**

- Schema: `streaks` table (user_id FK, streak_type ENUM[overall/health/craft/growth/connection], current_streak INT, longest_streak INT, last_activity_date DATE, streak_freeze_available BOOLEAN)
- Calculate daily: ARQ worker checks if user completed mission yesterday
- Frontend: prominent streak display in header/dashboard
- MVP: no streak freeze, add in future

---

### Story 5.2: Build Daily Consistency Index (DCI) Dashboard

As a **user**,  
I want **a quantitative measure of my overall consistency**,  
So that **I can see patterns and understand what's working**.

**Acceptance Criteria:**

**Given** I have at least 7 days of activity  
**When** I view the DCI dashboard  
**Then** I see my Daily Consistency Index score (0-1.0):

- Calculated from: streak, mission completion rate, goal engagement, nudge responses
- Shown as percentage (e.g., "DCI: 73%")
- Color-coded (red/yellow/green zones)

**And** I see trend visualizations:

- 7-day, 30-day, 90-day views
- Line chart of DCI over time
- Breakdown by value category

**And** I get insights:

- "You're most consistent with Health missions (82%)"
- "Your DCI peaks on Tuesday mornings"
- "20% improvement since last month"

**Prerequisites:** Story 5.1 (streak tracking), Story 3.4 (mission sessions)

**Technical Notes:**

- Service: `backend/app/services/progress_service.py`
- DCI formula: `weighted_average(streak_factor, completion_rate, engagement_depth, response_rate)`
- Store daily DCI snapshots in `dci_history` table for trend analysis
- Frontend: `frontend/src/app/progress/page.tsx`
- Use Chart.js or Recharts for visualizations

---

### Story 5.3: Generate Highlight Reels (MVP)

As a **user**,  
I want **cinematic summaries of my accomplishments**,  
So that **I can celebrate progress and share my journey**.

**Acceptance Criteria:**

**Given** I've completed significant milestones (goal completed, 7-day streak, chapter unlock)  
**When** a highlight reel is generated  
**Then** I see a beautiful summary including:

- Title: "Your 7-Day Journey in Craft"
- Key accomplishments listed
- Motivational quote or Eliza message
- Stats: missions completed, time invested, streak maintained

**And** the reel has visual polish:

- Animated transitions
- Value category colors/icons
- Timeline visualization
- Optional: music/sound effects (future)

**And** I can:

- View past highlight reels
- Export as image/PDF
- Share to social media (opt-in, privacy-aware)

**Prerequisites:** Story 5.1 (streaks), Story 3.4 (mission completion data)

**Technical Notes:**

- Service: `backend/app/services/highlight_service.py`
- Trigger: ARQ worker generates reels on milestone events
- Store in `highlight_reels` table (user_id FK, milestone_type, content JSONB, generated_at)
- Frontend: `HighlightReel.tsx` component with Framer Motion animations
- MVP: text+data reels; future: video generation with AI narration

---

### Story 5.4: Implement Progress Snapshots and Goal Timelines

As a **user**,  
I want **to see visual timelines of my goal progress**,  
So that **I can track momentum toward long-term objectives**.

**Acceptance Criteria:**

**Given** I have active goals  
**When** I view a goal's progress page  
**Then** I see:

- Timeline of all missions completed for that goal
- Milestones marked on timeline
- Velocity chart (missions/week over time)
- Estimated completion date based on current pace

**And** I can:

- Filter by date range
- See notes from each mission session
- Identify gaps (periods of inactivity)

**And** progress snapshots are stored weekly:

- Captures goal state every Sunday
- Allows historical comparison ("4 weeks ago vs now")

**Prerequisites:** Story 3.1 (goals), Story 3.4 (mission sessions)

**Technical Notes:**

- Schema: `progress_snapshots` table (goal_id FK, snapshot_date DATE, missions_completed INT, completion_percentage FLOAT, velocity FLOAT, notes TEXT)
- ARQ worker: runs weekly to create snapshots
- Frontend: `GoalTimeline.tsx` with interactive chart
- Use date-fns for date calculations

---

### Story 5.5: Add "What's Working" Analytics Insights (Future)

As a **user**,  
I want **AI-generated insights about my productivity patterns**,  
So that **I can optimize when and how I work**.

**Acceptance Criteria:**

**Given** I have at least 30 days of data  
**When** I view analytics insights  
**Then** I see personalized observations:

- "You complete 3x more missions on Tuesday mornings"
- "Health missions after 8am have 90% completion rate"
- "Your streaks break most often on Fridays"
- "Missions under 20min have highest completion rate"

**And** Eliza uses insights to:

- Recommend optimal mission times
- Adjust mission difficulty
- Suggest scheduling changes

**And** insights are updated monthly

**Prerequisites:** Story 5.2 (DCI dashboard with analytics data)

**Technical Notes:**

- Use LLM to generate natural language insights from analytics data
- Store in `user_insights` table with timestamps
- Pattern detection: time-of-day analysis, day-of-week trends, mission length preferences
- Privacy: insights never leave user's data context

---

### Story 5.6: Implement Achievement Gallery and Badges (Future)

As a **user**,  
I want **to collect badges and achievements for milestones**,  
So that **long-term progress feels tangibly rewarding**.

**Acceptance Criteria:**

**Given** I reach various milestones  
**When** I unlock achievements  
**Then** I receive badges such as:

- **The Starter**: Complete first mission
- **Week Warrior**: 7-day streak
- **Century**: 100 missions completed
- **The Relentless**: 20-day streak in one value category
- **Master Planner**: Decompose 10 goals with Eliza

**And** badges are displayed:

- In my profile/progress page
- Shareable on social media
- Visible to pod members (if in multiplayer)

**And** achievements come in tiers:

- Bronze, Silver, Gold, Platinum
- Unlocking higher tiers grants Essence

**Prerequisites:** Story 5.1 (milestones), Story 4.7 (Essence economy)

**Technical Notes:**

- Schema: `achievements` table (id, name, description, tier, unlock_criteria JSONB, icon_url)
- Schema: `user_achievements` table (user_id FK, achievement_id FK, unlocked_at, tier)
- Define achievement criteria in seed data
- Worker checks criteria daily
- Frontend: badge gallery with filters and search

---

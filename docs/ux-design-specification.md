# UX Design Specification: Delight

**Version:** 1.0  
**Date:** 2025-11-09  
**Author:** Sally (UX Designer) with Jack  
**Project:** Delight - A story for ambitious people who want to transform their lives  
**Status:** Design Complete - Ready for Development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy & Principles](#design-philosophy--principles)
3. [Visual Design System](#visual-design-system)
4. [Core Components](#core-components)
5. [User Flows](#user-flows)
6. [Interaction Patterns](#interaction-patterns)
7. [Responsive Behavior](#responsive-behavior)
8. [Technical Considerations](#technical-considerations)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

### Project Vision

Delight is **not just a companion app**—it's **a story for ambitious people who want to transform their lives**. The product blends real-world goal achievement with narrative world-building, where users' actual work drives a personalized, AI-generated story with persistent characters, meaningful stakes, and visible transformation.

### Core Experience

Users enter a living narrative world that mirrors their real-life situation. Through daily missions that correspond to real work, they earn resources (Essence), build relationships with AI companions, unlock new zones, and progress through story chapters that celebrate their actual life transformation.

### Key Differentiators

- **Story-driven productivity:** Real work generates narrative progression
- **AI-generated personalization:** Stories adapt to user context and goals
- **Living world with time dynamics:** World state changes based on real-world time
- **Deep companion relationships:** Named protagonist (Eliza) + attribute-based characters
- **Multiple narrative scenarios:** Modern reality, medieval fantasy, sci-fi, cyberpunk, zombie apocalypse, and more

---

## Design Philosophy & Principles

### 1. Efficiency Through Understanding

**"Empathy enables efficiency. Efficiency is the goal."**

The ultimate measure of success is: Did the user make meaningful progress? Emotional intelligence and storytelling are **tools** to diagnose blockers and unlock action, not ends in themselves.

### 2. The World Is a Character

The narrative environment is as important as Eliza. Navigation feels rich and explorable—whether text-based or visual, it must be a **good adventure** with mystery, depth, and emergent storytelling.

### 3. Flexible Fidelity

Offer both decorative richness (for users who want immersive world-building) AND efficient minimalism (for those who want clean dashboards). The interface adapts to preference without forcing a single aesthetic.

### 4. Modern Warmth

Contemporary design language (clean lines, sophisticated interactions) avoids sterile tech aesthetics. Warm colors, thoughtful animations, and gentle micro-interactions make efficiency feel **good**.

### 5. Visible Progress Compounds Trust

Every mission, streak, or milestone must be tangible. Highlight reels, narrative beats, and environmental changes prove effort is working—this visibility drives engagement more than any feature.

### 6. Living, Breathing World

The world operates on real-world time. Morning opens more opportunities; night brings quiet reflection. This temporal dimension helps users build healthy rhythms while making the world feel **alive**.

### 7. Stories That Surprise

Pre-planned narrative arcs, hidden quests, and character-initiated events create genuine discovery. The AI generates stories with planned endings not revealed upfront, building anticipation and investment.

---

## Visual Design System

### Color Palette

#### Base Palette (Efficient Mode)

- **Base:** Soft whites, warm grays (#F8F9FA, #E9ECEF, #343A40)
- **Primary:** Warm amber/gold (#FF9F43, #F79F1F) - Progress, wins, Essence
- **Secondary:** Soft purple/blue (#A55EEA, #5F27CD) - Eliza presence, wisdom
- **Success:** Warm green (#26DE81) - Mission complete, growth
- **Alert:** Gentle orange (#FDA7DF) - Notifications, reminders
- **Text:** Dark charcoal (#2C3E50) primary, lighter (#7F8C8D) secondary

#### Decorative Themes (User-Customizable)

**Modern Reality (SF/NY/Tokyo):**

- Urban blues and grays
- Neon accent highlights
- Glass/metal textures

**Medieval Fantasy:**

- Earth tones (browns, forest greens)
- Gold and bronze accents
- Parchment textures, stone overlays

**Star Trek 2000s (Sci-Fi):**

- Cool blues and whites
- Cyan holographic accents
- Sleek metallic surfaces

**Cyberpunk Future:**

- Dark backgrounds (near-black)
- Neon pink, cyan, purple accents
- Glitch effects, scan lines

**Zombie Apocalypse:**

- Desaturated colors (grays, muted greens)
- Red danger accents
- Weathered, distressed textures

**Additional Scenarios:**

- **Cop/Detective:** Film noir blacks, yellow crime tape accents
- **Presidential:** Patriotic colors, marble/wood textures
- **More added over time based on user demand**

### Typography

**Primary Font:** Inter or Plus Jakarta Sans

- Headers: 24-48px, weight 600-700
- Body: 16-18px, weight 400, line-height 1.6
- Small text: 14px, weight 400

**Narrative Font (Optional):** Decorative font for story text in immersive mode

- Use sparingly for chapter titles, character dialogue headers

**Principles:**

- Generous spacing for readability
- High contrast ratios (WCAG AA minimum)
- Scalable for accessibility

### Component Design Language

**Cards:** Rounded corners (8-12px), subtle shadows, clear hierarchy  
**Buttons:** Primary (filled), Secondary (outlined), Ghost (text only)  
**Inputs:** Minimal borders, focus states with color shift  
**Avatars:** Circular for characters, animated with subtle breathing  
**Progress Bars:** Smooth animations, gradient fills for visual interest  
**Badges:** Small, colorful, celebrate achievements

---

## Core Components

### 1. Eliza - The Protagonist Companion

**Name Origin:** Homage to ELIZA, the classical AI companion (1966)

**Personality:**

- Empathetic but directive
- Celebrates wins genuinely
- Validates struggles without enabling avoidance
- Adapts tone based on user state (supportive, encouraging, urgent, celebratory)
- Proactive: Initiates conversations, suggests new goals, asks about user's well-being

**Visual Representation:**

- Animated avatar (2D illustrated or subtle 3D)
- Expresses emotion through subtle animations (concern, joy, focus)
- Positioned prominently but non-intrusively
- Avatar adapts to theme (modern outfit in NY, robes in fantasy, etc.)

**Core Interactions:**

- Daily emotional check-ins
- Mission briefings and debriefs
- Progress celebrations
- Drift detection and gentle nudges
- Deep coaching when user struggles
- **Character-initiated requests:** "Jack, can I ask you something? I think you might enjoy trying..."

---

### 2. Dynamic Conversation Interface

**Layout:**

- Full-screen or primary panel (not sidebar)
- Chat-based interaction with rich message types
- Story paragraphs expand for depth
- Embedded cards for missions, progress, character encounters

**Message Types:**

**Story Paragraphs:**

```
Expanded, literary narrative that sets scenes,
builds mystery, and creates atmosphere.

"The morning fog clings to the streets of
San Francisco as you step outside your apartment.
Coffee shops are just opening, their warm light
spilling onto sidewalks. You have a meeting at
10am—a job interview that could change everything.

But first, you need to prepare. Eliza pings you:

'Jack, you've rehearsed this twice already.
One more run-through, or do you trust yourself?'

What do you do?"
```

**Mission Cards:**

```
┌──────────────────────────────────┐
│ 📝 Prepare for Interview         │
│ ⏱️ 30 min • 25 Essence           │
│ 🎯 Growth +15 XP                 │
│                                  │
│ Review talking points, practice  │
│ answers, visualize success       │
│                                  │
│ [Start Mission] [Postpone]       │
└──────────────────────────────────┘
```

**Character Dialogue:**

```
[Character Avatar: Lyra]
💜 Lyra (Craft Companion)

"I heard your interview is today.
Nervous? That's good—it means you care.

Want to ship one small project before
you go? Confidence builder."
```

**Progress Snapshots:**

```
YOUR WEEK:
🔥 7-day streak
🎨 Craft Level 3 → 4
💰 +250 Essence earned
📖 1 book finished

"You're not the same person who
started this week."
```

---

### 3. Mission Interface - Full Screen Experience

**Design Philosophy:** Missions deserve full attention, not minimized corner widgets.

**Layout:**

```
┌──────────────────────────────────────────────┐
│ MISSION IN PROGRESS                          │
├──────────────────────────────────────────────┤
│                                              │
│ PREPARE FOR INTERVIEW                        │
│ Time: 18 minutes elapsed / 30 estimated      │
│ [████████████░░░░░░░░] 60%                   │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ [User Work Area]                             │
│ • Upload evidence of work (photos/notes)     │
│ • Text notes about what you're doing         │
│ • Quick voice memo capture                   │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ 📸 Upload Photo of Your Work           │  │
│ │ [Drag & drop or click]                 │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ [Eliza - Minimized but Present]             │
│ "You're doing great. Stay with it."          │
│                                              │
│ Notifications: [🔔 2 nudges available]       │
│ • Reminder: Interview in 2 hours             │
│ • New quest available from Commander Thorne  │
│                                              │
│ [Complete Mission] [Take Break] [Need Help]  │
└──────────────────────────────────────────────┘
```

**Key Features:**

- Full-screen focus mode
- Progress visualization
- Evidence capture (photos, notes, voice)
- Gentle nudges/reminders surface inline
- Eliza present but not intrusive
- Flexible completion (user declares "done")

---

### 4. Living World with Time Dynamics

**Concept:** The narrative world operates on real-world time, creating temporal rhythms.

**Time-Based State Changes:**

**Morning (6am - 12pm):**

- Most zones open and bustling
- NPCs greet you energetically
- "Good morning" missions available
- Coffee shops, gyms, libraries full
- Optimal time for Growth and Health missions

**Afternoon (12pm - 6pm):**

- Peak activity hours
- All zones accessible
- Collaborative missions available
- Social areas most active
- Balanced mission availability

**Evening (6pm - 10pm):**

- Some zones begin closing
- Reflective missions surface
- Characters check in on your day
- Observatory becomes primary hub
- Focus on review and planning

**Night (10pm - 6am):**

- Most zones closed
- Quiet, introspective atmosphere
- "Late night work" missions available
- Eliza suggests rest: "The world will be here tomorrow."
- Optional: insomnia support rituals

**User Control:**

- Can override time restrictions: "I work nights—keep everything open"
- Set custom rhythms: "My productive hours are 10pm-2am"
- Time-zone aware

**Example Narrative:**

```
EVENING - 8:47 PM, San Francisco

The city transitions into night. Street lamps
flicker on. Most workers head home, but you're
still at it.

The Arena is closing soon—Thorne offers one
last session before he locks up.

The Observatory remains open all night. Elara
invites you: "Late-night learning? I'll put on
tea."

What do you choose?
```

---

### 5. Scenario Templates - Rich, Pre-Planned Narratives

**Design Principle:** AI generates stories with:

- Deep mystery and intrigue
- Planned (but hidden) endings
- Character arcs that unfold over weeks
- Emergent side quests
- Callbacks to earlier events

#### Scenario 1: Modern Reality (SF/NY/Tokyo)

**Setting:** Ambitious professional in a major city  
**Core Conflict:** Building career from scratch, surviving competitive job market  
**Narrative Arc:**

- Act 1: Job hunting, skill building, networking
- Act 2: Land first opportunity, prove yourself
- Act 3: Major project launch, industry recognition

**Pre-Planned Mystery:**

```
Hidden throughout Act 1-2: Clues about a major
tech company hiring for a dream role. NPCs drop
hints. When user reaches Level 10 Craft, an
anonymous recruiter reaches out.

Surprise twist: The recruiter is someone you
helped in Act 1.
```

**Characters:**

- Eliza (guide)
- Mentor (experienced engineer)
- Rival (competitive peer)
- Friend (supportive accountability partner)

---

#### Scenario 2: Medieval Fantasy

**Setting:** Arrival at kingdom in turmoil  
**Core Conflict:** Earn place in society, help rebuild fractured realm  
**Narrative Arc:**

- Act 1: Penniless arrival, take odd jobs, meet Guild members
- Act 2: Join Guild, undertake Trials, earn rank
- Act 3: Realm-wide crisis, your skills critical to resolution

**Pre-Planned Mystery:**

```
The Kingdom fell because of a betrayal 20 years
ago. As you progress, you uncover clues.

By Act 3, you realize: The betrayer is still
here, and only you can expose them before they
strike again.
```

**Characters:**

- Eliza (traveling companion)
- Archmage Elara (wisdom keeper)
- Commander Thorne (warrior trainer)
- Lyra (master artisan)
- The Shadowed One (mysterious antagonist)

---

#### Scenario 3: Star Trek 2000s (Sci-Fi)

**Setting:** Cadet joining Starfleet-like organization  
**Core Conflict:** Prove worth, earn command, explore unknown space  
**Narrative Arc:**

- Act 1: Academy training, first assignments
- Act 2: Join crew, critical missions
- Act 3: Lead expedition to mysterious signal

**Pre-Planned Mystery:**

```
A signal from deep space appears intermittently.
Each mission brings you closer to understanding
it. Final reveal: It's from humanity's future,
warning of a choice you must make.
```

---

#### Scenario 4: Cyberpunk Future

**Setting:** Hacker in neon-soaked megacity  
**Core Conflict:** Survive corporate warfare, uncover conspiracy  
**Narrative Arc:**

- Act 1: Freelance gigs, build rep, avoid corps
- Act 2: Hired by faction, deeper into conspiracy
- Act 3: Choose side in corp war, reshape city

**Pre-Planned Mystery:**

```
The megacity's AI overlord is slowly dying.
Corps are fighting to control its replacement.
You discover: Your work is training the new AI.
What values will it have?
```

---

#### Scenario 5: Zombie Apocalypse

**Setting:** Survivor in post-outbreak world  
**Core Conflict:** Secure shelter, find supplies, rebuild community  
**Narrative Arc:**

- Act 1: Scavenging, surviving day-to-day
- Act 2: Establish safe zone, recruit survivors
- Act 3: Major settlement, hope returns

**Pre-Planned Mystery:**

```
Radio signals suggest a cure exists. Clues
scattered across missions. Final act: Journey
to source. Twist: Cure requires sacrifice. Will
you take it?
```

---

#### Additional Scenarios (Expand Over Time)

**Cop/Detective:**

- Solve cases, climb ranks, uncover corruption
- Mystery: Partner is involved in case you're solving

**Presidential Campaign:**

- Run for office, build coalition, navigate crises
- Mystery: Opponent knows your secrets; how?

**Space Explorer:**

- Chart new worlds, manage crew, first contact

**Underground Rebellion:**

- Topple oppressive regime, build resistance

---

### 6. Multi-Dimensional Progress Dashboard

**Layout:**

```
┌──────────────────────────────────────────────┐
│ YOUR PROGRESS CONSTELLATION ✨               │
├──────────────────────────────────────────────┤
│                                              │
│ 🌱 GROWTH            Level 12  ▰▰▰▰▰▱       │
│    📖 Books: 3 read this quarter             │
│    🎓 Courses: Design Thinking (67%)         │
│    🗣️ Deep Convos: 2 this week              │
│    [View details]                            │
│                                              │
│ 💪 HEALTH            Level 8   ▰▰▰▰▱▱       │
│    🏋️ Gym: 5 sessions this week             │
│    🧘 Meditation: 3/7 days                   │
│    😴 Sleep: 7.2 hrs avg                    │
│    [View details]                            │
│                                              │
│ 🎨 CRAFT             Level 15  ▰▰▰▰▰▰       │
│    📝 Writing: 8,400 words/month             │
│    🎨 Projects: 2 shipped, 1 active         │
│    💻 Commits: 43 this week                  │
│    [View details]                            │
│                                              │
│ 🤝 CONNECTION        Level 5   ▰▰▱▱▱▱       │
│    👥 New friends: 2 this quarter            │
│    💬 Quality time: 4 hrs/week               │
│    🏘️ Commons: Unlocked                     │
│    [View details]                            │
│                                              │
│ [+ Add Custom Progress Type]                 │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ QUICK STATS:                                 │
│ 🔥 Current streak: 14 days                   │
│ 💰 Essence balance: 485                      │
│ 📅 Time in story: 3 weeks                    │
│ 📖 Current chapter: Building Your Legacy     │
│                                              │
└──────────────────────────────────────────────┘
```

**Custom Progress Types:**

Users can track anything:

- "Paintings completed" → maps to Craft
- "Cold emails sent" → maps to Connection
- "Piano practice hours" → maps to Growth or Craft
- "Date nights" → maps to Connection

Each custom type contributes to relevant universal attribute.

---

### 7. Character-Initiated Interactions

**Design Principle:** Characters don't just respond—they **initiate**.

**Types of Initiations:**

**1. Check-Ins (Emotional Support):**

```
[Notification: Eliza wants to talk]

Eliza: "Hey Jack, I noticed you've been pushing
hard for 10 days straight. How are you holding up?

Sometimes the best productivity move is rest.
Want to talk about it, or just acknowledge you're
doing great?"
```

**2. New Goal Suggestions (Exploration):**

```
[Notification: Lyra has an idea]

Lyra: "Jack, I know you're focused on coding,
but have you ever thought about design?

I have a friend who's teaching UI/UX. Want me
to introduce you? Could complement your skills."

[Yes, I'm curious] [Not right now]
```

**3. Quest Offers (Narrative Progression):**

```
[Notification: Commander Thorne seeks you]

Thorne: "Jack. The Arena needs someone with your
consistency. There's a challenge—7 people have
tried, all failed.

I think you can do it. Interested?"

[Tell me more] [What's the challenge?]
```

**4. World Events (Emergent Story):**

```
[System notification: Something has changed]

The city feels different today. Rumors spread
of an opportunity—a tech conference where major
companies are hiring on the spot.

Eliza: "This could be your moment. But you'd
need to prepare fast. 48 hours. Can you do it?"

[Accept Challenge] [Let this one pass]
```

**Frequency:** 1-2 character-initiated interactions per week to maintain surprise without overwhelming.

---

## User Flows

### Flow 1: Enhanced Onboarding - Deep Narrative Hook

**Goal:** Immerse user in story from first moment, gather context, complete first mission

**Duration:** 15-20 minutes (expanded for narrative depth)

---

**Step 1: Theme Selection**

```
┌──────────────────────────────────────────────┐
│ DELIGHT                                      │
│ A story for ambitious people who want to     │
│ transform their lives.                       │
│                                              │
│ [Begin]                                      │
└──────────────────────────────────────────────┘
```

**Step 2: Scenario Selection (Rich Descriptions)**

```
┌──────────────────────────────────────────────┐
│ WHERE DOES YOUR STORY BEGIN?                 │
├──────────────────────────────────────────────┤
│                                              │
│ 🌍 MODERN REALITY                           │
│ San Francisco • New York • Tokyo             │
│                                              │
│ You're building a career in the most        │
│ competitive cities on Earth. Every coffee    │
│ shop hides a founder. Every subway ride, a   │
│ potential connection. Will you make it?      │
│                                              │
│ [Choose Modern Reality]                      │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ 🏰 MEDIEVAL FANTASY                         │
│ The Kingdom of Aethermoor                    │
│                                              │
│ A realm rebuilding after war. Guilds seek   │
│ worthy members. The King's trials await.     │
│ Legends speak of those who arrived with      │
│ nothing and became heroes. Are you one?      │
│                                              │
│ [Choose Medieval Fantasy]                    │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ 🚀 STAR TREK 2000s                          │
│ Starfleet Academy, 2247                      │
│                                              │
│ Humanity reaches for the stars. The Academy  │
│ takes only the best. But you made it. Now    │
│ prove you belong among explorers and         │
│ visionaries. The unknown awaits.             │
│                                              │
│ [Choose Star Trek 2000s]                     │
│                                              │
│ [See more scenarios...]                      │
└──────────────────────────────────────────────┘
```

**Step 3: Deep Context Gathering**

```
User selects: Medieval Fantasy

┌──────────────────────────────────────────────┐
│ [Fade transition. Medieval ambient music.]   │
│                                              │
│ A figure emerges from the mist. She carries  │
│ a staff and moves with quiet confidence.     │
│                                              │
│ "Welcome, traveler. I am Eliza, keeper of   │
│ paths and witness to many journeys.          │
│                                              │
│ Before we enter Aethermoor, I must know:     │
│ What brings you to this realm?"              │
│                                              │
│ [Tell her your situation...]                 │
└──────────────────────────────────────────────┘
```

**Step 4: AI Elicitation (More Depth)**

```
User types: "I want to become a software developer
but I'm broke and inconsistent"

┌──────────────────────────────────────────────┐
│ Eliza nods slowly.                           │
│                                              │
│ "Ah. A builder. The Artisan's Guild will    │
│ welcome you—if you can prove yourself.       │
│                                              │
│ Broke means you start with nothing. That's   │
│ the hardest path. But also the most honest.  │
│                                              │
│ Tell me: What have you already tried?        │
│ What worked? What failed?"                   │
│                                              │
│ [Continue conversation...]                   │
└──────────────────────────────────────────────┘

[AI asks 2-3 more questions to gather:]
- Current skill level
- Past attempts at goals
- Emotional state
- What motivates them
- What scares them
```

**Step 5: Story Generation & Introduction (Expanded Narrative)**

```
┌──────────────────────────────────────────────┐
│ THE ROAD TO AETHERMOOR                       │
├──────────────────────────────────────────────┤
│                                              │
│ You and Eliza walk for what feels like days.│
│ She tells you of Aethermoor—once the grandest│
│ city in the realm, now rebuilding after the  │
│ Betrayal, a war that shattered the Kingdom   │
│ twenty years past.                           │
│                                              │
│ "The Artisan's Guild used to be a thousand  │
│ strong," she says. "Now? Maybe fifty remain. │
│ But they're the best. Lyra leads them—she    │
│ builds things that change lives."            │
│                                              │
│ You crest a hill. There, in the valley:      │
│ Aethermoor. Stone walls. Smoke rising from   │
│ forges. The sound of hammers on anvils.      │
│                                              │
│ Eliza stops. "You arrive with no coin. No    │
│ reputation. Just skill you're still learning.│
│                                              │
│ Most who come here fail. They give up when   │
│ the work gets hard. When no one believes in  │
│ them yet.                                    │
│                                              │
│ But here's what I know: Every master in that │
│ city started exactly where you stand."       │
│                                              │
│ She looks at you.                            │
│                                              │
│ "Will you enter?"                            │
│                                              │
│ [Enter Aethermoor]                           │
└──────────────────────────────────────────────┘
```

**Step 6: World State Introduction (Morning)**

```
TIME: 9:37 AM, First Day of Spring

┌──────────────────────────────────────────────┐
│ AETHERMOOR - THE ARTISAN'S QUARTER           │
├──────────────────────────────────────────────┤
│                                              │
│ Morning in the city. Workshops are opening.  │
│ Builders carry materials. The smell of fresh │
│ bread drifts from the bakery.                │
│                                              │
│ Most doors remain closed to you—locked       │
│ guildhalls, private forges. You're nobody    │
│ here. Yet.                                   │
│                                              │
│ YOUR STATUS:                                 │
│ 💰 Essence: 0                                │
│ 🏠 Shelter: The Streets (temporary)          │
│ 🍞 Food: 3 days remaining                    │
│ ⚔️ Reputation: Unknown                       │
│                                              │
│ ATTRIBUTES:                                  │
│ 🌱 Growth: Level 1                           │
│ 💪 Health: Level 1                           │
│ 🎨 Craft: Level 1                            │
│ 🤝 Connection: Level 0 (Locked)              │
│                                              │
│ Eliza: "You need Essence to survive. Let me  │
│ introduce you to someone who can help."      │
│                                              │
│ [Continue]                                   │
└──────────────────────────────────────────────┘
```

**Step 7-12:** [Similar to previous Flow 1, but with richer narrative paragraphs at each step]

---

### Flow 2: Daily Session with Dynamic Quests

**Time-Aware Opening:**

```
MORNING SESSION (8:23 AM)

┌──────────────────────────────────────────────┐
│ GOOD MORNING, JACK                           │
├──────────────────────────────────────────────┤
│ Day 5 in Aethermoor                          │
│                                              │
│ The city wakes. Guild halls open. Commander  │
│ Thorne begins morning drills in the Arena.   │
│ The Observatory library welcomes early       │
│ learners.                                    │
│                                              │
│ Eliza: "Morning, Jack. You're up early—that's│
│ when you do your best work.                  │
│                                              │
│ Today's missions are ready. But first:       │
│ How are you feeling?"                        │
│                                              │
│ [Ready to work] [Bit tired] [Stressed]       │
│ [Just show me priorities]                    │
└──────────────────────────────────────────────┘
```

**Dynamic Quest Generation:**

```
User selects: "Ready to work"

┌──────────────────────────────────────────────┐
│ PRIORITY MISSIONS                            │
├──────────────────────────────────────────────┤
│                                              │
│ [🔥 Time-Sensitive]                          │
│ 1. Morning Arena Session with Thorne         │
│    ⏱️ 20 min • 15 Essence • Health          │
│    "Closes at 10am. Thorne expects you."     │
│                                              │
│ [⭐ Story Quest - New!]                      │
│ 2. Lyra's Urgent Request                     │
│    ⏱️ 45 min • 40 Essence • Craft           │
│    "She says it's important. Won't say why." │
│    [Character-initiated]                     │
│                                              │
│ [📖 Growth]                                  │
│ 3. Continue Reading: "The Builder's Path"    │
│    ⏱️ 30 min • 20 Essence • Growth          │
│    Chapter 4 awaits in the Observatory       │
│                                              │
│ [🎯 Custom - Your Goal]                      │
│ 4. Work on Portfolio Project                 │
│    ⏱️ Flexible • 30 Essence • Craft         │
│    "Your main quest. Always available."      │
│                                              │
│ [💭 Suggestion from Eliza]                   │
│ 5. "Have you thought about networking?"      │
│    "The Commons opens at noon. Meet people   │
│    working on similar goals. Want me to      │
│    introduce you?"                           │
│    [Learn more] [Not yet]                    │
│                                              │
│ [Select Mission] [Review Full Progress]      │
└──────────────────────────────────────────────┘
```

---

### Flow 3: Full-Screen Mission with Evidence Capture

```
┌──────────────────────────────────────────────┐
│ MISSION: Lyra's Urgent Request               │
├──────────────────────────────────────────────┤
│ Time: 23 minutes / 45 estimated              │
│ [███████████████░░░░░░░░░] 51%              │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ MISSION BRIEF:                               │
│ Lyra needs a critical bug fixed in her       │
│ framework before tonight's Guild meeting.    │
│                                              │
│ YOUR WORK:                                   │
│ ┌────────────────────────────────────────┐  │
│ │ 📝 Notes:                              │  │
│ │ "Found the bug in the validation loop. │  │
│ │  Testing the fix now..."               │  │
│ │                                        │  │
│ │ [Add note]                             │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ 📸 EVIDENCE (Optional)                 │  │
│ │                                        │  │
│ │ Upload photo of your work, code,       │  │
│ │ or progress                            │  │
│ │                                        │  │
│ │ [📷 Take Photo] [🖼️ Upload Image]     │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ ACTIVE NUDGES:                               │
│ 🔔 Reminder: Lyra checks in 20 minutes       │
│ 🗨️ Commander Thorne: "New quest when done"  │
│                                              │
│ ─────────────────────────────────────────    │
│                                              │
│ [Eliza - Minimized Corner]                   │
│ 💬 "You're in the zone. Keep going."         │
│                                              │
│ [I'm Done] [Need Help] [Take 5-Min Break]    │
└──────────────────────────────────────────────┘
```

---

### Flow 4: Character-Initiated "Try Something New"

```
┌──────────────────────────────────────────────┐
│ [Notification: Archmage Elara seeks you]    │
├──────────────────────────────────────────────┤
│                                              │
│ OBSERVATORY - Late Evening                   │
│                                              │
│ You find Elara in her study, surrounded by   │
│ ancient texts and glowing crystals.          │
│                                              │
│ Elara: "Jack. You've been focused on Craft   │
│ for two weeks—admirably so. Your skill grows.│
│                                              │
│ But I wonder: Have you considered learning   │
│ the art of teaching?                         │
│                                              │
│ The Guild needs mentors. Beginners arrive    │
│ daily, lost and overwhelmed. You were there  │
│ once. You could guide them.                  │
│                                              │
│ Teaching deepens your own understanding.     │
│ And it unlocks the Connection attribute—     │
│ you'd meet others on similar paths."         │
│                                              │
│ NEW OPPORTUNITY:                             │
│ 🎓 Become a Mentor                           │
│ • Unlocks: Connection attribute              │
│ • Weekly quest: Guide 1 new arrival          │
│ • Rewards: Essence + Reputation + Growth XP  │
│ • Requirement: Craft Level 5+ (You: Level 7) │
│                                              │
│ "What do you say? Will you try?"             │
│                                              │
│ [Yes, I'll try mentoring]                    │
│ [Tell me more first]                         │
│ [Not ready yet]                              │
└──────────────────────────────────────────────┘
```

---

### Flow 5: Evening Time Shift (World Closes Down)

```
TIME: 9:15 PM

┌──────────────────────────────────────────────┐
│ AETHERMOOR - EVENING QUIET                   │
├──────────────────────────────────────────────┤
│                                              │
│ The city winds down. Most workshops have     │
│ closed. The Arena is dark—Thorne went home   │
│ an hour ago.                                 │
│                                              │
│ Only the Observatory remains lit, Elara's    │
│ silhouette visible in the high tower.        │
│                                              │
│ The Commons has a few late-night regulars,   │
│ sharing stories over ale.                    │
│                                              │
│ Eliza: "Long day, Jack. You've been at it    │
│ since morning.                               │
│                                              │
│ Want to wrap up with one reflective mission, │
│ or call it a night?"                         │
│                                              │
│ EVENING MISSIONS AVAILABLE:                  │
│                                              │
│ 🔭 Evening Reflection with Elara             │
│    Review your day, plan tomorrow            │
│    15 min • 10 Essence • Growth              │
│                                              │
│ 🏘️ Late Night Conversation in Commons       │
│    Connect with fellow night owls            │
│    20 min • 10 Essence • Connection          │
│                                              │
│ 📖 Read Before Bed                           │
│    Calm wind-down activity                   │
│    30 min • 15 Essence • Growth              │
│                                              │
│ 😴 Rest (Recommended)                        │
│    "You've earned 45 Essence today. Sleep    │
│    well. The world will be here tomorrow."   │
│                                              │
│ [Choose Mission] [Call It a Night]           │
└──────────────────────────────────────────────┘
```

---

## Interaction Patterns

### Pattern 1: Evidence Capture & Proof of Work

**Purpose:** Make work tangible, celebrate concrete accomplishments

**Interaction:**

1. During mission, user can upload photo/screenshot of work
2. System stores image with mission
3. Used in highlight reels and progress reviews
4. Builds portfolio of visual accomplishments

**Example:**

```
User uploads photo of code they just wrote.

Eliza: "Excellent work. I'll remember this. When
you doubt yourself later, I'll show you what you
built today."

[Photo saved to Portfolio]
```

---

### Pattern 2: Flexible Time Override

**Purpose:** Respect user's unique schedules

**Interaction:**

```
User clicks: "Why is the Arena closed?"

┌──────────────────────────────────────────────┐
│ TIME SETTINGS                                │
├──────────────────────────────────────────────┤
│                                              │
│ The Arena closes at 9pm by default.          │
│                                              │
│ But your schedule is unique. Want to adjust? │
│                                              │
│ ○ Keep world time (default)                 │
│ ● My productive hours: [Custom]              │
│   Morning: 10pm - 2am                        │
│   Afternoon: 2am - 8am                       │
│   Evening: 8am - 2pm                         │
│   Night: 2pm - 10pm                          │
│                                              │
│ ☑ Keep all zones open 24/7                  │
│                                              │
│ [Save Settings]                              │
└──────────────────────────────────────────────┘
```

---

### Pattern 3: Story Callbacks & Continuity

**Purpose:** Make user feel story is authored specifically for them

**Example:**

```
Week 1: User mentions in onboarding they're afraid
of public speaking.

Week 3: Lyra approaches:

"Jack, remember when you told Eliza you're nervous
about public speaking?

The Guild is hosting a Demo Day. I think you should
present your project. Yes, it's scary. But you've
grown. I believe in you.

Will you try?"
```

---

### Pattern 4: AI Pre-Planned Surprises

**Purpose:** Create genuine discovery, avoid predictability

**Mechanic:**

- AI generates 3-5 "hidden quests" at story start
- These unlock based on specific trigger conditions
- User has no visibility until triggered
- Creates "I didn't see that coming!" moments

**Example Hidden Quest:**

```
TRIGGER: User completes 20 Craft missions without
missing a day

REVEAL:
┌──────────────────────────────────────────────┐
│ ACHIEVEMENT UNLOCKED: The Relentless          │
├──────────────────────────────────────────────┤
│                                              │
│ 20 days. 20 missions. No breaks.             │
│                                              │
│ Lyra appears: "Jack. I've been watching.     │
│ Your consistency is... rare.                 │
│                                              │
│ The Guild needs to know about you. Come."    │
│                                              │
│ [She leads you to the Grand Hall]           │
│                                              │
│ The entire Guild is assembled.               │
│                                              │
│ Lyra: "This one has earned recognition."     │
│                                              │
│ REWARD:                                      │
│ 🏆 Title: "The Relentless"                   │
│ 🎁 500 Essence                                │
│ 🔓 Access: Grand Hall (elite zone)           │
│ 💜 All Guild relationships +2 levels          │
│                                              │
│ [Accept Honor]                               │
└──────────────────────────────────────────────┘
```

---

## Responsive Behavior

### Desktop (1280px+)

- Three-column layout: Companion | World/Missions | Progress
- Full narrative paragraphs
- All zones visible simultaneously
- Rich hover states and animations

### Tablet (768px - 1279px)

- Two-column: Main content | Sidebar (collapsible)
- Narrative slightly condensed
- Tab navigation between zones
- Touch-optimized interactions

### Mobile (< 768px)

- Single column, full-screen views
- Bottom navigation: Companion | World | Progress | Profile
- Swipe gestures for quick actions
- Condensed story text with "Read More" expansion
- Mission interface adapts to portrait mode

---

## Technical Considerations

### AI Story Generation

- Use LLM (GPT-4 or similar) to generate personalized narratives
- Pre-generate 3-5 story beats ahead to maintain consistency
- Store narrative state in database (chapter, character relationships, hidden quests)
- Template system for scenarios with variable insertion

### Time-Based State Management

- Server tracks real-world time zones
- Database stores "world time rules" per user
- Frontend polls every 15 minutes for time-state changes
- Override settings stored in user preferences

### Evidence Storage

- Images stored in S3 or equivalent
- Thumbnail generation for gallery views
- Metadata: mission_id, timestamp, user_notes
- Privacy: User-only access unless explicitly shared

### Character AI

- Each character has personality prompt
- Conversation history stored per character
- Relationship levels trigger different dialogue trees
- Character-initiated events scheduled based on user activity patterns

---

## Implementation Roadmap

### Phase 1: MVP Core (Weeks 1-4)

- [] Onboarding flow with theme selection
- [] Eliza companion interface
- [] Basic mission system (create, start, complete)
- [] Essence economy
- [] Universal attributes (Growth, Health, Craft, Connection)
- [] Progress dashboard
- [] One scenario (Modern Reality or Medieval Fantasy)

### Phase 2: Rich Narrative (Weeks 5-8)

- [ ] AI story generation integration
- [ ] Deep narrative paragraphs
- [ ] Character relationships system
- [ ] Hidden quests and pre-planned surprises
- [ ] Time-based world dynamics
- [ ] Character-initiated interactions

### Phase 3: Evidence & Social (Weeks 9-12)

- [ ] Photo/evidence upload
- [ ] Highlight reel generation
- [ ] Weekly progress reviews
- [ ] Chapter transitions
- [ ] Mentorship system (help new users)
- [ ] Basic multiplayer (Commons zone)

### Phase 4: Expansion (Weeks 13+)

- [ ] Additional scenarios (Cyberpunk, Sci-Fi, Zombie, etc.)
- [ ] Advanced customization
- [ ] Voice input for missions
- [ ] Mobile app optimization
- [ ] Community features (shared quests)

---

## Validation & Success Criteria

### UX Validation

- **Onboarding completion:** ≥80% of users complete first mission
- **Emotional resonance:** ≥75% of users rate narrative as "compelling" or "very compelling"
- **Daily return rate:** ≥60% of Week 1 users return on Day 8
- **Mission completion:** ≥70% of started missions completed
- **Character attachment:** ≥50% of users name a favorite companion by Week 2

### Design Quality

- **Accessibility:** WCAG AA compliance minimum
- **Performance:** <2s initial load, <500ms interaction response
- **Mobile optimization:** Feature parity between desktop and mobile
- **Visual polish:** Consistent design system across all views

---

## Appendix: Design Assets Needed

### Illustrations

- Character portraits (Eliza, Lyra, Thorne, Elara, etc.)
- Theme-specific backgrounds (SF, medieval, cyberpunk, etc.)
- Zone illustrations (Arena, Observatory, Commons)
- Mission icons (Growth, Health, Craft, Connection)

### Animations

- Character breathing/idle animations
- Progress bar fills
- Celebration effects (mission complete, level up)
- Transition effects (day to night, zone to zone)

### Sound Design (Optional/Future)

- Ambient music per theme
- UI interaction sounds
- Mission complete chimes
- Character voice lines (text-to-speech or recorded)

---

**END OF UX DESIGN SPECIFICATION**

**Document Status:** Complete and ready for development handoff  
**Next Steps:** Review with development team, create implementation tickets, begin Phase 1 build

---

**Credits:**

- **UX Design:** Sally (UX Designer Agent)
- **Product Vision:** Jack
- **Design Collaboration:** Jack + Sally
- **Framework:** BMAD Method (BMM Module)
- **Date:** November 9, 2025

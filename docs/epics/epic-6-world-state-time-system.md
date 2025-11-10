# Epic 6: World State & Time System

**Epic Goal:** Create dynamic world zones (Arena, Observatory, Commons) with time-aware availability and presence, building the foundation for future multiplayer features.

**Architecture Components:** World service, Redis cache, WebSocket for real-time updates, time rules engine

### Story 6.1: Implement Time-Aware State Engine

As a **developer**,  
I want **a time-based rules engine for world state**,  
So that **zone availability and events can change based on user's time and productive hours**.

**Acceptance Criteria:**

**Given** the system is set up  
**When** I query world state for a user  
**Then** the engine applies time rules:

- Default rules: Arena closes 9pm-6am (user's local time)
- User overrides: Custom productive hours from onboarding
- Timezone-aware: All times in user's timezone

**And** the engine caches state in Redis:

- Cache key: `world_state:{user_id}`
- TTL: 15 minutes
- Includes: zone availability, character presence, time-based events

**And** the state updates automatically:

- ARQ worker runs every 15 minutes
- Checks all active users' time rules
- Updates Redis cache

**Prerequisites:** Story 1.4 (user preferences with timezone)

**Technical Notes:**

- Service: `backend/app/services/world_service.py`
- Use `pytz` for timezone handling
- Schema: add `time_rules JSONB` to `user_preferences` table
- Worker: `backend/app/workers/world_state_updater.py`
- See Architecture Pattern 3 for time-aware world state design

---

### Story 6.2: Create World Zones (Arena, Observatory, Commons) - MVP

As a **user**,  
I want **to explore different themed zones for different types of work**,  
So that **my environment matches my current goal focus**.

**Acceptance Criteria:**

**Given** I'm logged in  
**When** I navigate the world  
**Then** I can access three zones:

- **Arena**: Health & craft missions, energizing atmosphere
- **Observatory**: Growth & learning missions, contemplative atmosphere
- **Commons**: Connection & reflection, collaborative atmosphere

**And** each zone shows:

- Zone name and description
- Available missions filtered by value category
- Characters present in the zone
- Atmospheric details (color scheme, ambient sounds optional)

**And** zone availability respects time rules:

- Grayed out if unavailable due to time
- Shows "Opens at [time]" message

**Prerequisites:** Story 6.1 (time engine), Story 3.3 (missions)

**Technical Notes:**

- Frontend routes: `/world/arena`, `/world/observatory`, `/world/commons`
- Component: `ZoneLayout.tsx` with zone-specific theming
- API: `GET /api/v1/world/zones` returns available zones with state
- Schema: `zones` table (id, name, description, value_categories ARRAY, default_availability JSONB)
- Use Tailwind theme variants for zone color schemes

---

### Story 6.3: Add WebSocket for Real-Time World Updates (MVP)

As a **user**,  
I want **real-time updates when world state changes**,  
So that **I see zone availability and events without refreshing**.

**Acceptance Criteria:**

**Given** I'm in a world zone  
**When** world state changes (zone opens/closes, character appears, event starts)  
**Then** I receive a WebSocket message

**And** the UI updates automatically:

- Zone becomes available/unavailable
- Character presence indicator updates
- Event notifications appear

**And** the connection is resilient:

- Auto-reconnects on disconnect
- Fallback to polling if WebSocket fails
- No data loss during reconnection

**Prerequisites:** Story 6.2 (world zones)

**Technical Notes:**

- Backend: FastAPI WebSocket endpoint `/ws/world`
- Frontend: WebSocket client in `lib/websocket.ts`
- Message format: `{"type": "zone_update", "zone_id": "arena", "state": {...}}`
- Use Heartbeat/ping-pong to detect disconnects
- Fallback: poll `/api/v1/world/zones` every 60s if WebSocket unavailable

---

### Story 6.4: Implement Zone Unlocking System (Future)

As a **user**,  
I want **zones to unlock as I progress**,  
So that **the world expands as my journey deepens**.

**Acceptance Criteria:**

**Given** I'm a new user  
**When** I start my journey  
**Then** only one zone is initially available (Commons)

**And** zones unlock through progression:

- **Arena**: Unlock after completing 5 missions
- **Observatory**: Unlock after 7-day streak or narrative Chapter 2
- **Future zones**: Based on story chapters, achievements, or Essence spending

**And** unlock moments are celebrated:

- Cinematic reveal animation
- Character introduction (Lyra in Arena, Elara in Observatory)
- Guided tour of new zone

**Prerequisites:** Story 6.2 (zones), Story 4.3 (narrative progression)

**Technical Notes:**

- Schema: `user_zones` table (user_id FK, zone_id FK, unlocked_at TIMESTAMP, intro_completed BOOLEAN)
- Unlock triggers defined in `zones` table `unlock_criteria JSONB`
- Worker checks criteria when user completes missions/achievements
- Frontend: unlock animation component with Framer Motion

---

### Story 6.5: Add Multiplayer Zone Features (Future)

As a **user**,  
I want **to see other users in shared zones**,  
So that **I feel part of a community working together**.

**Acceptance Criteria:**

**Given** multiplayer is enabled  
**When** I enter a zone  
**Then** I see:

- Other users' avatars/names (anonymized or real based on settings)
- Real-time presence (who's currently in the zone)
- Activity indicators (user just completed a mission)

**And** I can interact:

- Send encouragement emoji
- View others' public progress (opt-in)
- Join shared rituals (future: group meditation, co-working sessions)

**And** zones have capacity limits:

- Max users per instance (e.g., 50 per Commons)
- Multiple instances if over capacity
- Pod members prioritized in same instance

**Prerequisites:** Story 6.2 (zones), Future authentication/multiplayer infrastructure

**Technical Notes:**

- Requires user presence tracking via WebSocket
- Schema: `zone_presence` table (user_id FK, zone_id FK, joined_at, last_activity)
- WebSocket broadcasts presence changes to all users in zone
- Privacy: users can appear "anonymous" or "private"
- Consider scalability: sharding zones by region/instance

---

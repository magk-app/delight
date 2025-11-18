# Epic 7: Nudge & Outreach

**Epic Goal:** Implement compassionate nudges (in-app, SMS, email) that gently bring users back when they drift away, without feeling naggy or transactional.

**Architecture Components:** ARQ workers, notification service, Twilio (SMS), SendGrid (email), nudge intelligence

### Story 7.1: Set Up Notification Infrastructure

As a **developer**,  
I want **multi-channel notification infrastructure**,  
So that **we can send in-app, SMS, and email nudges reliably**.

**Acceptance Criteria:**

**Given** the notification system is configured  
**When** I send a notification  
**Then** I can target multiple channels:

- In-app (stored in database, shown in UI)
- Email (via SendGrid or similar)
- SMS (via Twilio or similar)
- Push (future: mobile app)

**And** the system handles:

- User opt-in/opt-out preferences per channel
- Rate limiting (max notifications per day/week)
- Delivery tracking (sent, delivered, opened, clicked)
- Failure handling and retries

**And** environment configuration:

- Dev: all notifications logged, not sent
- Staging: sent to test numbers/emails only
- Production: sent to real users respecting preferences

**Prerequisites:** Story 1.4 (user communication preferences)

**Technical Notes:**

- Service: `backend/app/services/notification_service.py`
- Schema: `notifications` table (user_id FK, channel ENUM, content JSONB, sent_at, delivered_at, opened_at, status)
- Integrations: Twilio SDK, SendGrid SDK
- Rate limiting: Redis-based (max 3 nudges/day default)
- Environment vars: TWILIO_API_KEY, SENDGRID_API_KEY

---

### Story 7.2: Implement Drop-Off Detection and Smart Nudge Scheduling

As a **user**,  
I want **to receive gentle reminders when I've been away**,  
So that **I'm encouraged to return without feeling pressured**.

**Acceptance Criteria:**

**Given** I've been inactive  
**When** the nudge scheduler detects my absence  
**Then** nudges are sent at strategic intervals:

- Day 2: In-app reminder only
- Day 4: Email with encouragement from Eliza
- Day 7: SMS (if opted in) with personalized message

**And** nudge content is compassionate:

- "We noticed you've been away—how are you doing?"
- "Your 14-day streak is waiting for you"
- "Eliza has been thinking about your [goal name] goal"
- NOT: "You haven't completed any missions!" (shame-free)

**And** nudges adapt to user patterns:

- Sent at optimal engagement times (based on past activity)
- Respect quiet hours (user preferences)
- Stop after 3 nudges if no response

**And** when I return:

- Welcomed back warmly
- Offered "ease back in" mission (shorter, easier)

**Prerequisites:** Story 7.1 (notification infrastructure), Story 3.4 (mission activity data)

**Technical Notes:**

- Worker: `backend/app/workers/nudge_scheduler.py` (runs daily)
- Drop-off detection: user has no activity for 48+ hours
- Nudge templates stored in `nudge_templates` table
- Uses Eliza agent to personalize message content
- Track nudge effectiveness (response rate) for optimization

---

### Story 7.3: Build In-App Notification Center (MVP)

As a **user**,  
I want **an in-app notification center**,  
So that **I can see all messages from Eliza and the system**.

**Acceptance Criteria:**

**Given** I'm using the app  
**When** I open the notification center  
**Then** I see:

- Unread notifications (badge count in header)
- All past notifications (scrollable list)
- Notification types: nudges, achievements, character messages, story updates

**And** I can:

- Mark as read
- Dismiss notifications
- Take action (e.g., "Start mission" button in notification)

**And** notifications appear in real-time:

- Toast/banner for high-priority notifications
- Badge count updates automatically

**Prerequisites:** Story 7.1 (notification infrastructure)

**Technical Notes:**

- Component: `NotificationCenter.tsx` with dropdown/modal
- API: `GET /api/v1/notifications` with pagination
- WebSocket: real-time notification delivery
- Schema: `is_read BOOLEAN`, `dismissed_at TIMESTAMP` in `notifications` table
- Use shadcn/ui Toast component for banners

---

### Story 7.4: Implement Opt-In/Opt-Out Management UI

As a **user**,  
I want **fine-grained control over which notifications I receive**,  
So that **I'm not overwhelmed and can set boundaries**.

**Acceptance Criteria:**

**Given** I'm in settings  
**When** I manage notification preferences  
**Then** I can toggle:

- In-app notifications (always on, can't disable)
- Email nudges (opt-in)
- SMS nudges (opt-in, requires phone number)
- Character-initiated messages (opt-in)
- Achievement celebrations (opt-in)

**And** I can set:

- Quiet hours (no notifications during these times)
- Maximum nudges per day/week
- Preferred contact method priority

**And** changes take effect immediately

**Prerequisites:** Story 7.1 (notification infrastructure)

**Technical Notes:**

- Frontend: `frontend/src/app/settings/notifications/page.tsx`
- API: `PATCH /api/v1/users/preferences` updates communication preferences
- Store in `user_preferences.communication_preferences JSONB`
- Worker respects preferences when scheduling nudges

---

### Story 7.5: Add AI-Driven Optimal Timing Intelligence (Future)

As a **user**,  
I want **nudges to arrive at times when I'm most likely to respond**,  
So that **they're helpful rather than disruptive**.

**Acceptance Criteria:**

**Given** the system has 30+ days of my data  
**When** scheduling a nudge  
**Then** the AI predicts optimal send time:

- Analyzes my response patterns (when I've acted on past nudges)
- Considers my mission completion times
- Respects circadian rhythms and work patterns

**And** the system learns over time:

- Tracks nudge open rates and response rates by time
- Adjusts future timing based on effectiveness
- A/B tests different timing strategies

**And** I can override:

- Set preferred nudge time manually
- System uses manual preference or AI prediction (whichever is set)

**Prerequisites:** Story 7.2 (nudge scheduler), Story 5.2 (analytics data)

**Technical Notes:**

- ML model: simple time-series prediction or LLM-based reasoning
- Store optimal times in `user_insights` table
- Worker queries insights before scheduling nudges
- Track experiment data for continuous improvement

---

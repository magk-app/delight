---
title: API Contracts
description: REST API endpoints and data contracts
---

# API Contracts

## Base URL

```
Development: http://localhost:8000
Production: https://api.delight.so
```

All endpoints are prefixed with `/api/v1/`.

## Authentication

All API requests (except health check) require authentication via Clerk session token:

```http
Authorization: Bearer <clerk_session_token>
```

## Companion Chat

### Send Message

**POST** `/api/v1/companion/chat`

Send a message to the AI companion and receive a streaming response.

**Request:**
```json
{
  "message": "How are you today?",
  "context": {
    "current_mission_id": 123,
    "emotional_state": "stressed"
  }
}
```

**Response (SSE Stream):**
```
data: {"type": "token", "content": "I"}
data: {"type": "token", "content": " 'm"}
data: {"type": "token", "content": " here"}
data: {"type": "token", "content": " for"}
data: {"type": "token", "content": " you"}
data: {"type": "complete", "message_id": "abc123"}
```

**SSE Event Types:**
- `token`: Individual token from LLM
- `complete`: Message generation complete
- `error`: Error during generation

---

## Missions

### List Missions

**GET** `/api/v1/missions`

Query parameters:
- `status`: Filter by status (`active`, `completed`, `pending`)
- `attribute_type`: Filter by attribute (`Growth`, `Health`, `Craft`, `Connection`)
- `limit`: Max results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "missions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Morning Arena Session",
      "description": "Complete 20 minutes of focused work",
      "duration_minutes": 20,
      "essence_reward": 15,
      "attribute_type": "Health",
      "status": "active",
      "created_at": "2025-11-09T08:00:00Z",
      "started_at": "2025-11-09T09:00:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

### Create Mission

**POST** `/api/v1/missions`

**Request:**
```json
{
  "title": "Write documentation",
  "description": "Migrate docs to Mintlify",
  "duration_minutes": 30,
  "attribute_type": "Craft"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write documentation",
  "status": "pending",
  "essence_reward": 20,
  "created_at": "2025-11-09T10:30:00Z"
}
```

### Start Mission

**POST** `/api/v1/missions/{id}/start`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "started_at": "2025-11-09T10:35:00Z"
}
```

### Complete Mission

**POST** `/api/v1/missions/{id}/complete`

**Request:**
```json
{
  "notes": "Successfully migrated all architecture docs",
  "evidence_url": "https://s3.amazonaws.com/..."
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "completed_at": "2025-11-09T11:05:00Z",
  "essence_earned": 20,
  "streak_bonus": 5
}
```

---

## World State

### Get Current World State

**GET** `/api/v1/world/state`

**Response:**
```json
{
  "current_time": "2025-11-09T14:30:00Z",
  "user_local_time": "09:30:00",
  "zones": {
    "arena": {
      "available": true,
      "closes_at": "21:00",
      "description": "Focus on your current mission"
    },
    "observatory": {
      "available": true,
      "description": "Review your progress and plan ahead"
    },
    "commons": {
      "available": false,
      "opens_at": "12:00",
      "description": "Connect with your companions"
    }
  },
  "characters_present": ["Eliza", "Lyra"],
  "active_quests": 2
}
```

### WebSocket Connection (World Updates)

**WS** `/api/v1/ws/world`

Server pushes updates when world state changes:

```json
{
  "type": "zone_update",
  "zone": "commons",
  "available": true,
  "timestamp": "2025-11-09T12:00:00Z"
}
```

```json
{
  "type": "character_arrival",
  "character": "Thorne",
  "zone": "arena",
  "timestamp": "2025-11-09T14:35:00Z"
}
```

---

## Progress & Analytics

### Get Daily Progress

**GET** `/api/v1/progress/daily`

Query parameters:
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response:**
```json
{
  "progress": [
    {
      "date": "2025-11-09",
      "dci_score": 0.75,
      "missions_completed": 5,
      "streak_days": 12,
      "essence_earned": 125
    }
  ]
}
```

### Get DCI (Daily Capacity Index)

**GET** `/api/v1/progress/dci`

**Response:**
```json
{
  "current_dci": 0.75,
  "factors": {
    "sleep_quality": 0.8,
    "stress_level": 0.6,
    "recent_completions": 0.9
  },
  "recommended_mission_duration": 20,
  "confidence": 0.85
}
```

---

## User Profile

### Get User Profile

**GET** `/api/v1/users/me`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "clerk_user_id": "user_2abc123def456",
  "email": "user@example.com",
  "display_name": "Alice",
  "timezone": "America/New_York",
  "theme_preference": "dark",
  "created_at": "2025-10-01T00:00:00Z"
}
```

### Update User Profile

**PATCH** `/api/v1/users/me`

**Request:**
```json
{
  "display_name": "Alice Wonder",
  "timezone": "America/Los_Angeles",
  "theme_preference": "light"
}
```

---

## Health Check

### Health Check (Unauthenticated)

**GET** `/api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T14:30:00Z",
  "database": "connected",
  "redis": "connected"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Mission not found",
  "error_code": "MISSION_NOT_FOUND",
  "timestamp": "2025-11-09T14:30:00Z"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (missing/invalid auth token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error

---

## Rate Limiting

- **Default:** 100 requests/minute per user
- **Companion chat:** 20 requests/minute (to prevent abuse)
- **Mission creation:** 50 requests/hour

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699564800
```

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

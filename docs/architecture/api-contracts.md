# API Contracts

### Companion Chat

**POST** `/api/v1/companion/chat`

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
data: {"type": "complete", "message_id": "abc123"}
```

### Missions

**GET** `/api/v1/missions?status=active`

```json
{
  "missions": [
    {
      "id": 123,
      "title": "Morning Arena Session",
      "duration_minutes": 20,
      "essence_reward": 15,
      "attribute_type": "Health",
      "status": "active"
    }
  ]
}
```

**POST** `/api/v1/missions/start`

```json
{
  "mission_id": 123
}
```

### World State

**GET** `/api/v1/world/state`

```json
{
  "current_time": "2025-11-09T14:30:00Z",
  "zones": {
    "arena": { "available": true, "closes_at": "21:00" },
    "observatory": { "available": true },
    "commons": { "available": false, "opens_at": "12:00" }
  },
  "characters_present": ["Eliza", "Lyra"]
}
```

---

# Data Architecture

### Core Models

**User:**

- `id`, `email`, `password_hash`, `timezone`, `theme_preference`, `created_at`

**Mission:**

- `id`, `user_id`, `title`, `description`, `duration_minutes`, `essence_reward`, `attribute_type` (Growth/Health/Craft/Connection), `status` (pending/active/completed), `created_at`, `completed_at`

**Character:**

- `id`, `name` (Eliza, Lyra, Thorne, Elara), `personality_prompt`, `attribute_focus`, `scenario` (medieval, sci-fi, etc.)

**Character Relationship:**

- `id`, `user_id`, `character_id`, `relationship_level` (0-10), `last_interaction_at`

**Narrative State:**

- `id`, `user_id`, `scenario`, `current_chapter`, `hidden_quests` (JSON), `story_progress` (JSON)

**Progress:**

- `id`, `user_id`, `date`, `dci_score`, `missions_completed`, `streak_days`, `essence_earned`

### Relationships

- User → Missions (1:N)
- User → Character Relationships (1:N)
- User → Narrative State (1:1)
- User → Progress (1:N, daily records)
- Mission → Evidence (1:N, optional photos/notes)

### Vector Storage (PostgreSQL pgvector)

**Tables with Vector Columns:**

- `personal_memories` - Personal context, emotional state (user_id, content, embedding vector(1536))
- `project_memories` - Goal-related memories (user_id, content, embedding vector(1536))
- `task_memories` - Mission-specific context (user_id, mission_id, content, embedding vector(1536))
- `character_conversations` - Per-character chat history (user_id, character_id, message, embedding vector(1536))

---

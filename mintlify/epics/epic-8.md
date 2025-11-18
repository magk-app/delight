# Epic 8: Evidence & Reflection

**Epic Goal:** Enable users to upload evidence of accomplishments (photos, artifacts) and reflect on their journey, building toward AI-validated achievements and shared galleries.

**Architecture Components:** S3-compatible storage, file upload service, evidence review system

### Story 8.1: Set Up S3 File Storage Infrastructure

As a **developer**,  
I want **reliable cloud storage for user-uploaded files**,  
So that **evidence uploads are scalable and cost-effective**.

**Acceptance Criteria:**

**Given** the file storage is configured  
**When** a file is uploaded  
**Then** it is stored in S3-compatible storage (AWS S3, MinIO, etc.)

**And** the system handles:

- Secure presigned URLs for uploads (no direct S3 access)
- File type validation (images: JPEG, PNG; PDFs for documents)
- Size limits (10MB per file for MVP)
- Virus scanning (optional for MVP, required for production)

**And** files are organized:

- Bucket: `delight-evidence`
- Structure: `{user_id}/{mission_id}/{filename}`
- Metadata stored in database

**Prerequisites:** Story 1.2 (database schema)

**Technical Notes:**

- Service: `backend/app/services/storage_service.py`
- Use `boto3` for S3 interaction
- Schema: `evidence_uploads` table (id, user_id FK, mission_id FK, s3_key, file_type, file_size, uploaded_at, visibility ENUM[private/public/pod])
- Environment: S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY
- Consider MinIO for local dev environment

---

### Story 8.2: Implement Evidence Upload Flow (MVP)

As a **user**,  
I want **to upload photos or documents as proof of my mission completion**,  
So that **I can build a tangible record of my accomplishments**.

**Acceptance Criteria:**

**Given** I'm completing or have completed a mission  
**When** I upload evidence  
**Then** I can:

- Select file from device (camera roll, file system)
- Preview before uploading
- Add optional caption/note

**And** the upload process:

- Shows progress bar
- Handles errors gracefully (retry, cancel)
- Confirms successful upload

**And** uploaded evidence:

- Links to the mission
- Appears in mission history
- Stored securely with privacy controls

**Prerequisites:** Story 8.1 (S3 storage), Story 3.4 (mission completion)

**Technical Notes:**

- API: `POST /api/v1/evidence/upload` returns presigned URL
- Frontend uploads directly to S3 via presigned URL
- After upload, frontend calls `POST /api/v1/evidence/confirm` to finalize
- Component: `EvidenceUploader.tsx` with drag-and-drop support
- Mobile: use file input with `accept="image/*"` for camera access

---

### Story 8.3: Create Evidence Gallery and Mission History

As a **user**,  
I want **to browse my evidence and see a visual history of my work**,  
So that **I can appreciate how far I've come**.

**Acceptance Criteria:**

**Given** I've uploaded evidence over time  
**When** I view my evidence gallery  
**Then** I see:

- Grid of thumbnails (photos/icons)
- Filter by: goal, time range, value category
- Sort by: date, mission, goal

**And** I can:

- Click thumbnail to view full-size with details
- Add/edit captions retroactively
- Delete evidence (marks as deleted, keeps in DB)
- Download originals

**And** the gallery integrates with mission timeline:

- Evidence appears on goal progress timelines
- Visual milestones (photo attached to key missions)

**Prerequisites:** Story 8.2 (evidence upload)

**Technical Notes:**

- Frontend: `frontend/src/app/evidence/page.tsx`
- API: `GET /api/v1/evidence?goal_id=&date_from=&date_to=` with pagination
- Generate thumbnails on upload (or on-demand)
- Use lazy loading for performance
- Component: `EvidenceGallery.tsx` with lightbox modal

---

### Story 8.4: Add Reflection Prompts Post-Mission (MVP)

As a **user**,  
I want **guided reflection prompts after completing missions**,  
So that **I internalize learnings and celebrate progress meaningfully**.

**Acceptance Criteria:**

**Given** I just completed a mission  
**When** the completion modal appears  
**Then** I'm offered optional reflection prompts:

- "What did you learn from this mission?"
- "How do you feel about completing this?"
- "What made this easier or harder than expected?"

**And** I can:

- Skip reflection (not required)
- Write free-form response
- Select from mood emojis
- Record voice note (future)

**And** reflections are stored:

- Linked to mission session
- Added to personal-tier memory
- Eliza can reference in future conversations

**Prerequisites:** Story 3.4 (mission completion), Story 2.2 (memory service)

**Technical Notes:**

- Schema: add `reflection TEXT` to `mission_sessions` table
- Frontend: reflection modal with textarea and emoji picker
- Reflection saved as personal memory: "Reflection on [mission]: [text]"
- Optional: use sentiment analysis to track emotional journey

---

### Story 8.5: Implement AI Validation of Evidence (Future)

As a **user**,  
I want **AI to recognize and validate my uploaded evidence**,  
So that **achievements feel verified and meaningful**.

**Acceptance Criteria:**

**Given** I upload evidence  
**When** AI analyzes the image/document  
**Then** it detects:

- Relevance to mission (e.g., photo of completed workout for health mission)
- Quality/authenticity indicators
- Specific accomplishments (e.g., "Ran 5km based on fitness tracker screenshot")

**And** validation results:

- Badge: "AI-Verified" on evidence
- Bonus rewards for verified evidence (extra Essence)
- Flags suspicious uploads (requires manual review)

**And** validation is optional:

- Users can skip AI review if preferred
- Doesn't block uploads or progress

**Prerequisites:** Story 8.2 (evidence upload)

**Technical Notes:**

- Use OpenAI Vision API or similar for image analysis
- Prompt: "Does this image show evidence of [mission goal]? Explain."
- Store validation results in `evidence_uploads.ai_validation JSONB`
- Handle false positives gracefully (don't punish users)

---

### Story 8.6: Create Shared Achievement Galleries (Future)

As a **user**,  
I want **to share selected evidence with my pod or publicly**,  
So that **I can inspire others and celebrate wins together**.

**Acceptance Criteria:**

**Given** I have evidence I'm proud of  
**When** I mark it as shareable  
**Then** it appears in:

- Pod gallery (if I'm in an accountability pod)
- Public gallery (opt-in, moderated)
- Social media preview (exportable)

**And** shared evidence includes:

- Photo/artifact
- Mission/goal context
- Optional caption
- Anonymized user info (or real name if opted in)

**And** others can:

- React with encouragement emoji
- Comment (if enabled)
- Get inspired and create similar missions

**Prerequisites:** Story 8.3 (evidence gallery), Future multiplayer/pod system

**Technical Notes:**

- Schema: `shared_evidence` table (evidence_id FK, shared_scope ENUM[pod/public], shared_at, moderation_status)
- Moderation: manual review for public gallery to prevent abuse
- API: `GET /api/v1/evidence/shared` for public gallery
- Frontend: gallery with filtering and discovery features

---

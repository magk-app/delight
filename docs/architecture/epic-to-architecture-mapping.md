# Epic to Architecture Mapping

| Epic                          | Architecture Component                                     | Location                                                                             |
| ----------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Companion & Memory**        | LangGraph agents (`eliza_agent.py`), Chroma memory service | `backend/app/agents/`, `backend/app/services/memory_service.py`                      |
| **Goal & Mission Management** | Mission service, PostgreSQL models                         | `backend/app/services/mission_service.py`, `backend/app/models/mission.py`           |
| **Narrative Engine**          | Narrative service, LangGraph narrative agent               | `backend/app/services/narrative_service.py`, `backend/app/agents/narrative_agent.py` |
| **Progress & Analytics**      | Progress service, DCI calculation                          | `backend/app/services/progress_service.py`, `frontend/src/app/progress/`             |
| **Nudge & Outreach**          | ARQ workers, scheduled jobs                                | `backend/app/workers/nudge_scheduler.py`                                             |
| **World State & Time**        | World service, time-aware state                            | `backend/app/services/world_service.py`, `backend/app/api/v1/world.py`               |
| **Evidence & Reflection**     | File upload service, S3 integration                        | `backend/app/services/evidence_service.py`                                           |
| **User Onboarding**           | Auth service, onboarding flow                              | `backend/app/core/security.py`, `frontend/src/app/(auth)/`                           |

---

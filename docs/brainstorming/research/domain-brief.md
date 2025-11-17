# Domain Brief - delight

Generated: 2025-11-12
Domain: Personal productivity & mental wellness companion agents
Complexity: High (interdisciplinary human factors + AI safety)

## Executive Summary

Delight’s Epic 2 focuses on “Eliza,” an emotionally intelligent productivity companion that blends task tracking, stress-awareness, and narrative motivation. The system must remember who the user is, what they are working on, and how they are feeling—across short-term blockers, long-term aspirations, and personal philosophies. Early research highlights three differentiators: a tiered memory architecture (personal, project, task), emotionally aware coaching, and gamified storytelling that nudges users toward discomfort-zone tasks without eroding psychological safety.

## Domain Overview

### Industry Context

The product sits at the intersection of productivity tooling, AI coaching, quantified self, and mental-wellness companions. Unlike standard task managers, it must synthesize operational data (tasks, blockers, commitments) with human context (stress signals, attachment styles, motivational narratives). Comparable references include ADHD-focused planners, CBT-informed coaching apps, and narrative productivity RPGs, but few combine deep memory with empathetic AI guidance.

### Regulatory Landscape

While not delivering clinical therapy, the agent handles sensitive emotional and behavioral data. That introduces privacy and data-handling obligations (GDPR/CCPA, HIPAA-adjacent safeguards if health data ever enters the system, SOC2 expectations for enterprise). Emotion models and behavioral nudges must also respect emerging AI transparency and safety guidelines.

### Key Stakeholders

- End users juggling ambitious projects, emotional complexity, and executive-function challenges
- Product/design teams crafting the narrative and motivational frameworks
- Safety/compliance reviewers ensuring ethical handling of emotional and identity data
- Potential therapists or coaches who may integrate insights into care plans later

## Critical Concerns

### Compliance Requirements

Self-coaching scope avoids HIPAA-level constraints, but we still commit to privacy-by-design: encrypted storage of emotional/motivational data, GDPR/CCPA rights management, and SOC2-style auditability for enterprise use. When insight quality drops or distress signals exceed thresholds, Eliza must surface disclaimers and recommend professional resources (therapy, crisis lines) so autonomy and safety stay clear.

### Technical Constraints

- **Deep memory architecture:** Three tiers (personal identity, project arcs, task intents) need consistent embedding, metadata schema, and recall heuristics so advice always reflects “who Jack is” plus what he’s working on.
- **Narrative motivation engine:** Memory retrieval feeds story-beats (quests, allies, milestones) that transform todo items into character growth; requires storyline templates, pacing logic, and personalization variables (values, attachment style, aspirational archetype).
- **Emotion + stress sensing:** Lightweight telemetry (message sentiment, time-of-day fatigue, stated blockers) must drive agent state (push, balance, circuit-breaker) and keep latency under ~100 ms with hybrid search.

### Safety/Risk Considerations

Goal is resilience, not fear—so “risks” translate into design guardrails: track stress load, trigger Yes-Theory-style challenges only when energy permitting, and pair every push with grounding techniques or narrative framing. Intrinsic motivation stays central; accountability prompts act as mirrors, not guilt trips.

## Regulatory Requirements

- **Transparency + consent:** Present clear onboarding copy that explains Delight is a self-coaching companion, how the three memory tiers capture emotional + behavioral data, and how users can opt out or delete any tier on demand (GDPR/CCPA Articles 13/17 alignment).
- **Data minimization + retention:** Store only what powers memory-driven coaching; prune task-tier data after 30 days (per Story 2.2) while retaining personal/project tiers until the user revokes consent. Document retention windows so future enterprise buyers can audit them.
- **Security posture:** Reuse backend SOC2-ready controls (encryption in transit/at rest, audit logs for memory writes/reads, least-privilege service accounts) to make future SOC2 reports straightforward.
- **Crisis handoff protocol:** Bake in policy + copy that, when stress detection crosses defined thresholds or when users request help, Eliza routes to professional resources (therapists, suicide prevention hotlines) and clearly states she is not a licensed clinician.
- **Responsible AI notices:** Include inline disclosures for narrative nudges and “Yes Theory” style challenges so users understand the encouragement is AI-generated and can disable it if desired.

## Industry Standards

- **Productivity research:** Ground prioritization heuristics in proven systems (GTD capture/clarify, PARA organization, OKR/ICE scoring) so Eliza’s suggestions feel rigorous rather than ad hoc.
- **Motivation science:** Use Self-Determination Theory (autonomy, mastery, purpose), BJ Fogg’s behavior model, and Atomic Habits-style habit loops to ensure nudges respect intrinsic motivation rather than guilt.
- **Narrative design:** Borrow arcs from Hero’s Journey + Campbell/Vogler story beats, plus live-ops practices from cozy RPGs, to translate tasks into quests with stakes, allies, and celebratory feedback loops.
- **Emotional resilience playbooks:** Blend CBT reframing, Acceptance & Commitment Therapy defusion, Yes Theory’s “seek discomfort” ethos, and somatic grounding prompts so pushes always pair with regulation techniques.
- **AI memory architecture:** Follow Epic 2 specs—start with pgvector-backed three-tier memory, graduate to mem0 for personal/project deduplication once metrics demand it, and orchestrate via LangGraph vertical slices for traceable state.

## Practical Implications

### Architecture Impact

- LangGraph-driven companion must orchestrate three memory tiers plus emotion sensing in one pass; requires state graph nodes (receive → recall → reason → respond → store) with streaming hooks for the vertical slice (Story 2.5) before extraction (Story 2.2).
- Hybrid memory stack: start with pgvector inside Postgres for all tiers, but keep adapters ready to route personal/project memories to mem0/Qdrant when dedup accuracy needs improve; task tier stays local for low-latency CRUD and pruning jobs.
- Narrative layer lives beside AI agent, not in frontend—define a “story engine” module that reads memory metadata (values, archetype, streaks) and emits prompts/UI payloads so both backend responses and frontend visuals stay in sync.
- Emotion + stress telemetry feeds into an “energy state” reducer shared by the agent and frontend, ensuring pushes/circuit-breakers follow consistent rules.

### Development Impact

- Need vertical-slice-first workflow: implement chat UI + inline memory logic (Story 2.5) to prove the loop end-to-end, then refactor into services (Story 2.2) to avoid blind infrastructure work.
- Requires cross-functional pairing (backend + UX narrative) to encode story templates, persona variables, and push/balance heuristics directly into prompts/tests.
- Telemetry + safety hooks must be configurable; developers need tooling to simulate stress loads, view retrieved memories, and flip between “Yes Theory push” vs “rest” responses during QA.
- Additional docs + onboarding flows to explain privacy choices and allow users to inspect/delete memories by tier, which means building admin/debug UIs early.

### Timeline Impact

- Vertical slice (Story 2.5) becomes gating item; once chat loop + essential memory works, extraction (2.2) and LangGraph agent (2.3) can partially overlap but still depend on stable telemetry schema.
- Emotion detection (Story 2.6) can start after vertical slice but should land before mem0 migration so stress signals influence dedup priorities; expect 1–2 sprints of overlap for model evaluation + UX tuning.
- Compliance copywriting + consent flows should ship with Story 2.5 to avoid retrofitting; delays here block beta testing because data rights messaging is required.
- Mem0 or advanced memory service adoption should be milestone-based (triggered by accuracy metrics) rather than fixed date, so schedule includes a validation checkpoint after Story 2.2.

### Cost Impact

- Baseline infra stays lean: shared Postgres (pgvector) + Redis + FastAPI/Next.js, so incremental cost is primarily LLM + embedding usage (<$0.10/user/day per README targets).
- Potential mem0/Qdrant migration adds ~$20–50/month self-hosted or ~$70/month with Pinecone; budget this as “accuracy reserve” once recall targets demand it.
- Emotion detection uses open-source RoBERTa models (Story 2.6) to avoid per-call API fees, but requires GPU time for fine-tuning or ONNX optimization; plan for occasional cloud GPU spend.
- Narrative content creation (story beats, celebrations) may need dedicated design/writing time or contract support—operational cost is more people-time than infra but should be recognized in roadmap.

## Domain Patterns

### Established Patterns

- **Three-tier memory architectures**: Many effective companions (Replika-inspired, MemAI, AutoGen) separate autobiographical context, medium-term goals, and short-term tasks so retrieval cost stays low while identity feels stable.
- **Emotion-led session loops**: Products like Introspect, Woebot, and Reflectly open every session with a check-in, then adapt mission size and tone to the user’s affect before suggesting work.
- **Narrative scaffolding for productivity**: Habitica, SuperBetter, and cozy RPG planners wrap mundane tasks in quest metaphors with streaks, allies, and celebratory artifacts to sustain engagement.
- **Energy-based push/pause frameworks**: Coaching platforms use “energy meters” or readiness scores to decide when to encourage harder pushes versus recommending recovery rituals—mirrors the circuit-breaker design in Epic 2 docs.
- **Vertical slice development**: Leading agentic systems validate memory + UX with working slices before extracting services, matching the Story 2.5 → Story 2.2 sequencing.

### Innovation Opportunities

- **Personal philosophy embedding**: Capture values, belief statements, and attachment styles as first-class memory types so Eliza’s advice references the user’s worldview instead of generic affirmations.
- **Dynamic narrative arcs**: Let companions choose from story templates (Hero’s Journey, slice-of-life, semester arc) that evolve based on detected stress/load, making motivation feel serialized rather than episodic.
- **Yes-Theory-inspired challenge generator**: Blend comfort-zone telemetry with narrative hooks to propose “seek discomfort” quests that still respect energy levels and provide negotiation levers.
- **Memory-aware consent UX**: Build UI that visualizes each memory tier, lets users edit/delete entries inline, and teaches why certain data improves coaching—trust-through-visibility.
- **Hybrid memory backplanes**: Mix pgvector (cheap, local) for rapid iteration with optional mem0 channels for high-fidelity personal/project memories, toggled once recall metrics demand it.

## Risk Assessment

### Identified Risks

- **Memory drift or loss of trust**: If Eliza forgets identity details or surfaces irrelevant memories, users disengage because the “companion” illusion breaks.
- **Narrative fatigue**: Overly gamified story beats may feel cheesy or repetitive, reducing intrinsic motivation.
- **Push/preserve imbalance**: Without accurate energy sensing, Yes-Theory-style prompts could arrive when users are depleted, creating frustration rather than courage.
- **Privacy concerns**: Even with optimistic users, storing attachment styles, stress logs, and relationship notes requires crystal-clear transparency to avoid hesitancy.
- **Vertical-slice delays**: If Story 2.5 slips, downstream service extraction and LangGraph agent work cannot start with real data, slowing the epic.

### Mitigation Strategies

- Track memory quality metrics (recall@10, precision, task-loss rate) and promote mem0 migration only when thresholds dip below targets; add inline “why this memory” tooltips in chat.
- Rotate narrative templates, let users pick tone (epic, cozy, pragmatic), and inject callbacks to their own words to keep story beats fresh and personalized.
- Maintain an “energy state” variable sourced from check-in sentiment + workload metadata; gate discomfort challenges behind minimum energy scores and always pair with grounding suggestions.
- Ship transparent privacy controls early: per-tier visibility, delete/edit tools, clear retention statements, and auto-suggestions to redact sensitive info before saving.
- Treat vertical slice as the epic’s heartbeat—timebox Story 2.5 scope, stub expensive features, and log learnings immediately to unblock Story 2.2/2.3 planning.

## Validation Strategy

### Compliance Validation

- Privacy/consent copy reviewed alongside Story 2.5 UX; run checklist against GDPR/CCPA articles (notice, access, deletion) and simulate opt-out/delete flows.
- Security: verify audit logging around memory CRUD, encryption configs, and role-based access via automated tests and manual inspection.
- Crisis protocol dry-runs: trigger stress-threshold scenarios in staging to ensure hotline recommendations display instantly and are logged.

### Technical Validation

- Memory accuracy suite: automated tests that create 100+ memories across tiers, evaluate recall@10 and task-loss rate, and confirm pruning worker behavior.
- Vertical slice manual scenarios (venting, task capture, memory recall) executed in UI to guarantee inline memory logic matches acceptance criteria.
- Narrative engine snapshot tests to ensure retrieved memories feed story templates correctly and SSE streaming remains stable under load.
- Emotion detection benchmarking comparing RoBERTa outputs to tagged sample data; tune thresholds until precision/recall acceptable for energy gating.

### Domain Expert Validation

- Partner with internal narrative designers + behavioral coaches (if available) for monthly reviews of story arcs, prompts, and motivational framing.
- Conduct user panels with ambitious builders/students to walk through personas, verify that memory recall feels authentic, and gather qualitative feedback on push/balance behavior.
- Incorporate Yes-Theory style advisors or community members for feedback on discomfort challenges to ensure authenticity and respect for boundaries.

## Key Decisions

- **Domain approach**: Position Delight as a self-coaching productivity companion that blends deep autobiographical memory with narrative motivation; emotional safety is achieved through push/pause heuristics instead of clinical safeguards.
- **Memory architecture**: Launch with pgvector-backed three-tier system inside Postgres for simplicity; earmark mem0/Qdrant migration for personal/project tiers once recall metrics fall below 90%.
- **Development order**: Follow the approved vertical slice plan (Story 2.5 before 2.2) so UX + memory assumptions are validated with real conversations before infrastructure hardens.
- **Narrative focus**: Treat stories as first-class outputs generated server-side; invest in templates and persona variables early so UI just renders structured payloads.
- **Safety stance**: No therapist integrations initially, but include crisis escalation messaging and easy ways for users to pause or adjust discomfort challenges.

## Recommendations

### Must Have (Critical)

1. **Three-tier memory with identity fidelity** – Personal, project, and task tiers must capture values, philosophies, stressors, and mission context so Eliza’s coaching always reflects who the user is and what they’re tackling.
2. **Narrative motivation loop** – Every chat cycle should transform priorities into story beats (quests, allies, celebrations) to keep goals compelling and intrinsically motivating.
3. **Energy-aware push/preserve logic** – Stress/energy sensing (via check-ins + emotion detection) must drive whether Eliza pushes for discomfort-zone action or recommends circuit breakers, with clear handoff to human help when needed.

### Should Have (Important)

1. **Hybrid memory accuracy upgrades** – Instrument recall metrics and enable optional mem0/Qdrant lanes for personal/project tiers once dedup accuracy or token costs require it.
2. **Memory transparency + editing UX** – Users should inspect, edit, or delete memories per tier directly in the app to build trust and stay compliant.
3. **Dynamic narrative templates** – Offer multiple tonal arcs (epic, cozy, pragmatic) and rotate story structures to avoid fatigue and keep motivation personalized.

### Consider (Nice-to-Have)

1. **Yes-Theory challenge generator** – Optional mode that proposes “seek discomfort” quests with negotiation levers and built-in grounding rituals.
2. **Attachment-style informed coaching** – Use onboarding surveys and memory cues to tailor encouragement styles (e.g., secure reassurance vs. autonomy boosts).
3. **Social accountability hooks** – Lightweight sharing/export mechanisms so users can loop in friends/coaches once intrinsic motivation is established.

### Development Sequence

1. **Story 2.5 vertical slice** – Chat UI + inline memory orchestration + narrative outputs working end-to-end.
2. **Story 2.2 extraction** – Pull proven memory logic into services, add hybrid search/pruning, integrate metrics.
3. **Story 2.3 LangGraph agent** – Build the full state machine, formalize prompts, wire energy state + narrative engine.
4. **Story 2.6 emotion detection** – Add model-driven emotion sensing feeding energy logic and narrative pacing.
5. **Mem0 upgrade (conditional)** – Promote personal/project memories to mem0 when recall metrics dip or scale demands it.

### Required Expertise

- **Applied AI engineer** – LangGraph, hybrid memory, emotion detection integration.
- **Narrative/design lead** – Story template creation, tone systems, motivational UX copy.
- **Behavioral coach / productivity researcher** – Map GTD, SDT, Yes-Theory concepts into actionable heuristics and guardrails.
- **Security/compliance engineer** – Ensure data rights, logging, and privacy UX meet GDPR/CCPA/SOC2 expectations.

## PRD Integration Guide

### Summary for PRD

Delight is a self-coaching productivity + mental-wellness companion that hinges on deep autobiographical memory and narrative motivation. The PRD must emphasize: (1) three-tier memory fidelity with privacy controls, (2) story-driven prioritization and celebration loops, and (3) energy-aware coaching logic that knows when to push or pause, with crisis escalation copy baked in.

### Requirements to Incorporate

- Three-tier memory storage, retrieval metrics, and UX for inspecting/deleting memories.
- Narrative engine outputs delivered with every chat cycle to drive intrinsic motivation.
- Emotion/stress sensing + push/preserve heuristics, including human-help escalation paths.

### Architecture Considerations

- LangGraph state machine orchestrating memory recall, reasoning, narrative generation, and storage in a single streaming pipeline.
- Hybrid memory stack (pgvector baseline, mem0 migration readiness) plus shared energy-state reducer accessible to frontend and backend.

### Development Considerations

- Follow vertical slice order (Story 2.5 → 2.2 → 2.3) so UX + memory accuracy are proven with real scenarios before service extraction.
- Embed privacy copy, consent flows, and memory management UI in the same milestone to avoid rework and unblock beta testing.

## References

### Regulations Researched

- GDPR Art. 13/17 guidance on data access, deletion, and transparent notices for personal data.
- CCPA user rights overview focused on data collection disclosures and opt-out mechanisms for coaching apps.

### Standards Referenced

- Getting Things Done (GTD) methodology for capture → clarify → organize workflows.
- Self-Determination Theory (autonomy, mastery, purpose) to guide motivational framing.

### Additional Resources

- Epic 2 Technical Specification (`docs/tech-spec-epic-2.md`).
- Memory Architecture Comparison (`docs/epic-2/MEMORY-ARCHITECTURE-COMPARISON.md`).

## Appendix

### Research Notes

- README + Product Brief highlight Delight’s differentiators: emotionally aware coaching, narrative worldbuilding, structured progress; these inform domain context and requirements.
- Epic 2 Technical Spec + Vertical Slice notes emphasize three-tier memory, LangGraph orchestration, and Story 2.5-first strategy; forms basis for architecture/timeline sections.
- Memory Architecture Comparison outlines pgvector vs. mem0 tradeoffs; used to plan hybrid memory + migration triggers.
- “How Eliza Should Respond” walkthrough demonstrates desired push/preserve tone, triage patterns, and circuit-breaker logic; informs narrative + energy-state design.
- User guidance reinforced focus on deep memory, narrative motivation, and optimistic framing (risk-as-guardrail mindset).

### Conversation Highlights

- User confirmed domain = self-coaching productivity companion (no HIPAA), with emphasis on deep memory + narrative motivation.
- Identified pillars: memory depth, narrative motivation, stress navigation/Yes-Theory-style challenges; accountability secondary.
- User asked for optimistic framing (risks reframed as positive guardrails) and requested relocation of new research docs under `docs/brainstorming/research/`.

### Open Questions

- What specific onboarding surveys or signals will capture attachment style, philosophies, and long-term stressors without overwhelming new users?
- Which narrative templates resonate most with target personas (founders vs. students) and how often should arcs rotate?
- What quantitative thresholds define “energy low” vs. “energy high” for discomfort challenges—purely emotion-model output or blend with behavior metrics (sleep, streaks)?

---

_This domain brief was created through collaborative research between {user_name} and the AI facilitator. It should be referenced during PRD creation and updated as new domain insights emerge._

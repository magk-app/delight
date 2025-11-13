# Technical Specification — Mintlify Documentation Publication

Date: 2025-11-13  
Author: Jack (Mintlify Docs track)  
Project Level: 1 (Quick Flow, Brownfield)  
Status: Draft

---

## 1. Overview
Delight already stores comprehensive Markdown documentation under `docs/`, but the content is inaccessible without cloning the repo. This project publishes the existing knowledge base through Mintlify so product stakeholders, developers, and AI agents get a searchable, linkable documentation site that mirrors the repo structure.

### Objectives
1. Ship a Mintlify site that mirrors the `docs/` hierarchy (index, architecture, runbooks, epics, stories).
2. Automate previews, linting, and deploys so docs regressions are caught in CI before release.
3. Expose FastAPI endpoints through Mintlify’s API reference, generated straight from the backend OpenAPI schema.
4. Keep `docs/` as the source of truth—Mintlify should never become a separate content store.

### Out of Scope
- Rewriting or restructuring content beyond navigation tweaks required for Mintlify.
- Multi-language or authenticated docs (defer until after initial launch).
- Replacing existing BMAD docs; this effort only layers Mintlify on top.

---

## 2. Current State Assessment
| Area | Findings |
| --- | --- |
| Content | `docs/` contains architecture deep dives, epics, runbooks, and sprint trackers already indexed in `docs/INDEX.md`. |
| Tooling | Mintlify CLI referenced in `docs/ARCHITECTURE.md`, but there is no `mint.json`, CLI dependency, or npm script. |
| API Reference | FastAPI’s OpenAPI schema is not exported anywhere, so API docs can’t be surfaced. |
| CI/CD | No automation exists for docs-specific linting; GitHub Actions only cover core app pipelines. |
| Hosting | No Mintlify project or custom domain configured. All docs are local-only. |

Implication: this is a brownfield Level 1 change—documentation assets exist, but the Mintlify delivery layer is missing.

---

## 3. Target Architecture
| Layer | Decisions |
| --- | --- |
| Source of Truth | Continue editing Markdown under `docs/`. Mintlify only consumes it. |
| Mintlify Config | Add `docs/mint.json` (or `mint.config.ts`) with sections mirroring `docs/INDEX.md`: Introduction, Setup, Architecture, Runbooks, Epics, Guides, API Reference. |
| API Reference | Export FastAPI schema via a script (`poetry run python scripts/export_openapi.py > docs/api-reference/openapi.json`) and wire it into Mintlify’s `api` block. |
| Tooling | Pin `mintlify` CLI as a devDependency in the repo root, exposing `npm run docs:dev`, `docs:lint`, and `docs:deploy`. |
| CI | Add `.github/workflows/docs.yml` that runs `npm ci` + `npm run docs:lint` whenever `docs/**` or doc tooling changes. |
| Hosting | Connect repo to Mintlify Cloud, enable preview builds on PRs, and deploy `main` to `docs.delight.so` (or agreed domain) with SSL. |
| Access Control | Keep Mintlify project private/invite-only until launch approval, then flip DNS. |

---

## 4. Implementation Plan
### Phase A — Inventory & Config
1. Generate a manifest of Markdown files (`rg --files docs --iglob '*.md'`) and map each path to a Mintlify sidebar entry.
2. Run `mintlify init --path docs` and commit the scaffold (`docs/mint.json`, `docs/public/`, theme overrides).
3. Add scripts to `package.json`:
```json
"scripts": {
  "docs:dev": "mintlify dev --config docs/mint.json",
  "docs:lint": "mintlify lint --config docs/mint.json",
  "docs:deploy": "mintlify deploy --config docs/mint.json"
}
```
4. Document new tooling in `README.md` and `docs/runbook/documentation.md`.

### Phase B — API Reference & Automation
1. Create `packages/backend/scripts/export_openapi.py` to dump FastAPI’s schema.
2. Store the generated JSON in `docs/api-reference/openapi.json` and reference it inside `mint.json`.
3. Add `.github/workflows/docs.yml` that installs Node 20, runs `npm ci`, and executes `npm run docs:lint`. Failures block merges.
4. Optionally add `markdownlint-cli` to catch formatting issues before Mintlify even runs.

### Phase C — Hosting & Rollout
1. Create the Mintlify project, connect GitHub, and enable preview builds.
2. Configure production deploy on `main`, then request DNS for `docs.delight.so` (or chosen hostname) and enable SSL.
3. Define a launch checklist + rollback plan inside `docs/runbook/documentation.md`.
4. After verification, announce the new docs entry point and keep the site private/public per leadership guidance.

---

## 5. Testing & Validation
1. Local lint/preview: `npm run docs:lint` and `npm run docs:dev`, clicking through each sidebar section plus the API reference.
2. CI: ensure `.github/workflows/docs.yml` passes on every PR touching docs/tooling.
3. Production smoke: verify Mintlify analytics show a successful deploy, and spot-check canonical URLs (e.g., `/guides/quickstart`, `/architecture/system-design`) return HTTP 200.
4. API verification: cross-check a few FastAPI endpoints in Mintlify’s API explorer and ensure examples match backend handlers.

---

## 6. Risks & Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Drift between Mintlify and repo | Stale docs surface publicly | Treat `docs:lint` output as required evidence in PRs; update runbook checklists. |
| Missing OpenAPI export | API tab fails to render | Automate schema export and fail CI when JSON isn’t regenerated. |
| Premature public access | Sensitive content leaks | Maintain private visibility until sign-off; audit content before DNS switch. |
| CLI version mismatch | Different previews locally vs CI | Pin `mintlify` in `package.json` and rely on `npm run` scripts instead of global installs. |

---

## 7. Deliverables
1. `docs/mint.json` (plus theme assets) describing navigation and metadata.
2. `docs/api-reference/openapi.json` generated from FastAPI.
3. `mintlify/epic-mintlify-docs.md` with epic + stories for execution (see below).
4. `.github/workflows/docs.yml` and updated `package.json` scripts.
5. Updated `docs/runbook/documentation.md` capturing launch/rollback steps (already drafted).

---

## 8. Story Breakdown (Level 1 Quick Flow)
See `mintlify/epic-mintlify-docs.md` for full details; summary:
1. **Story 1:** Inventory existing docs and bootstrap Mintlify config.
2. **Story 2:** Export API schema and enforce docs linting in CI.
3. **Story 3:** Publish Mintlify site and document operations procedures.

Each story references this tech spec as its primary technical context, so developers can implement without running separate story-context workflows.

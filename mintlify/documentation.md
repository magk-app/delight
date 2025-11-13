# Runbook: Mintlify Docs

## Purpose
Keep the Delight documentation site (Mintlify) in a predictable layout so anyone can spin it up locally or add new guides without hunting for instructions.

## Directory Layout
```
docs/
├─ mint.json           # Global Mintlify config
├─ introduction.md     # Landing page
├─ quickstart.md       # 5‑minute setup
├─ api-reference/      # Auto/hand-written endpoints
├─ architecture/       # System design notes
└─ guides/             # Feature walkthroughs
```
Touch only the content files; structural tweaks go through `mint.json`.

## Local Workflow
1. `npm install -g mintlify` (once per machine)
2. `mintlify dev` from repo root → serves at http://localhost:3000 with hot reload
3. Author/change docs in Markdown or import OpenAPI specs; Mintlify Watcher rebuilds instantly
4. When satisfied, commit Markdown + `mint.json` updates together

## Tips
- Keep API examples alongside handlers, then embed them via code fences.
- Prefer short “Task + Outcome” sections so Codex/agents can chunk instructions.
- Record new sections in `docs/INDEX.md` so discovery stays simple.

---

## Tech Spec: Publish Delight Docs via Mintlify

### Summary
1. Delight already maintains a rich Markdown knowledge base under `docs/`, but there is no Mintlify project (`mint.json`) or deployment target, so content cannot be previewed or shared as a coherent documentation site.
2. This Level 1 change publishes the repository documentation through Mintlify so product, engineering, and AI agents can browse, search, and link to living docs without cloning the repo.
3. Deliverables: Mintlify configuration checked into the repo, automated lint/preview workflows, and a documented launch + rollback path captured in this runbook.

### Current State Assessment
1. Source files live in `docs/` with curated indices such as `docs/INDEX.md`, epic tech specs (`docs/tech-spec-epic-*.md`), and runbooks (`docs/runbook/*.md`).
2. No Mintlify configuration exists (`mint.json`/`mint.config.ts` is absent), so Mintlify CLI commands cannot load navigation or themes.
3. Mintlify CLI is mentioned in `docs/ARCHITECTURE.md`, but there is no package-level script, npm dependency, or GitHub Action enforcing documentation linting.
4. The API reference folder referenced in architecture docs is not yet generated from FastAPI (no OpenAPI artifact checked in), so Mintlify cannot surface reference docs today.

### Goals
1. Keep `docs/` as the single source of truth while exposing the same content via Mintlify with search, navigation, and responsive layouts.
2. Provide a repeatable local workflow (`npm run docs:dev` → `mintlify dev`) plus CI validation so contributors catch broken links before publish.
3. Host the Mintlify site on a Delight-owned domain (e.g., `docs.delight.so`) with automatic deploys on `main`.
4. Publish the FastAPI OpenAPI contract (generated from `packages/backend`) into Mintlify’s `api-reference/` section for live endpoint documentation.

### Non-Goals
1. Rewriting existing documentation content or changing ownership of documents outside the Mintlify navigation work.
2. Replacing Mintlify with another documentation system—this spec only covers Mintlify packaging and publication.
3. Building multi-language translations or gated docs (can be handled later via Mintlify Enterprise features).

### Requirements & Constraints
1. **Content fidelity:** Markdown structure, code fences, and mermaid blocks must render correctly in Mintlify; any unsupported syntax requires conversion.
2. **Access control:** Until a public launch is approved, the Mintlify project should remain “private with invite” so docs are not accidentally exposed.
3. **Automation:** Docs CI must block merges when `mintlify lint` or link checks fail; leverage GitHub Actions that already run for the repo.
4. **Traceability:** Every Mintlify navigation item must map back to a file tracked in `docs/INDEX.md` so AI agents can continue referencing canonical paths.
5. **No secret leakage:** Ensure `.env` samples or secrets referenced in docs comply with the “never commit secrets” rule from `AGENTS.md`.

### Target Architecture & Tooling
| Layer | Implementation | Notes |
| --- | --- | --- |
| Source of truth | Markdown + assets already in `docs/` | Continue using folders like `architecture/`, `epics/`, `runbook/` |
| Navigation | `docs/mint.json` (or `mint.config.ts`) with groups: Introduction, Setup, Architecture, Guides, Runbooks, API Reference | Mirror the structure described in `docs/INDEX.md` so visitors see a familiar outline |
| API Reference | Export FastAPI schema via `poetry run python scripts/export_openapi.py > docs/api-reference/openapi.json` | Hook Mintlify `api` block to the generated JSON; regenerate on backend changes |
| Local tooling | `devDependencies` entry for `mintlify` in root `package.json`, plus scripts `docs:dev`, `docs:lint`, `docs:deploy` | This keeps CLI versions pinned and reproducible |
| CI enforcement | `.github/workflows/docs.yml` running `npm ci && npm run docs:lint` on `docs/**` changes | Failure blocks merge; cache npm for speed |
| Hosting | Mintlify Cloud connected to GitHub (`main` branch) with optional preview deployments on PRs | Configure custom domain + SSL once DNS is ready |

### Implementation Plan
1. **Inventory & Mapping (Owner: Docs)**
   - Generate a list of all Markdown endpoints using `rg --files docs --iglob '*.md'`.
   - Decide which files become Mintlify sidebar entries vs. hidden reference pages; update `docs/INDEX.md` if any new landing pages are needed.
   - Identify assets to exclude (archived docs, private briefs) or move under an `archive/` section.
   - Output: spreadsheet or `docs/runbook/documentation.md` appendix that maps file → Mintlify slug.
2. **Bootstrap Mintlify Config (Owner: Docs Platform)**
   - Install CLI locally: `npm install -g mintlify` (already noted in this runbook) and run `mintlify init --path docs`.
   - Commit `docs/mint.json`, `docs/public/` assets (logo, favicon), and optional theme overrides.
   - Add `scripts` to root `package.json`:
     ```json
     "scripts": {
       "docs:dev": "mintlify dev --config docs/mint.json",
       "docs:lint": "mintlify lint --config docs/mint.json",
       "docs:deploy": "mintlify deploy --config docs/mint.json"
     }
     ```
   - Document any required env vars (e.g., `MINTLIFY_API_KEY`) in `README.md`.
3. **Wire API Reference (Owner: Backend)**
   - Add a FastAPI utility script that prints the OpenAPI schema (`from fastapi.openapi.utils import get_openapi`).
   - Store output in `docs/api-reference/openapi.json` and add a regenerate step to backend CI or release checklist.
   - Reference the file inside `mint.json` under the `api` block so the Mintlify sidebar renders endpoints.
4. **Local QA + CI (Owner: Docs Platform)**
   - Run `npm run docs:dev` to confirm the site loads, then walk through every section using the nav.
   - Add `.github/workflows/docs.yml`:
     ```yaml
     name: docs
     on:
       pull_request:
         paths:
           - 'docs/**'
           - 'package.json'
           - 'package-lock.json'
     jobs:
       lint:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v4
           - uses: actions/setup-node@v4
             with:
               node-version: 20
           - run: npm ci
           - run: npm run docs:lint
     ```
   - Optionally add `markdownlint-cli` to catch pure Markdown issues before Mintlify.
5. **Connect & Deploy (Owner: Platform)**
   - Create a Mintlify project, install the Mintlify GitHub App, and point it to this repository.
   - Configure preview environments on PRs and a production deploy on merges to `main`.
   - Once happy, set up DNS for `docs.delight.so` (or chosen hostname) and enable SSL inside Mintlify.
   - Document the deploy switch in this runbook, including how to trigger a manual `mintlify deploy`.

### Validation & Monitoring
1. `npm run docs:lint` passes locally and in CI (runs `mintlify lint` + link validation).
2. Manual regression pass: verify homepage hero, search, API reference, and at least one guide from each section.
3. Mintlify analytics dashboard shows successful deploy with no build errors.
4. Spot-check 3–5 canonical links (e.g., `/guides/quickstart`, `/architecture/system-overview`) to make sure they return HTTP 200 in production.

### Rollback Strategy
1. If the Mintlify deploy introduces regressions, toggle the project visibility back to “Private” or “Preview” to block public access.
2. Revert the Git commit that introduced `mint.json`, CI changes, or navigation updates; Mintlify will rebuild using the previous working commit.
3. Update this runbook with the rollback reason so on-call engineers know which docs version is live.

### Risks & Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Missing or outdated OpenAPI export | API reference tab is blank or wrong | Automate schema export during backend CI and fail the job if the JSON diff is missing |
| Docs drift between repo and Mintlify | Users see stale instructions | Treat Mintlify deploy as part of the Definition of Done; PR template should include “`npm run docs:lint` output pasted” |
| Unauthorized public access | Sensitive docs leak | Keep Mintlify project private until leadership approves, and audit pages before flipping DNS |
| CLI version mismatches | Contributors see different previews | Pin `mintlify` CLI via devDependency and rely on `npm run` scripts instead of global installs |

### Work Packages (Suggested Level 1 Stories)
1. **Story: Docs Inventory & Mintlify Config**
   - Tasks: audit `docs/`, decide nav grouping, run `mintlify init`, commit `docs/mint.json`.
   - Acceptance: navigation matches sections listed in `docs/INDEX.md`; `npm run docs:dev` renders without runtime errors.
2. **Story: API Reference + Automation**
   - Tasks: add OpenAPI export script under `packages/backend/scripts/`, generate `docs/api-reference/openapi.json`, wire `mint.json` `api` block, add CI job running `npm run docs:lint`.
   - Acceptance: `mintlify lint` passes in CI; API tab shows FastAPI endpoints sourced from generated schema.
3. **Story: Publish & Document Operations**
   - Tasks: connect repo to Mintlify Cloud, configure production + preview deploys, set up custom domain/DNS, expand this runbook with launch + rollback steps.
   - Acceptance: published site reachable at agreed hostname with SSL; this runbook updated with deployment checklist and support contacts.

### Open Questions
1. Which domain should host the docs (`docs.delight.so`, `delight-docs.com`, or Mintlify-provided subdomain)?
2. Do we keep the site private to the team or expose it publicly for beta customers?
3. Should AI agents consume the Mintlify JSON Search API for retrieval, or continue reading Markdown directly from `docs/`?


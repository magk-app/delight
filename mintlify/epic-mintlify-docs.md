# Epic: Publish Delight Docs via Mintlify

## Epic Summary
Transform the static `docs/` folder into a Mintlify-powered documentation site with automated linting, API reference, and hosted previews so stakeholders can browse current guides without cloning the repo.

### Success Criteria
1. Mintlify navigation mirrors `docs/INDEX.md`, covering intro, setup, architecture, runbooks, guides, and epics.
2. FastAPI OpenAPI schema renders inside Mintlify’s API explorer.
3. GitHub Actions block merges when `mintlify lint` fails.
4. Production Mintlify site (private or public) deploys automatically from `main`, with documented launch/rollback steps.

---

## Story 1 — Stand Up Mintlify Config & Navigation
**User Story:**  
As a docs platform engineer, I need a Mintlify project that reflects our repository structure so anyone can preview Delight docs locally or via hosted previews.

**Technical Tasks**
1. Inventory all Markdown assets with `rg --files docs --iglob '*.md'` and map them to Mintlify sidebar sections.
2. Run `mintlify init --path docs`, commit `docs/mint.json`, `docs/public/`, and theme overrides.
3. Add `mintlify` as a devDependency plus `docs:dev`, `docs:lint`, and `docs:deploy` scripts in `package.json`.
4. Update `docs/runbook/documentation.md` with instructions for the new workflow.

**Acceptance Criteria**
- Mintlify dev server loads without missing routes, and navigation mirrors `docs/INDEX.md`.
- Running `npm run docs:dev` from repo root serves the docs at `http://localhost:3000`.
- Runbook shows the updated process for adding or editing docs.

---

## Story 2 — API Reference & CI Automation
**User Story:**  
As a backend engineer, I want the FastAPI schema rendered in Mintlify and protected by CI so API docs stay accurate and PRs fail when docs break.

**Technical Tasks**
1. Create `packages/backend/scripts/export_openapi.py` to serialize FastAPI’s OpenAPI spec.
2. Generate `docs/api-reference/openapi.json` via the script; wire the file into Mintlify’s `api` block.
3. Add `.github/workflows/docs.yml` that runs `npm ci` and `npm run docs:lint` on docs/tooling changes.
4. (Optional) Add `markdownlint-cli` to catch Markdown issues before Mintlify runs.

**Acceptance Criteria**
- `mintlify lint` passes locally and in CI.
- Mintlify API tab displays endpoints with request/response schemas sourced from OpenAPI JSON.
- PRs touching docs fail when `docs:lint` fails.

---

## Story 3 — Deploy Mintlify & Document Operations
**User Story:**  
As an operator, I need the Mintlify site deployed with a clear launch/rollback process so docs can be published (or pulled back) safely.

**Technical Tasks**
1. Create a Mintlify Cloud project, connect GitHub, and enable preview deployments.
2. Configure production deploy from `main` and set up DNS/SSL for the chosen domain (e.g., `docs.delight.so`).
3. Update `docs/runbook/documentation.md` with deployment, monitoring, and rollback steps; note owner/on-call expectations.
4. Confirm analytics and basic auth/search functionality post-launch.

**Acceptance Criteria**
- Production Mintlify site reachable at the agreed hostname (even if private).
- Runbook contains the launch checklist, verification steps, and rollback instructions.
- Analytics/dashboard show a successful deploy corresponding to the release commit.

---

## References
- `mintlify/tech-spec.md` (primary technical context)
- `docs/runbook/documentation.md` (operational runbook)
- `docs/INDEX.md` (navigation source of truth)

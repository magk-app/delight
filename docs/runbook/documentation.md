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


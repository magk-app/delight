# Runbook: Documentation Operations

## Purpose
Maintain the Delight documentation site (Mintlify) so anyone can spin it up locally, add new guides, or deploy updates without hunting for instructions.

## Directory Layout
```
mintlify/
├── docs.json              # Mintlify configuration (navigation, theme, branding)
├── introduction.md        # Landing page
├── quickstart.md          # 5-minute setup
├── architecture/          # System design docs
│   ├── overview.md
│   ├── executive-summary.md
│   ├── technology-stack.md
│   ├── decision-records.md
│   ├── data-architecture.md
│   ├── api-contracts.md
│   ├── security.md
│   └── deployment.md
├── dev/                   # Development guides
│   ├── setup.md
│   ├── bmad-guide.md
│   ├── quick-reference.md
│   └── contributing.md
├── epics/                 # Product epics
│   ├── overview.md
│   ├── epic-1.md through epic-8.md
├── users/                 # User guides
│   └── getting-started.md
└── runbook/              # Operational runbooks
    ├── documentation.md   # This file
    ├── deployment.md
    └── troubleshooting.md
```

## Local Development Workflow

### Prerequisites
- Node.js v19-v24 (LTS recommended)
- pnpm package manager
- Internet connection (mint CLI downloads resources on first run)

### Quick Start

1. **Install dependencies** (from repo root):
   ```bash
   pnpm install
   ```

2. **Start local preview**:
   ```bash
   pnpm docs:dev
   ```
   This launches the Mintlify dev server at http://localhost:3000 with hot reload.

3. **Edit documentation**:
   - Modify any `.md` file in `mintlify/`
   - Changes appear instantly in browser
   - Navigation structure is controlled by `docs.json`

4. **Lint before committing**:
   ```bash
   pnpm docs:lint
   ```
   This runs `mint broken-links` to catch broken internal links.

### Adding New Pages

1. **Create the Markdown file** in the appropriate directory:
   ```bash
   # Example: adding a new architecture doc
   touch mintlify/architecture/caching-strategy.md
   ```

2. **Write content** using standard Markdown:
   ```markdown
   # Caching Strategy

   ## Overview
   ...
   ```

3. **Add to navigation** in `docs.json`:
   ```json
   {
     "group": "Architecture",
     "pages": [
       "architecture/overview",
       "architecture/caching-strategy",  // Add here
       ...
     ]
   }
   ```

4. **Test locally**:
   ```bash
   pnpm docs:dev
   # Verify new page appears in sidebar
   ```

5. **Lint and commit**:
   ```bash
   pnpm docs:lint
   git add mintlify/
   git commit -m "docs: add caching strategy guide"
   ```

### Updating Navigation

Edit `mintlify/docs.json` to control:
- **Sidebar structure**: Groups and page order
- **Theme colors**: Primary, light, dark color schemes
- **Topbar links**: GitHub, external resources
- **Footer**: Social links, legal pages

After editing `docs.json`, refresh the preview to see changes immediately.

## Available Commands

From the repository root:

| Command | Description |
|---------|-------------|
| `pnpm docs:dev` | Start Mintlify dev server at http://localhost:3000 |
| `pnpm docs:lint` | Check for broken links and validation errors |
| `pnpm docs:deploy` | Deploy to Mintlify Cloud (requires API key) |

**Alternative (using npx)**:
```bash
cd mintlify
npx mint dev          # Local preview
npx mint broken-links # Link checking
npx mint deploy       # Deploy to cloud
```

## Content Guidelines

### Markdown Best Practices
- **Use descriptive headings**: Help readers scan quickly
- **Include code examples**: Use proper language tags for syntax highlighting
- **Add callouts**: Use Mintlify callouts for important notes
  ```markdown
  <Note>
  This is an important note that will be highlighted.
  </Note>

  <Warning>
  Critical warning that needs attention.
  </Warning>
  ```

### File Naming Conventions
- Use **kebab-case** for file names: `quick-reference.md`, not `Quick_Reference.md`
- Keep names **descriptive but concise**: `setup.md`, not `how-to-set-up-everything.md`
- Match **URL structure**: File `dev/setup.md` → URL `/dev/setup`

### Internal Links
```markdown
[Setup Guide](/dev/setup)
[Architecture Overview](/architecture/overview)
```
Links use absolute paths starting from `/`.

## CI/CD Integration

### Continuous Integration
When docs are modified, GitHub Actions should:
1. Install dependencies (`pnpm install`)
2. Run linting (`pnpm docs:lint`)
3. Block merge if linting fails

### Continuous Deployment
- **Preview Deployments**: Mintlify creates preview URLs for PRs
- **Production Deployment**: Merges to `main` auto-deploy to production
- **Rollback**: Revert the commit and Mintlify rebuilds from previous version

## Troubleshooting

See [Troubleshooting Runbook](/runbook/troubleshooting) for common issues and solutions.

Quick fixes:
- **Port 3000 in use**: Mint auto-selects next available port
- **Internet required**: Mint CLI needs connectivity for first run
- **Cache issues**: Delete `~/.mintlify` and restart dev server

## Resources

- **Mintlify Documentation**: https://mintlify.com/docs
- **Project Repository**: https://github.com/magk-app/delight
- **Deployment Runbook**: [See deployment.md](/runbook/deployment)

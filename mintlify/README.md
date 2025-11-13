# Mintlify Documentation Setup

This directory contains the Mintlify configuration and documentation pages for Delight.

## Quick Start

1. **Install dependencies** (if not already installed):

   ```bash
   pnpm install
   ```

2. **Start the Mintlify dev server**:

   ```bash
   pnpm docs:dev
   ```

3. **View your docs**: Open http://localhost:3000 in your browser

## Available Commands

- `pnpm docs:dev` - Start the Mintlify development server with hot reload
- `pnpm docs:lint` - Lint the documentation for errors
- `pnpm docs:deploy` - Deploy documentation to Mintlify Cloud (requires API key)

## Project Structure

```
mintlify/
├── mint.json              # Mintlify configuration
├── introduction.md        # Landing page
├── quickstart.md          # Quick start guide
├── architecture/          # Architecture documentation
│   └── overview.md
└── dev/                   # Development guides
    └── setup.md
```

## Adding New Pages

1. Create a new `.md` file in the appropriate directory
2. Add the page to `mint.json` navigation under the relevant group
3. The page will automatically appear in the sidebar

## Configuration

The `mint.json` file controls:

- Navigation structure
- Theme colors
- Topbar links and CTAs
- Footer social links

See [Mintlify Documentation](https://mintlify.com/docs) for full configuration options.

## Next Steps

- Add more pages from `docs/` directory
- Customize colors and branding in `mint.json`
- Set up Mintlify Cloud deployment
- Add API reference documentation

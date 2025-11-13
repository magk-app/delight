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
├── favicon.svg            # Site favicon (see below)
├── images/                 # Documentation images
│   └── .gitkeep
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

## Favicon

To update the favicon:

1. **Place your favicon file** in the `mintlify/` directory root:

   - Supported formats: `.svg`, `.png`, `.ico`
   - Recommended: Use `.svg` for best quality and scalability
   - File should be named `favicon.svg` (or update the path in `mint.json`)

2. **Update `mint.json`** if using a different filename or format:

   ```json
   {
     "favicon": "/favicon.svg" // or "/favicon.png", "/favicon.ico"
   }
   ```

3. **Restart the dev server** to see changes:
   ```bash
   pnpm docs:dev
   ```

**Note**: The favicon path in `mint.json` should start with `/` and be relative to the `mintlify/` directory root.

## Images

All documentation images should be placed in the `mintlify/images/` directory.

### Adding Images

1. **Place your image** in `mintlify/images/`:

   ```bash
   # Example: Save your image as
   mintlify/images/architecture-diagram.png
   ```

2. **Reference in markdown files**:

   ```markdown
   ![Architecture Diagram](/images/architecture-diagram.png)
   ```

3. **Supported formats**: `.png`, `.jpg`, `.jpeg`, `.svg`, `.gif`, `.webp`

### Image Best Practices

- Use descriptive filenames (e.g., `user-flow-diagram.png` not `image1.png`)
- Optimize images for web (keep file sizes reasonable)
- Use SVG for diagrams and logos when possible
- Use PNG for screenshots and complex images
- Consider responsive images for large diagrams

## Next Steps

- Add more pages from `docs/` directory
- Customize colors and branding in `mint.json`
- Set up Mintlify Cloud deployment
- Add API reference documentation

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

### Windows Users: Username with Spaces Issue

If you encounter a `SyntaxError: Invalid or unexpected token` error on Windows, this is likely because your Windows username contains spaces (e.g., "Jack Luo"). Here are three solutions:

**Option 1: Use npx (Recommended - No Installation Needed)**

Instead of using the globally installed mint CLI, use npx which bypasses the path issue:

```bash
# From the mintlify directory
npx mint dev

# Or from the repo root
cd mintlify && npx mint dev
```

**Option 2: Use WSL (Windows Subsystem for Linux)**

1. Install WSL: `wsl --install` in PowerShell (admin)
2. Open your WSL terminal (Ubuntu/Debian)
3. Navigate to your project: `cd /mnt/c/Users/Jack\ Luo/Desktop/delight`
4. Run: `pnpm docs:dev`

**Option 3: Change npm Global Prefix**

Change where npm installs global packages to a path without spaces:

```bash
# Create a directory for global packages
mkdir C:\npm-global

# Configure npm to use it
npm config set prefix C:\npm-global

# Add to PATH: C:\npm-global (System Environment Variables)

# Reinstall mint
pnpm add -g mint

# Now pnpm docs:dev should work
```

**Verification**: After applying any solution, run `pnpm docs:dev` and verify the server starts at http://localhost:3000

## Available Commands

- `pnpm docs:dev` - Start the Mintlify development server with hot reload
- `pnpm docs:lint` - Lint the documentation for errors
- `pnpm docs:deploy` - Deploy documentation to Mintlify Cloud (requires API key)

## Project Structure

```
mintlify/
├── docs.json              # Mintlify configuration (renamed from mint.json in Feb 2025)
├── favicon.ico            # Site favicon (see below)
├── images/                # Documentation images
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
2. Add the page to `docs.json` navigation under the relevant group
3. The page will automatically appear in the sidebar

## Configuration

The `docs.json` file controls:

- Navigation structure
- Theme colors
- Topbar links and CTAs
- Footer social links

See [Mintlify Documentation](https://mintlify.com/docs) for full configuration options.

## Favicon

To update the favicon:

1. **Place your favicon file** in the `mintlify/` directory root:

   **Supported formats** (you can use any of these):

   - `.svg` - Scalable vector graphics (recommended for best quality)
   - `.png` - Portable Network Graphics (works great too)
   - `.ico` - Traditional favicon format (also supported)

   **Recommendation**: Use `.svg` for best quality and scalability, but `.png` and `.ico` work perfectly fine.

2. **Update `docs.json`** to point to your favicon file:

   ```json
   {
     "favicon": "/favicon.svg" // Use "/favicon.png" or "/favicon.ico" if preferred
   }
   ```

   You can name your file anything (e.g., `logo.svg`, `icon.png`) - just update the path in `docs.json` accordingly.

3. **Restart the dev server** to see changes:
   ```bash
   pnpm docs:dev
   ```

**Note**: The favicon path in `docs.json` should start with `/` and be relative to the `mintlify/` directory root.

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
- Customize colors and branding in `docs.json`
- Set up Mintlify Cloud deployment
- Add API reference documentation

## Troubleshooting

### "requires an internet connection" Error

The mint CLI requires internet access to download and run the preview server. If you see this error:

```
error running mint dev after updating requires an internet connection.
```

Make sure you have an active internet connection and try again. The mint CLI downloads resources on first run and when updates are available.

### Port Already in Use

If port 3000 is already in use, mint will automatically try the next available port (3001, 3002, etc.). Check the terminal output to see which port was selected.

### Cache Issues

If you experience unexpected behavior, try clearing the mint cache:

```bash
# Delete the mint cache directory
rm -rf ~/.mintlify

# Then run mint dev again
pnpm docs:dev
```

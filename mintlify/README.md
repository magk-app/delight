# Mintlify Documentation

This directory contains the Mintlify documentation for the Delight platform.

## Structure

```
mintlify/
├── docs.json              # Navigation configuration
├── introduction.mdx       # Landing page
├── quickstart.mdx         # Quick start guide
├── architecture/          # Architecture documentation (8 pages)
├── dev/                   # Development guides (4 pages)
├── epics/                 # Product epics (9 pages)
├── runbook/              # Operational runbooks (3 pages)
├── users/                # User guides (1 page)
├── logo/                 # Logo and favicon files
└── public/               # Public assets
```

**Total:** 27 MDX pages + 1 JSON config

## Quick Start

### Install Dependencies

```bash
# From project root
pnpm install
```

### Start Dev Server

**⚠️ Windows Users: See [Windows Setup](#-windows-users-critical-path-space-bug) below first!**

```bash
# Option 1: Use pnpm script (recommended)
pnpm docs:dev

# Option 2: Run directly
cd mintlify
npx --yes mint@latest dev
```

This starts the documentation at **http://localhost:3000**

### Verify All Pages Load

After starting the dev server, check:

- ✅ All tabs appear (Documentation, Product, Operations)
- ✅ All groups expand correctly
- ✅ No "page not found" errors
- ✅ All navigation links work

## 🚨 Windows Users: Critical Path Space Bug

**If you see this error on Windows:**

```
C:\Users\Jack:1
 ^^
SyntaxError: Invalid or unexpected token
```

**Root Cause**: The Mintlify CLI has a bug where it **cannot run** on Windows when your username contains a space (e.g., "Jack Luo" → `C:\Users\Jack Luo\`).

**Status**: This is an upstream bug in the `mint` package. See `WINDOWS-FIX-COMPLETE.md` for full analysis and `GITHUB-ISSUE-FOR-MINTLIFY.md` for the bug report.

### ✅ WORKING SOLUTION: Use WSL (Recommended)

**This is the only reliable solution that works consistently.**

#### Step 1: Install WSL (if not already installed)

```powershell
# In PowerShell (run as Administrator)
wsl --install

# Restart your computer if prompted
```

#### Step 2: Open WSL Terminal

- Windows 11: Open "Ubuntu" from Start Menu
- Windows 10: Open "Ubuntu" or "WSL" from Start Menu
- Or use Windows Terminal → select Ubuntu/Linux profile

#### Step 3: Navigate to Your Project

```bash
# Windows drives are mounted at /mnt/c/, /mnt/d/, etc.
cd /mnt/c/Users/Jack\ Luo/Desktop/\(local\)\ github\ software/delight
```

**Important**: Escape the space in your username with `\` (backslash)

#### Step 4: Run Mintlify

```bash
# Option A: Use pnpm scripts (from project root)
pnpm docs:dev

# Option B: Run directly (from mintlify directory)
cd mintlify
npx --yes mint@latest dev
```

#### Step 5: Open Browser

Navigate to **http://localhost:3000**

### 📋 Alternative Solutions (Not Recommended)

<details>
<summary>❌ Option: Use npx on Windows (DOES NOT WORK)</summary>

```bash
# This fails with the same error because the bug is in mint itself
cd mintlify
npx mint dev
# ❌ Still fails with SyntaxError
```

</details>

<details>
<summary>⚠️ Option: Change npm Global Prefix (Advanced)</summary>

Only attempt this if you understand Windows PATH configuration:

```bash
mkdir C:\npm-global
npm config set prefix C:\npm-global
# Add C:\npm-global to System Environment Variables → PATH
pnpm add -g mint
```

**Note**: This may still fail due to the mint CLI bug.

</details>

## Key Fix Applied

This implementation fixes the Mintlify "page not found" issues by:

✅ **Correct Navigation Structure**

- Uses `tabs → groups → pages` hierarchy (not `tabs → pages`)
- This was the primary cause of page not found errors

✅ **Proper File Extensions**

- All files are `.mdx` (Mintlify requirement)
- No `.md` files that Mintlify can't find

✅ **Correct docs.json**

- Page references don't include `.mdx` extension
- Uses latest schema: `https://mintlify.com/docs.json`
- Proper structure matches working examples

## Navigation Structure

### Documentation Tab

- **Get Started** - Introduction, Quickstart
- **Architecture** - 8 architecture pages
- **Development** - 4 development guides

### Product Tab

- **Epics** - 9 epic pages (overview + epic-1 through epic-8)
- **User Guide** - Getting started guide

### Operations Tab

- **Runbooks** - Documentation, deployment, troubleshooting

## Available Commands

- `pnpm docs:dev` - Start the Mintlify development server with hot reload
- `pnpm docs:lint` - Lint the documentation for errors
- `pnpm docs:deploy` - Deploy documentation to Mintlify Cloud (requires API key)

## Deployment

Documentation is automatically deployed when changes are pushed to main branch.

**To deploy:**

1. Make changes to MDX files
2. Test locally with `pnpm docs:dev`
3. Commit and push to repository
4. Mintlify automatically rebuilds and deploys

## Adding New Pages

<details>
<summary>Step-by-step guide</summary>

1. **Create the MDX file**

   ```bash
   touch mintlify/section/new-page.mdx
   ```

2. **Add frontmatter**

   ```mdx
   ---
   title: "Your Page Title"
   description: "Brief description"
   ---

   # Your Content
   ```

3. **Update docs.json**
   Add to the appropriate group:

   ```json
   {
     "group": "Section Name",
     "pages": ["section/existing-page", "section/new-page"]
   }
   ```

4. **Test locally**
   ```bash
   pnpm docs:dev
   ```

</details>

## Configuration

The `docs.json` file controls:

- Navigation structure
- Theme colors
- Topbar links and CTAs
- Footer social links

See [Mintlify Documentation](https://mintlify.com/docs) for full configuration options.

## Favicon

To update the favicon:

1. **Place your favicon file** in the `mintlify/logo/` directory:

   **Supported formats** (you can use any of these):

   - `.svg` - Scalable vector graphics (recommended for best quality)
   - `.png` - Portable Network Graphics (works great too)
   - `.ico` - Traditional favicon format (also supported)

   **Recommendation**: Use `.svg` for best quality and scalability, but `.png` and `.ico` work perfectly fine.

2. **Update `docs.json`** to point to your favicon file:

   ```json
   {
     "favicon": "/logo/favicon.ico" // Use "/logo/favicon.svg" or "/logo/favicon.png" if preferred
   }
   ```

   You can name your file anything (e.g., `logo.svg`, `icon.png`) - just update the path in `docs.json` accordingly.

3. **Restart the dev server** to see changes:
   ```bash
   pnpm docs:dev
   ```

**Note**: The favicon path in `docs.json` should start with `/` and be relative to the `mintlify/` directory root.

## Images

All documentation images should be placed in the `mintlify/images/` directory (create it if it doesn't exist).

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

## Mintlify Components Used

This documentation uses Mintlify's rich component library:

- `<Card>` & `<CardGroup>` - Visual organization
- `<Info>`, `<Warning>`, `<Tip>`, `<Note>` - Callouts
- `<Steps>` & `<Step>` - Step-by-step guides
- `<Checks>` & `<Check>` - Checklists
- `<Accordion>` & `<AccordionGroup>` - Collapsible sections
- `<CodeGroup>` - Multi-language code examples
- `<Tabs>` & `<Tab>` - Tabbed content

See [Mintlify Components Docs](https://mintlify.com/docs/content/components) for full reference.

## File Naming Conventions

- Use `.mdx` extension (not `.md`)
- Use lowercase with hyphens: `my-page.mdx`
- No spaces in filenames
- Match filename to page topic

## Content Guidelines

- Add descriptive frontmatter to every page
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code examples with language identifiers
- Add navigation links between related pages
- Use Mintlify components for better UX

## Troubleshooting

### "Page not found" errors

✅ **Already fixed!** This implementation uses:

- Correct `tabs → groups → pages` structure
- `.mdx` file extensions
- Proper path references in docs.json

### Dev server not starting

```bash
# Clear cache
rm -rf node_modules .mintlify
npm install -g mintlify@latest

# Restart
pnpm docs:dev
```

### Navigation not updating

After changing docs.json:

1. Stop the dev server (Ctrl+C)
2. Restart with `pnpm docs:dev`
3. Hard refresh browser (Ctrl+Shift+R)

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

### Windows Path Space Bug

See [Windows Setup](#-windows-users-critical-path-space-bug) section above for the WSL workaround.

## Resources

- **Mintlify Docs:** https://mintlify.com/docs
- **Component Reference:** https://mintlify.com/docs/content/components
- **Navigation Guide:** https://mintlify.com/docs/settings/navigation
- **Deployment Guide:** https://mintlify.com/docs/development

---

**Last Updated:** 2025-01-17  
**Maintained By:** Delight Team

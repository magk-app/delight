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

### 🚨 Windows Users: Critical Path Space Bug

**If you see this error on Windows:**
```
C:\Users\Jack:1
 ^^
SyntaxError: Invalid or unexpected token
```

**Root Cause**: The Mintlify CLI has a bug where it **cannot run** on Windows when your username contains a space (e.g., "Jack Luo" → `C:\Users\Jack Luo\`).

**Status**: This is an upstream bug in the `mint` package. See `WINDOWS-FIX-COMPLETE.md` for full analysis and `GITHUB-ISSUE-FOR-MINTLIFY.md` for the bug report.

---

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

---

### 📋 Alternative Solutions (Not Recommended)

**These may NOT work due to the mint CLI bug:**

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

---

### ✅ Verification

After setup, confirm it works:

```bash
# From WSL
cd /mnt/c/Users/Jack\ Luo/Desktop/\(local\)\ github\ software/delight
pnpm docs:dev
```

**Expected output**:
```
✔ Local: http://localhost:3000
```

Then open your browser to http://localhost:3000 and verify the docs load.

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

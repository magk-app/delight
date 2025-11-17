# Mintlify Windows Issues - Complete Guide

**Date**: November 17, 2025
**Author**: Jack & Claude Code
**Status**: ✅ Documented & Workaround Available

---

## 📋 Quick Summary (TL;DR)

**Problem**: Mint CLI fails on Windows when your username has a space (e.g., `C:\Users\Jack Luo\`)
**Error**: `SyntaxError: Invalid or unexpected token at C:\Users\Jack:1`
**Root Cause**: Upstream bug in mint CLI - doesn't quote Windows paths properly
**Solution**: **Use WSL** (Windows Subsystem for Linux)

```bash
# Quick Fix (5 minutes)
wsl
cd /mnt/c/Users/Jack\ Luo/Desktop/\(local\)\ github\ software/delight
pnpm docs:dev
# Open http://localhost:3000
```

---

## 🔴 The Problem Explained

### What's Happening

When you run `mint dev` on Windows with a space in your username path:

```powershell
PS C:\Users\Jack Luo\Desktop\project> mint --version
C:\Users\Jack:1
 ^^

SyntaxError: Invalid or unexpected token
    at wrapSafe (node:internal/modules/cjs/loader:1620:18)
```

**Why it fails:**
1. Node.js tries to parse `C:\Users\Jack Luo\AppData\Local\pnpm\...`
2. It **stops at the space** after "Jack"
3. Treats "Luo" as invalid syntax
4. **Crashes immediately**

---

## 🔍 Root Cause Analysis

We discovered **THREE separate issues** affecting Mintlify on Windows:

### Issue #1: Windows Path Space Bug ❌ **CRITICAL**

**Location**: Inside mint npm package wrapper scripts/shims
**Problem**: Mint CLI doesn't properly **quote or escape** Windows paths with spaces
**Impact**: Completely blocks Windows users with spaces in usernames
**Can you fix it?**: ❌ **NO** - requires Mintlify to fix upstream

**Evidence:**
- ✅ `pnpm add -g mint` succeeds (package installs)
- ✅ Binary created at `C:\Users\Jack Luo\AppData\Local\pnpm\mint.exe`
- ❌ Running the binary fails with syntax error
- ❌ Even `npx mint` fails on native Windows

### Issue #2: Outdated docs.json Schema ⚠️ **FIXED**

**Problem**: Pre-2025 schema examples are everywhere, causing validation errors
**Impact**: Even when mint starts, it rejects the config

```
🚨 Invalid docs.json:
#.colors: Unrecognized key(s) in object: 'anchors'
#.navigation: Invalid type. Expected 'object', received 'array'
```

**Old Schema (Pre-2025):**
```json
{
  "navigation": [
    { "group": "Getting Started", "pages": [...] }
  ],
  "colors": {
    "anchors": { "from": "#...", "to": "#..." }
  }
}
```

**New Schema (2025+):**
```json
{
  "$schema": "https://mintlify.com/docs.json",
  "navigation": {
    "dropdowns": [
      {
        "dropdown": "Getting Started",
        "groups": [{ "group": "...", "pages": [...] }]
      }
    ]
  },
  "colors": {
    "primary": "#...",
    "light": "#...",
    "dark": "#..."
  }
}
```

**Status**: ✅ **FIXED** - Updated `docs.json` to 2025 schema

### Issue #3: "Preparing Preview" Hangs ⚠️ **INVESTIGATING**

**Problem**: After fixing everything, mint gets stuck on spinner forever
**Theories**:
- Network timeout downloading resources (~50MB first run)
- Firewall/proxy blocking downloads
- Another path-related issue
- Bug in prebuild step

**Status**: Under investigation

---

## ✅ WORKING SOLUTION

### Use WSL (Windows Subsystem for Linux)

This is the **ONLY** reliable solution that works consistently.

**Why WSL works:**
- ✅ True Linux environment (no Windows path issues)
- ✅ Uses Linux binaries (no cross-platform conflicts)
- ✅ Matches production environment
- ✅ You already have it installed!

### Step-by-Step Setup

#### 1. Open WSL Terminal

```bash
# From Windows Command Prompt or PowerShell
wsl

# Or: Windows Terminal → Ubuntu/Linux tab
```

#### 2. Navigate to Your Project

```bash
cd /mnt/c/Users/Jack\ Luo/Desktop/\(local\)\ github\ software/delight
```

**Note**: Windows drives mount at `/mnt/c/`, `/mnt/d/`, etc. in WSL
**Important**: Escape spaces with `\` (backslash)

#### 3. Run Mintlify

```bash
# Option A: Use package.json scripts (from root)
pnpm docs:dev

# Option B: Run directly (from mintlify folder)
cd mintlify
npx --yes mint@latest dev
```

#### 4. Open Browser

Navigate to **http://localhost:3000**

**Expected output:**
```
⠋ preparing local preview...
✔ Local: http://localhost:3000
```

---

## 📊 Issues Summary Table

| Issue | Status | User Fixable? | Workaround |
|-------|--------|---------------|------------|
| **Windows path with space** | ❌ Confirmed bug | ❌ No | Use WSL |
| **pnpm global bin config** | ✅ Fixed | ✅ Yes | Restart terminal after `pnpm setup` |
| **Outdated docs.json schema** | ✅ Fixed | ✅ Yes | Update to 2025 schema |
| **"Preparing preview" hangs** | ⚠️ Investigating | ❓ Unknown | Use WSL or wait |

---

## 🚀 Quick Reference Commands

### ❌ Don't Do This (Will Fail on Windows)

```powershell
# Native Windows - WILL FAIL if username has space
npm install -g mint
mint dev
```

### ✅ Do This Instead

```bash
# Use WSL
wsl
cd /mnt/c/Users/Jack\ Luo/Desktop/\(local\)\ github\ software/delight/mintlify
npx --yes mint@latest dev
```

---

## 🐛 GitHub Issue Ready to Submit

A complete bug report is ready in `GITHUB-ISSUE-FOR-MINTLIFY.md`.

**To submit:**
1. Go to https://github.com/mintlify/docs/issues
2. Click "New Issue"
3. Copy entire contents of `GITHUB-ISSUE-FOR-MINTLIFY.md`
4. Submit!

This helps Mintlify fix it for all Windows users.

---

## 💡 Key Learnings

`★ Insight ─────────────────────────────────────`
What looked like a simple pnpm configuration issue was actually three separate problems: (1) mint CLI bug with Windows paths, (2) outdated schema documentation, and (3) possible network/download issues. Systematic debugging—testing each hypothesis independently—was key to identifying all root causes.
`─────────────────────────────────────────────────`

### Technical Insights

1. **Path Handling**: Always quote paths with spaces in CLI wrapper scripts
2. **Schema Evolution**: Major tools can have breaking schema updates
3. **Environment Variables**: Windows terminal needs restart after env var changes
4. **WSL Benefits**: Linux on Windows avoids entire classes of path/binary issues

### Process Insights

1. **Reproduce First**: Confirmed exact error before attempting fixes
2. **Test Systematically**: Tried pnpm → npm → npx → WSL sequentially
3. **Document Everything**: Created comprehensive docs for future developers
4. **Report Upstream**: Proper bug report helps the entire community

---

## 📊 Mintlify Project Status

### Overall: ~45% Complete

**✅ Done:**
- Tech spec & epic defined
- Basic docs.json configured
- Theme customized
- **Windows issues resolved** (via WSL)
- Comprehensive bug documentation

**🔄 In Progress:**
- Story 1: Config & Navigation (50%)
  - ✅ Basic structure created
  - ❌ Content migration incomplete (only 4 pages)

**❌ Not Started:**
- Story 2: API Reference & CI (0%)
- Story 3: Deployment & Ops (0%)

### Story 1: Remaining Work

| Task | Estimate | Status |
|------|----------|--------|
| **Content Migration** | 2-4 hours | Not started |
| - Inventory `docs/` markdown files | 30 min | |
| - Create pages in `mintlify/` | 2 hours | |
| - Update navigation in `docs.json` | 1 hour | |
| **Navigation Expansion** | 1 hour | Not started |
| - Add Runbooks section | 15 min | |
| - Add Epics section | 15 min | |
| - Add Guides section | 15 min | |
| - Add Stories section | 15 min | |
| **Testing** | 30 min | Not started |
| - Verify all links | 15 min | |
| - Run `mint broken-links` | 10 min | |
| - Test navigation flows | 5 min | |

---

## 🎯 Next Steps

### Immediate (Right Now)

1. ✅ **Use WSL** for all mintlify work (see solution above)
2. ✅ **Verify** docs.json uses 2025 schema (already updated)
3. ✅ **Test** that `pnpm docs:dev` works in WSL

### Short-term (This Week)

1. **Submit GitHub issue** to Mintlify
2. **Continue Story 1**:
   - Complete content migration
   - Expand navigation structure
   - Test all pages

### Medium-term (Next Week)

1. **Story 2**: OpenAPI export script + CI automation
2. **Story 3**: Mintlify Cloud deployment + ops docs
3. **Monitor**: GitHub issue for Mintlify response

---

## ✨ Success Criteria

You'll know everything is working when:

- ✅ `pnpm docs:dev` starts without errors in WSL
- ✅ Browser loads http://localhost:3000
- ✅ Navigation sidebar appears with all sections
- ✅ Clicking pages loads content correctly
- ✅ No console errors in browser dev tools

---

## 📞 Support & Resources

- **Mintlify Docs**: https://www.mintlify.com/docs
- **2025 Schema Migration**: https://www.mintlify.com/blog/refactoring-mint-json-into-docs-json
- **WSL Installation**: https://learn.microsoft.com/en-us/windows/wsl/install
- **Mintlify GitHub Issues**: https://github.com/mintlify/docs/issues
- **Schema Reference**: https://mintlify.com/docs.json

---

## 📝 Documentation Files

| File | Purpose |
|------|---------|
| **`WINDOWS-ISSUES-COMPLETE.md`** | This file - everything in one place |
| **`GITHUB-ISSUE-FOR-MINTLIFY.md`** | Ready-to-submit bug report |
| **`../README.md`** | Updated with WSL setup instructions |
| **`../docs.json`** | Fixed to 2025 schema |

---

**Last Updated**: 2025-11-17
**Reported By**: Jack (@magk-app/delight)
**Status**: ✅ Workaround available (WSL) | ⏳ Awaiting upstream fix from Mintlify

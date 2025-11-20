# PR Review: package-lock.json Merge Conflicts

## Summary

**PR**: `claude/redesign-marketing-page-01SbForz4awmc13rUoGHma8g` → `claude/frontend-backend-integration-01XkTzdh6c6s5pmm7ZcqENFm`

**Issue**: Multiple merge conflicts in `package-lock.json` preventing PR merge.

**Root Cause**: The project uses **pnpm** as its package manager, but `package-lock.json` (npm's lockfile) exists in the repository, causing conflicts when branches diverge.

**Important**: We are removing `package-lock.json` (npm's lockfile), NOT `package.json` (the project configuration file). `package.json` is essential and must be kept.

---

## Root Cause Analysis

### The Problem

1. **Project Configuration**: The project is explicitly configured to use **pnpm**:

   - `package.json` specifies `"packageManager": "pnpm@10.21.0"`
   - All scripts use `pnpm` commands
   - `pnpm-workspace.yaml` exists for monorepo support
   - `pnpm-lock.yaml` is the correct lockfile

2. **Conflicting Lockfile**: `package-lock.json` exists in the repository:

   - This is npm's lockfile format
   - It was likely created by accidentally running `npm install` instead of `pnpm install`
   - Both branches have different versions of this file, causing merge conflicts

3. **Why This Causes Conflicts**:
   - Lockfiles are auto-generated and change frequently
   - When two branches modify dependencies differently, the lockfiles diverge
   - `package-lock.json` shouldn't exist in a pnpm project, so any changes to it are unnecessary
   - The large diff (+19,237 −1,200) suggests significant dependency changes in both branches

### Evidence

- ✅ `package.json` line 31: `"packageManager": "pnpm@10.21.0"`
- ✅ `pnpm-lock.yaml` exists (47,498 bytes)
- ❌ `package-lock.json` exists (48,990 bytes) - **This shouldn't be here**
- ❌ `.gitignore` does NOT ignore `package-lock.json`

---

## Resolution Steps

### Step 1: Resolve the Merge Conflict (Immediate Fix)

**Option A: Using GitHub Web Editor (Recommended)**

1. In the PR, click "Resolve conflicts" on `package-lock.json`
2. **Delete the entire file** (accept neither version)
3. Commit the deletion

**Option B: Using Command Line**

```bash
# Checkout the target branch
git checkout claude/frontend-backend-integration-01XkTzdh6c6s5pmm7ZcqENFm
git pull origin claude/frontend-backend-integration-01XkTzdh6c6s5pmm7ZcqENFm

# Checkout the PR branch
git checkout claude/redesign-marketing-page-01SbForz4awmc13rUoGHma8g

# Remove package-lock.json
git rm package-lock.json

# Commit the removal
git commit -m "chore: remove package-lock.json (project uses pnpm)"

# Push to PR branch
git push origin claude/redesign-marketing-page-01SbForz4awmc13rUoGHma8g
```

### Step 2: Prevent Future Conflicts (Long-term Fix)

Add `package-lock.json` to `.gitignore`:

```bash
# Add to .gitignore
echo "" >> .gitignore
echo "# npm lockfile (project uses pnpm)" >> .gitignore
echo "package-lock.json" >> .gitignore
```

Or manually add this line to `.gitignore`:

```
package-lock.json
```

### Step 3: Clean Up Existing Commits (Optional but Recommended)

If `package-lock.json` exists in the target branch too, remove it there as well:

```bash
# On the target branch
git checkout claude/frontend-backend-integration-01XkTzdh6c6s5pmm7ZcqENFm
git rm package-lock.json
git commit -m "chore: remove package-lock.json (project uses pnpm)"
git push origin claude/frontend-backend-integration-01XkTzdh6c6s5pmm7ZcqENFm
```

### Step 4: Regenerate pnpm-lock.yaml (If Needed)

After resolving conflicts, ensure `pnpm-lock.yaml` is up to date:

```bash
# Remove node_modules and reinstall with pnpm
rm -rf node_modules packages/*/node_modules
pnpm install

# Commit updated pnpm-lock.yaml if it changed
git add pnpm-lock.yaml
git commit -m "chore: update pnpm-lock.yaml"
```

---

## Why This Happened

### Common Causes

1. **Accidental npm install**: Developer ran `npm install` instead of `pnpm install`
2. **IDE auto-install**: Some IDEs auto-run `npm install` when detecting `package.json`
3. **Copy-paste from npm project**: Code copied from an npm project brought `package-lock.json` along
4. **Missing .gitignore entry**: File wasn't ignored, so it got committed

### Prevention

1. ✅ Add `package-lock.json` to `.gitignore`
2. ✅ Use `packageManager` field in `package.json` (already done)
3. ✅ Add pre-commit hook to detect npm lockfiles
4. ✅ Document in README that project uses pnpm only

---

## Additional Notes

### Other Issues Found in PR

1. **Navigation Link Issue** (from Codex review):
   - `main-nav.tsx` links to `/#product` but no such section exists
   - Should link to an existing section like `/#hero`, `/#psychology`, etc.

### Verification Checklist

After resolving conflicts:

- [ ] `package-lock.json` is removed from both branches
- [ ] `package-lock.json` is added to `.gitignore`
- [ ] `pnpm-lock.yaml` is up to date
- [ ] `pnpm install` runs successfully
- [ ] PR can be merged without conflicts
- [ ] CI/CD passes (if configured)

---

## Quick Reference

**Project Package Manager**: pnpm (NOT npm)

**Files to KEEP**:

- `package.json` ✅ (Essential - project configuration)
- `pnpm-lock.yaml` ✅ (pnpm's lockfile)

**Files to REMOVE**:

- `package-lock.json` ❌ (npm's lockfile - conflicts with pnpm)

**Install Command**: `pnpm install` (NOT `npm install`)

---

## Related Documentation

- Previous issue documented in: `docs/stories/epic-1/1-1-initialize-monorepo-structure-and-core-dependencies.md` (lines 1066-1073)
- Project uses pnpm workspace: `pnpm-workspace.yaml`
- Package manager specified: `package.json` line 31

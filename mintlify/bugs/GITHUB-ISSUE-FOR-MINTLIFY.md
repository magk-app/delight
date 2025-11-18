# Bug Report: Mint CLI Fails on Windows with Spaces in Username

## 🐛 Bug Description

The `mint` CLI completely fails to execute on Windows systems when the user's Windows username contains a space (e.g., "John Doe" → `C:\Users\John Doe\`).

## 📋 Environment

- **OS**: Windows 10/11
- **Node Version**: v22.18.0
- **mint CLI Version**: 4.2.202 (latest)
- **Package Manager**: pnpm 10.21.0 / npm 10.x
- **Installation Method**: Global install (`pnpm add -g mint` / `npm install -g mint`)

## 🔄 Steps to Reproduce

1. Use a Windows system with a username containing a space:
   - Example: `C:\Users\Jack Luo\`

2. Install mint CLI globally:
   ```powershell
   pnpm add -g mint
   # OR
   npm install -g mint
   ```

3. Try to run any mint command:
   ```powershell
   mint --version
   # OR
   mint dev
   ```

4. **Observe error**:
   ```
   C:\Users\Jack:1
   [45F0:5078][2024-10-09T10:03:28]i001: Burn v3.14.1.8722...
    ^^

   SyntaxError: Invalid or unexpected token
       at wrapSafe (node:internal/modules/cjs/loader:1620:18)
       at Module._compile (node:internal/modules/cjs/loader:1662:20)
       at Object..js (node:internal/modules/cjs/loader:1820:10)
   ```

## ✅ Expected Behavior

The mint CLI should execute successfully regardless of Windows username/path structure, just like other Node.js CLI tools (npm, npx, pnpm, etc.) handle paths with spaces correctly.

## ❌ Actual Behavior

- **Installation succeeds**: `pnpm add -g mint` completes without errors
- **Binary created**: `C:\Users\Jack Luo\AppData\Local\pnpm\mint.exe` exists
- **Execution fails**: Node.js cannot parse the path due to the space
- **Error location**: Stops at space character: `C:\Users\Jack:1` (colon after "Jack" indicates parser stopped there)

## 🔍 Root Cause Analysis

The mint CLI wrapper scripts or shims don't properly **quote or escape** Windows paths containing spaces. When Node.js attempts to execute the mint binary, it fails to parse the path:

```javascript
// What's happening (simplified)
const mintPath = C:\Users\Jack Luo\AppData\Local\pnpm\mint.exe
//                           ^ Parser stops at space, treats "Luo" as syntax error
```

## 🧪 Additional Testing

### Test 1: Global Install via pnpm
```powershell
PS C:\Users\Jack Luo> pnpm add -g mint
✅ SUCCESS: Packages: +830, done in 22.7s

PS C:\Users\Jack Luo> mint --version
❌ FAIL: SyntaxError: Invalid or unexpected token at C:\Users\Jack:1
```

### Test 2: Using npx (also fails)
```powershell
PS C:\Users\Jack Luo\project\mintlify> npx mint dev
❌ FAIL: Same SyntaxError
```

### Test 3: WSL Workaround (works!)
```bash
$ wsl
$ cd /mnt/c/Users/Jack\ Luo/project/mintlify
$ npx mint@latest dev
✅ SUCCESS: Downloads mint and runs successfully
```

## 💥 Impact

**High Severity**:
- ❌ Completely blocks Windows users with spaces in usernames
- ❌ No workaround on native Windows (even npx fails)
- ⚠️ Forces users to either:
  1. Use WSL (requires additional setup)
  2. Rename Windows user account (destructive, breaks many things)
  3. Create Windows junction to space-free path (advanced, requires admin)

**Affected Users**:
- Anyone with a two-word name: "John Doe", "Jane Smith", "Jack Luo", etc.
- Corporate environments with naming conventions: "FirstName LastName"
- Very common scenario - likely affects **thousands of Windows users**

## 🔧 Suggested Fix

Ensure all path references in mint wrapper scripts are properly quoted. Example fix locations:

**Possible locations** (haven't inspected source, but likely culprits):
- Binary wrapper/shim generation
- Path resolution for Node.js execution
- Any hardcoded path strings

**Example fix**:
```javascript
// ❌ BAD - No quotes
const command = `node ${mintPath} ${args}`;

// ✅ GOOD - Properly quoted
const command = `node "${mintPath}" ${args}`;
```

**Also check**:
- PowerShell script wrappers (`.ps1` files)
- Batch file wrappers (`.cmd` files)
- Node.js shims

## ✅ Current Workaround

**For affected Windows users**:

```bash
# Install WSL
wsl --install

# Navigate to project (Windows drives mount at /mnt/)
cd /mnt/c/Users/Jack\ Luo/project/mintlify

# Run mint via npx in WSL
npx --yes mint@latest dev
```

**Update package.json** to always use npx in WSL:
```json
{
  "scripts": {
    "docs:dev": "cd mintlify && npx mint@latest dev",
    "docs:lint": "cd mintlify && npx mint@latest broken-links"
  }
}
```

## 📚 Related Issues

- This is similar to path handling bugs that affected other Node.js CLIs in the past
- Likely affects **all mint CLI commands** (`dev`, `lint`, `deploy`, etc.)
- May also affect users with other special characters in paths

## 🙏 Request

Please prioritize this fix as it blocks a significant portion of Windows users. The fix should be straightforward (adding proper path quoting), and would greatly improve the Windows development experience.

---

**Additional Context**:
- We spent several hours debugging this before identifying the root cause
- Initially thought it was pnpm configuration, but verified it's a mint CLI bug
- Happy to provide additional testing or information if needed

**Thank you for maintaining Mintlify!** 🚀

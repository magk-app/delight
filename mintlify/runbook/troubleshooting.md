# Runbook: Troubleshooting Mintlify Documentation

## Purpose
Diagnose and resolve common issues when working with Delight's Mintlify documentation site, covering local development, deployment, and content problems.

---

## Local Development Issues

### mint CLI Not Found

**Symptom**:
```bash
$ pnpm docs:dev
mint: command not found
```

**Cause**: mint package not installed or not in PATH

**Solutions**:

1. **Install dependencies**:
   ```bash
   pnpm install
   ```

2. **Use npx** (bypasses PATH issues):
   ```bash
   cd mintlify
   npx mint dev
   ```

3. **Install globally** (alternative):
   ```bash
   pnpm add -g mint
   ```

### Windows: SyntaxError on Startup

**Symptom**:
```
SyntaxError: Invalid or unexpected token
at wrapSafe (node:internal/modules/cjs/loader:1620:18)
```

**Cause**: Windows username contains spaces (e.g., "Jack Luo"), breaking Node.js path parsing

**Solutions** (in order of preference):

**Option 1: Use npx** (Recommended)
```bash
cd mintlify
npx mint dev
```

**Option 2: Use WSL**
```bash
wsl --install
# After WSL is installed:
cd /mnt/c/Users/Jack\ Luo/Desktop/delight
pnpm docs:dev
```

**Option 3: Change npm Global Prefix**
```bash
mkdir C:\npm-global
npm config set prefix C:\npm-global
# Add C:\npm-global to System PATH variable
pnpm add -g mint
```

See [README.md Windows section](/mintlify/README.md#windows-users-username-with-spaces-issue) for details.

### Requires Internet Connection Error

**Symptom**:
```
error running mint dev after updating requires an internet connection.
```

**Cause**: mint CLI downloads resources on first run and updates

**Solutions**:

1. **Check internet connection**: Ensure active network connectivity

2. **Check firewall**: Verify mint CLI isn't blocked by firewall

3. **Use VPN**: If corporate network blocks downloads, try VPN

4. **Wait and retry**: Temporary network issues may resolve automatically

### Port Already in Use

**Symptom**:
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Cause**: Another process is using port 3000

**Solutions**:

1. **Auto-select next port**: mint usually auto-selects 3001, 3002, etc.
   - Check terminal output for actual port: `Server running on http://localhost:3001`

2. **Kill process using port 3000**:
   ```bash
   # Mac/Linux
   lsof -ti:3000 | xargs kill -9

   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

3. **Specify custom port**:
   ```bash
   npx mint dev --port 3001
   ```

### Hot Reload Not Working

**Symptom**: Changes to `.md` files don't appear in browser

**Solutions**:

1. **Hard refresh browser**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

2. **Restart dev server**: Stop (`Ctrl+C`) and restart `pnpm docs:dev`

3. **Check file watcher limits** (Linux):
   ```bash
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

4. **Clear mint cache**:
   ```bash
   rm -rf ~/.mintlify
   pnpm docs:dev
   ```

---

## Content & Navigation Issues

### Missing Page in Sidebar

**Symptom**: New `.md` file doesn't appear in navigation

**Cause**: File not added to `docs.json` navigation

**Solution**:

1. **Add to docs.json**:
   ```json
   {
     "group": "Development",
     "pages": [
       "dev/setup",
       "dev/new-guide"  // Add your new file here
     ]
   }
   ```

2. **Verify file path**: Ensure path in `docs.json` matches actual file location
   - ❌ `dev/new-guide.md` (don't include `.md` extension)
   - ✅ `dev/new-guide`

3. **Restart dev server**: `Ctrl+C` and `pnpm docs:dev`

### Broken Internal Links

**Symptom**: Clicking link shows 404 or broken page

**Cause**: Link path doesn't match file structure

**Solutions**:

1. **Use correct link format**:
   ```markdown
   ❌ [Setup](dev/setup.md)
   ❌ [Setup](./dev/setup)
   ✅ [Setup](/dev/setup)
   ```
   Links should be absolute paths starting with `/`

2. **Run link validator**:
   ```bash
   pnpm docs:lint
   ```
   This catches broken links before deployment

3. **Check file exists**: Verify target file is in `mintlify/` directory

### Images Not Displaying

**Symptom**: Broken image icons or missing images

**Causes & Solutions**:

**Cause 1: Wrong path**
```markdown
❌ ![Diagram](./images/diagram.png)
✅ ![Diagram](/images/diagram.png)
```

**Cause 2: File not committed**
```bash
git add mintlify/images/diagram.png
git commit -m "docs: add architecture diagram"
```

**Cause 3: Case sensitivity** (Linux/Mac vs Windows)
- File: `Diagram.png`
- Reference: `![Diagram](/images/diagram.png)` ❌
- Fix: Rename file to `diagram.png` to match

### Code Blocks Not Highlighting

**Symptom**: Code appears as plain text without syntax colors

**Cause**: Missing or incorrect language tag

**Solution**:

```markdown
❌
```
pnpm install
```

✅
```bash
pnpm install
```
```

Supported languages: `bash`, `javascript`, `typescript`, `python`, `json`, `yaml`, `sql`, `tsx`, `jsx`, `markdown`

---

## Deployment Issues

### Build Failing in Mintlify Cloud

**Symptom**: Mintlify deployment fails with build error

**Debugging Steps**:

1. **Check build logs**:
   - Mintlify Dashboard → Deployments → Select failed deployment → View Logs

2. **Test locally first**:
   ```bash
   pnpm docs:lint
   pnpm docs:dev
   # Navigate through all pages to verify
   ```

3. **Common causes**:
   - **Invalid docs.json**: Validate JSON syntax
     ```bash
     cat mintlify/docs.json | jq .
     ```
   - **Missing files**: Navigation references non-existent file
   - **Malformed frontmatter**: Check YAML at top of `.md` files
   - **Circular references**: Page links to itself

4. **Fix and redeploy**:
   ```bash
   git commit -m "fix: resolve build error"
   git push origin main
   ```

### Preview Deployment Not Created

**Symptom**: PR doesn't get preview deployment comment

**Solutions**:

1. **Check PR has docs changes**:
   - Preview only triggers if `mintlify/` files are modified

2. **Verify GitHub App permissions**:
   - GitHub repo → Settings → Integrations → Mintlify
   - Ensure read/write access granted

3. **Check Mintlify settings**:
   - Dashboard → Settings → Previews
   - Enable "Deploy previews for pull requests"

4. **Manually trigger**:
   ```bash
   cd mintlify
   npx mint deploy --preview
   ```

### Custom Domain SSL Error

**Symptom**: `https://docs.delight.so` shows SSL certificate error

**Solutions**:

1. **Wait for DNS propagation**: Can take 1-48 hours after DNS changes

2. **Verify DNS record**:
   ```bash
   dig docs.delight.so CNAME
   # Should return: cname.mintlify.com
   ```

3. **Re-verify in Mintlify**:
   - Dashboard → Settings → Custom Domain → "Re-verify"

4. **Check Mintlify status**: https://status.mintlify.com

5. **Contact support**: If SSL doesn't provision after 48 hours

---

## Performance Issues

### Slow Page Loads

**Symptoms**: Documentation site takes >3 seconds to load

**Solutions**:

1. **Optimize images**:
   - Use compressed formats (WebP, optimized PNG)
   - Max recommended size: 500KB per image
   - Tools: TinyPNG, ImageOptim, Squoosh

2. **Reduce page size**:
   - Split large pages into multiple smaller pages
   - Use accordions for lengthy sections
   - Move reference content to separate pages

3. **Check CDN**: Mintlify uses CDN, verify it's working:
   - Inspect network tab in browser dev tools
   - Check `CF-Cache-Status` header (Cloudflare)

4. **Clear browser cache**: Hard refresh page

### Search Not Working

**Symptom**: Search bar returns no results or incorrect results

**Solutions**:

1. **Wait for indexing**: Search index updates after deployment (~5 minutes)

2. **Rebuild search index**:
   - Mintlify Dashboard → Settings → Search → "Rebuild Index"

3. **Check content format**:
   - Search works best with proper headings (`#`, `##`, `###`)
   - Use descriptive titles and summaries

4. **Test different keywords**: Try synonyms or related terms

---

## Cache Issues

### Stale Content Showing

**Symptom**: Updates deployed but old content still visible

**Solutions**:

1. **Clear browser cache**:
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or open in incognito/private window

2. **Clear mint local cache**:
   ```bash
   rm -rf ~/.mintlify
   pnpm docs:dev
   ```

3. **Purge CDN cache**:
   - Mintlify Dashboard → Deployments → Select latest → "Purge Cache"
   - Or redeploy: "Redeploy"

4. **Verify deployment**:
   - Check deployment timestamp in dashboard
   - Compare with git commit time

---

## Getting Help

### Self-Service Resources

1. **Mintlify Documentation**: https://mintlify.com/docs
2. **GitHub Issues**: https://github.com/magk-app/delight/issues
3. **Internal Runbooks**:
   - [Documentation Operations](/runbook/documentation)
   - [Deployment Procedures](/runbook/deployment)

### Escalation Path

1. **Check existing issues**: Search GitHub issues for similar problems
2. **Create new issue**: Include:
   - Error message (full text)
   - Steps to reproduce
   - Environment (OS, Node version, browser)
   - Screenshots if applicable

3. **Contact Mintlify Support**:
   - Email: support@mintlify.com
   - Include: Account details, deployment logs, error screenshots

### Debug Checklist

Before asking for help, try:

- [ ] Run `pnpm docs:lint` locally
- [ ] Check browser console for errors (F12)
- [ ] Verify issue reproduces in clean environment
- [ ] Review recent changes with `git log mintlify/`
- [ ] Test in incognito/private browser window
- [ ] Check Mintlify status page: https://status.mintlify.com
- [ ] Review build logs in Mintlify Dashboard

---

**Last Updated**: 2025-11-13
**Document Owner**: Delight Platform Team

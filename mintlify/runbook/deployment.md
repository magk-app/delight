# Runbook: Mintlify Deployment

## Purpose
Document the process for deploying Delight documentation to Mintlify Cloud, including setup, configuration, deployment procedures, and rollback strategies.

## Deployment Architecture

### Components
- **Source**: Markdown files in `mintlify/` directory
- **Build**: Mintlify Cloud build service
- **Hosting**: Mintlify Cloud CDN
- **Integration**: GitHub repository connection
- **DNS**: Custom domain (when configured)

### Deployment Flow
```
Git Push → GitHub → Mintlify Cloud → Build → Deploy → CDN
```

## Prerequisites

### Required Access
- GitHub repository admin access
- Mintlify Cloud account
- Domain DNS admin access (for custom domain)

### Environment Setup
1. **Mintlify API Key** (for CLI deployments):
   ```bash
   export MINTLIFY_API_KEY="your-api-key-here"
   ```
   Get from: Mintlify Dashboard → Settings → API Keys

2. **GitHub App Installation**:
   - Install Mintlify GitHub App on repository
   - Grant read/write access to `mintlify/` directory

## Initial Setup

### 1. Create Mintlify Project

1. **Sign up** at https://mintlify.com
2. **Create new project**:
   - Project name: "Delight Documentation"
   - Connect GitHub repository
   - Select branch: `main` (production) or feature branch (preview)
3. **Configure repository path**:
   - Root directory: `mintlify/`
   - Config file: `docs.json`

### 2. Configure GitHub Integration

1. **Install Mintlify GitHub App**:
   - Go to GitHub repository → Settings → Integrations
   - Add Mintlify app
   - Grant permissions for repository access

2. **Enable Preview Deployments**:
   - Mintlify Dashboard → Settings → Previews
   - Enable "Deploy previews for pull requests"
   - Set base branch: `main`

### 3. Set Up Custom Domain (Optional)

1. **Choose domain**: e.g., `docs.delight.so`

2. **Add DNS records**:
   ```
   Type: CNAME
   Name: docs
   Value: cname.mintlify.com
   TTL: 3600
   ```

3. **Configure in Mintlify**:
   - Dashboard → Settings → Custom Domain
   - Enter: `docs.delight.so`
   - Verify DNS propagation
   - Enable SSL (automatic via Mintlify)

## Deployment Procedures

### Automatic Deployment (Recommended)

**Production (main branch)**:
1. Merge PR to `main` branch
2. Mintlify auto-detects push
3. Builds and deploys within 1-2 minutes
4. Check deployment status in Mintlify Dashboard

**Preview (feature branches)**:
1. Create PR from feature branch
2. Mintlify creates preview deployment
3. Preview URL posted as PR comment
4. Updates on each new commit to PR

### Manual Deployment (CLI)

```bash
# From repository root
cd mintlify

# Deploy to Mintlify Cloud
npx mint deploy

# Or using pnpm (from repo root)
pnpm docs:deploy
```

**When to use manual deployment**:
- Testing deployment before merge
- Hotfix deployments
- Troubleshooting auto-deployment issues

## Verification Checklist

After deployment, verify:

- [ ] **Site loads**: Navigate to production URL
- [ ] **Navigation works**: Test all sidebar links
- [ ] **Search functions**: Try search bar with keywords
- [ ] **Images load**: Check all embedded images/diagrams
- [ ] **Code blocks**: Verify syntax highlighting
- [ ] **Internal links**: Click through to other pages
- [ ] **Mobile responsive**: Test on mobile viewport
- [ ] **SSL certificate**: Check HTTPS works (if custom domain)

## Monitoring

### Deployment Status
- **Mintlify Dashboard**: Real-time build logs and deployment history
- **GitHub Checks**: Deployment status shows in PR checks
- **Webhook Notifications**: Configure Slack/email alerts for deployment events

### Analytics
Track documentation usage via:
- Mintlify built-in analytics (page views, search queries)
- Google Analytics (if integrated)
- Custom event tracking (if configured)

### Health Checks
- **Availability**: Use external monitoring (UptimeRobot, Pingdom)
- **Link Validation**: Run `pnpm docs:lint` regularly
- **Content Freshness**: Review outdated pages quarterly

## Rollback Procedures

### Scenario 1: Bad Deployment (Broken Navigation)

**Quick Fix**:
```bash
# 1. Identify last good commit
git log --oneline mintlify/

# 2. Revert problematic commit
git revert <bad-commit-sha>

# 3. Push to trigger re-deployment
git push origin main
```

**Alternative (Dashboard)**:
1. Mintlify Dashboard → Deployments
2. Select previous successful deployment
3. Click "Redeploy"

### Scenario 2: Urgent Hotfix

```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/docs-fix main

# 2. Fix the issue
# Edit problematic files in mintlify/

# 3. Commit and push
git add mintlify/
git commit -m "hotfix: correct API endpoint documentation"
git push origin hotfix/docs-fix

# 4. Merge to main immediately
gh pr create --title "Hotfix: Docs correction" --body "Urgent fix for production docs"
gh pr merge --merge --delete-branch
```

### Scenario 3: Complete Rollback

**If deployment causes critical issues**:

1. **Make site private** (immediate mitigation):
   - Mintlify Dashboard → Settings → Visibility
   - Set to "Private" or "Password Protected"

2. **Revert to last stable state**:
   ```bash
   git revert HEAD~1  # Revert last commit
   git push origin main
   ```

3. **Investigate and fix**:
   - Review build logs in Mintlify Dashboard
   - Test locally with `pnpm docs:dev`
   - Fix issues in feature branch

4. **Re-deploy** when fixed:
   - Test thoroughly in preview deployment
   - Merge to main
   - Set visibility back to "Public"

## Troubleshooting

### Build Failures

**Symptom**: Mintlify build fails with error

**Solutions**:
1. **Check build logs**: Mintlify Dashboard → Deployments → Build Logs
2. **Validate locally**: Run `pnpm docs:lint` to catch errors before push
3. **Common causes**:
   - Invalid `docs.json` syntax (JSON linting)
   - Missing referenced files in navigation
   - Malformed markdown (frontmatter errors)
   - Broken image paths

### Deployment Delays

**Symptom**: Deployment takes >5 minutes

**Solutions**:
1. **Check Mintlify status**: https://status.mintlify.com
2. **Verify GitHub webhook**: Settings → Webhooks → Recent Deliveries
3. **Manual trigger**: Use `npx mint deploy`
4. **Contact support**: If persistent, email Mintlify support

### Custom Domain Not Working

**Symptom**: Custom domain shows SSL or DNS errors

**Solutions**:
1. **Verify DNS**: Use `dig docs.delight.so` or https://dns.google.com
   ```bash
   dig docs.delight.so CNAME
   # Should return: cname.mintlify.com
   ```
2. **Wait for propagation**: DNS changes take 1-48 hours
3. **Check SSL**: Mintlify auto-provisions SSL via Let's Encrypt
4. **Re-verify domain**: Dashboard → Custom Domain → "Re-verify"

## Security & Access Control

### Repository Access
- **Principle of least privilege**: Only grant write access to necessary team members
- **Branch protection**: Require PR reviews for main branch changes
- **Secrets management**: Never commit Mintlify API keys to repository

### Deployment Permissions
- **Mintlify Team Roles**:
  - **Admin**: Full access (deployment, settings, billing)
  - **Editor**: Can deploy and edit content
  - **Viewer**: Read-only access to dashboard

### Content Visibility
- **Public**: Anyone can access (for open-source projects)
- **Private**: Requires Mintlify login
- **Password Protected**: Simple password gate
- **SSO**: Enterprise feature for team-wide authentication

## Emergency Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| Docs Owner | [TBD] | Documentation content and structure |
| Platform Engineer | [TBD] | Mintlify configuration and deployment |
| DevOps On-Call | [TBD] | Production issues and rollbacks |
| Mintlify Support | support@mintlify.com | Platform issues and outages |

## Deployment History

### Template Entry
```
Date: YYYY-MM-DD
Deployed By: Name
Commit: abc123
Changes: Brief description
Status: ✅ Success | ⚠️ Issues | ❌ Rolled Back
Notes: Any relevant context
```

### Recent Deployments
(To be filled in as deployments occur)

---

**Last Updated**: 2025-11-13
**Document Owner**: Delight Platform Team

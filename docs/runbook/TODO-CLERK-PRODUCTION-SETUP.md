# Runbook: Promote Clerk to Production

Keep this compact playbook handy when flipping Clerk from test to live credentials.

## Snapshot
- Goal: enable live Clerk auth (`pk_live_*`/`sk_live_*`) with production domains and webhooks.
- Owners: Delight platform team.
- Related story: `stories/1-3-integrate-clerk-authentication-system.md`.

## Prep Checklist
1. Production domain + SSL ready (for example `app.delight.com`).
2. Access to deployment targets (Vercel for frontend and the backend host).
3. Backups of current test environment variables so rollback is easy.

## Execution Flow
1. **Switch Environment**
   - https://dashboard.clerk.com → choose the Delight app → toggle to **Production**.
   - Copy publishable, secret, and webhook keys immediately; add them to the secret manager.
2. **Register Domains + Origins**
   - Settings → Domains → add each live host, complete DNS verification.
   - Settings → Allowed Origins → whitelist every production URL, remove unused test entries.
3. **Wire Webhooks (if needed)**
   - Settings → Webhooks → point to `https://api.delight.com/api/v1/webhooks/clerk`.
   - Subscribe to `user.created`, `user.updated`, `user.deleted`, plus any custom triggers.
4. **Update Environment Variables**
   - Frontend (Vercel → Settings → Environment):
     ```
     NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxx
     CLERK_SECRET_KEY=sk_live_xxx
     NEXT_PUBLIC_API_URL=https://api.delight.com
     ```
     Keep Preview/Development environments on `pk_test_*` keys to isolate QA.
   - Backend host:
     ```
     CLERK_SECRET_KEY=sk_live_xxx
     CLERK_WEBHOOK_SECRET=whsec_xxx
     CORS_ORIGINS=https://app.delight.com
     ```
5. **Redeploy + Smoke Test**
   - Redeploy frontend + backend.
   - Exercise sign-up, sign-in, and a protected route.
   - Trigger a webhook test from Clerk and confirm logs show 2xx responses.

## Troubleshooting Quick Hits
- **Missing users:** production has its own DB. Either export/import via API or ask users to re-register (simplest).
- **Webhook failures:** confirm HTTPS endpoint is reachable, secrets match, and backend logs show traffic. Re-run "Test Endpoint" from Clerk.
- **Developer banner still visible:** double-check environment toggle and redeploy with the live publishable key.

## Security Notes
- Never commit `pk_live_*`, `sk_live_*`, or `whsec_*` to git; store them only in env managers.
- Rotate `sk_live_*` and webhook secrets quarterly or after any incident.
- Lock Clerk dashboard access behind SSO/MFA and review who can read production logs.

## Verification List
- [ ] Live keys configured in frontend + backend
- [ ] Domains verified + CORS cleaned up
- [ ] Webhook secret stored + endpoint tested
- [ ] Manual auth smoke tests passed
- [ ] Ops log entry created with date + operator

## References
- Clerk production guide: https://clerk.com/docs/deployments/overview
- Delight webhook playbook: `docs/WEBHOOK-SETUP-GUIDE.md`

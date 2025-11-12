# Runbook: Jack's Personal Integrations

Quick-reference queue for side quests that do not merit full stories yet. Copy sections into Codex tasks when you are ready to execute.

## 1. Sentry Wiring (Next.js Frontend)
- Command: `npx @sentry/wizard@latest -i nextjs --saas --org jack-luo-mo --project delight`
- Follow the wizard to inject the SDK, then confirm through the onboarding checklist: https://jack-luo-mo.sentry.io/insights/projects/delight/getting-started/
- After verification, capture release health by exporting DSN + auth tokens into the frontend `.env` files.

## 2. Vercel Speed Insights (Optional)
- Validate whether the project actually needs Vercel Speed Insights; if yes, enable the integration under **Vercel → Project → Speed Insights** and document key metrics in sprint notes.
- If no, record the decision + rationale here so the question stops resurfacing.

## 3. Reference Links
- Supabase control plane: https://supabase.com/dashboard/project/zllzszxipezzmgfjllox
- Miro board (story maps + UX flows): https://miro.com/app/board/uXjVJspoD7g=/?focusWidget=3458764647813008983

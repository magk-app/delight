# Delight Component Inventory

Compiled 2025-11-12 from the Next.js frontend (`packages/frontend/src/app`). Use this as a catalog when extending the UI.

| Component / Page | Location | Type | Description |
|------------------|----------|------|-------------|
| `RootLayout` | `src/app/layout.tsx` | Layout | Wraps the app in `ClerkProvider`, renders floating header with `SignInButton`, `SignUpButton`, `UserButton`. |
| `LandingPage` | `src/app/page.tsx` | Marketing | Hero headline, CTA buttons, three feature cards (Remembered Context, Adaptive Missions, Visible Progress). |
| `DashboardPage` | `src/app/dashboard/page.tsx` | Auth Shell | Card grid placeholders for “Your Progress”, “Active Missions”, “Companion”. Exports `dynamic = "force-dynamic"` to keep Clerk sessions fresh. |
| `SignInPage` | `src/app/sign-in/[[...sign-in]]/page.tsx` | Auth | Full-screen gradient wrapper around `<SignIn />`. |
| `SignUpPage` | `src/app/sign-up/[[...sign-up]]/page.tsx` | Auth | Same wrapper for `<SignUp />`. |
| `middleware.ts` | `src/middleware.ts` | Infrastructure | `clerkMiddleware` route guard; defines public route matcher. |
| Global styles | `src/app/globals.css` | Styling | Tailwind base styles, gradients, typography, button tokens. |

## Planned Components (Epic 2)

| Future Component | Notes |
|------------------|-------|
| Memory Timeline Card | Will render tiered memories returned by FastAPI (`MemoryType.personal/project/task`). |
| Companion Chat Panel | Will stream LangGraph responses and show mission context. |
| Mission List | Will summarize open quests from backend once REST endpoints exist. |

Document new components here (location + purpose) as they land so agents and developers can quickly identify reuse opportunities.

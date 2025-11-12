# Delight Frontend UI Inventory

Source: `packages/frontend/src/app` (Next.js App Router). Generated 2025-11-12 to support Epic 2 documentation.

## Layout & Global Elements

- **`src/app/layout.tsx`**
  - Wraps every page in `ClerkProvider`.
  - Injects Inter font + global CSS.
  - Floating header with `SignInButton`, `SignUpButton`, and `UserButton`, automatically switching based on `SignedIn/SignedOut`.
  - Sets SEO metadata (`Delight - AI-Powered Self-Improvement Companion`).
- **`src/app/globals.css`**
  - Tailwind base with gradients + CTA button styles referenced on landing and auth pages.

## Pages & Components

| Route | Component | Purpose | Key Elements |
|-------|-----------|---------|--------------|
| `/` | `src/app/page.tsx` | Marketing landing + CTAs | Hero headline, “Sign In / Get Started” buttons, three feature cards (“Remembered Context”, “Adaptive Missions”, “Visible Progress”). |
| `/dashboard` | `src/app/dashboard/page.tsx` | Authenticated shell for companion UI | Sticky header with “Dashboard” title, placeholder cards for progress, missions, companion. Currently static copy awaiting data APIs. |
| `/sign-in` | `src/app/sign-in/[[...sign-in]]/page.tsx` | Clerk-hosted sign-in form | Full-screen gradient background with `<SignIn />`. |
| `/sign-up` | `src/app/sign-up/[[...sign-up]]/page.tsx` | Clerk-hosted sign-up form | Same layout as sign-in with `<SignUp />`. |

Reusable styles rely on Tailwind utility classes (see `tailwind.config.ts` custom palette for `primary`, `muted`, etc.).

## Component Categories

- **Layout / Shell:** Root layout + dashboard page establishing spacing tokens and responsive grid.
- **Auth Widgets:** Clerk buttons + hosted components; ensure `@clerk/nextjs` stays updated alongside backend configuration.
- **Marketing Blocks:** Grid of feature cards on the landing page; each card uses consistent border + typography tokens and can be swapped for dynamic highlights later.

## Gaps / Next Steps

- Epic 2 will add actual companion cards (chat transcript, memory timeline). When those ship, append them here with source paths and prop definitions.
- Consider extracting the feature cards into `src/components/FeatureCard.tsx` once we add more marketing content.

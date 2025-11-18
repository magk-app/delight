# Delight Marketing Site Implementation

_Last updated: 2025-11-18_  
_Scope: Marketing surface only, not the logged in mission interface_

This document explains the design and implementation of the Delight marketing site that now lives inside the `packages/frontend` app. It covers:

- Goals and constraints
- Information architecture and routing
- Design system changes
- Page level behavior and content
- Dependencies and middleware updates
- Deployment quirks and how we fixed them
- Future improvements

The intent is to give future contributors enough context to extend or refactor without guessing.

---

## 1. Goal and constraints

**Goal**

Create a separate, opinionated marketing surface for Delight:

> An emotionally intelligent AI companion that turns overwhelming goals into adaptive daily missions with a light narrative and game layer.

This is **not** the in app mission UI. It is a site that should feel like a thoughtful essay that happens to be a product, not a generic landing page template.

**Brand and tone**

From README, manifesto, and UX spec, we anchored on:

- ~60 percent serious productivity and real work
- ~40 percent narrative and game energy
- Voice: direct, intelligent, low hype, low fluff
- Visual references:
  - Essay like depth similar to roam.lol
  - Tight modern polish similar to cluely.com
- Personas:
  - Founders and multi project operators
  - Ambitious students balancing class and side projects
  - Overloaded ambitious people in transition

**Technical constraints**

- Next.js App Router (v15) with React and TypeScript
- Lives under `packages/frontend`
- Tailwind CSS (reusing existing config, extended where needed)
- shadcn/ui for primitives such as buttons and layout primitives
- Framer Motion for animation
- Clerk for auth, with correct public routes for marketing pages

---

## 2. High level structure

### 2.1 Route group and files

Marketing pages live under a dedicated App Router group:

```
packages/frontend/src/app
  ├─ (marketing)/
  │   ├─ layout.tsx          // Shared marketing shell
  │   ├─ page.tsx            // GET /        - Landing
  │   ├─ why/
  │   │   └─ page.tsx        // GET /why     - Manifesto
  │   ├─ waitlist/
  │   │   └─ page.tsx        // GET /waitlist
  │   └─ future/
  │       └─ page.tsx        // GET /future  - Future ideas
  ├─ sign-in/[[...sign-in]]  // Existing Clerk routes
  └─ sign-up/[[...sign-up]]
```

**Shared marketing components:**

```
packages/frontend/src/components/marketing
  ├─ header.tsx
  ├─ footer.tsx
  └─ hero-animation.tsx
```

### 2.2 Removal of old homepage

Previously there was a root `src/app/page.tsx` that rendered the original basic frontend. With the introduction of `(marketing)/page.tsx`, there were two competing definitions of `/`. That led to build artifacts like:

```
ENOENT: no such file or directory, lstat '.next/server/app/(marketing)/page_client-reference-manifest.js'
```

To resolve this:

- `packages/frontend/src/app/page.tsx` was removed
- The canonical homepage for `/` is now `src/app/(marketing)/page.tsx`
- If you ever reintroduce a logged in dashboard at `/`, it will need either a different route group or a routing decision inside `(marketing)` that checks auth and delegates.

---

## 3. Shared layout, header, and footer

### 3.1 Marketing layout

**File:** `src/app/(marketing)/layout.tsx`

**Responsibilities:**

- Provides the shared chrome for all marketing routes
- Renders `MarketingHeader` fixed at the top
- Renders `MarketingFooter` at the bottom
- Adds top padding so body content clears the fixed header

**Skeleton:**

```tsx
import { MarketingHeader } from "@/components/marketing/header";
import { MarketingFooter } from "@/components/marketing/footer";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <MarketingHeader />
      <main className="flex-1 pt-16">{children}</main>
      <MarketingFooter />
    </div>
  );
}
```

### 3.2 Header

**File:** `src/components/marketing/header.tsx`

**Key behavior:**

- Fixed header with blur and border
- Left: Delight logo mark and wordmark
- Center or left: navigation links
  - Product (scroll anchors on `/` where applicable)
  - Why Delight (`/why`)
  - Future (`/future`)
- Right: actions
  - "Sign in" link (placeholder, currently points to `/sign-in`)
  - Primary "Join waitlist" button pointing to `/waitlist`
- Mobile:
  - Uses a hamburger icon (Menu from lucide-react)
  - Toggles a Sheet style slide out menu using shadcn style markup (or a custom implementation that behaves similarly)
  - All nav links and CTA available in the mobile menu

**Reused brand treatment:**

- Logo: simple square with a gradient from primary to secondary and a white "D" inside
- Text: "Delight" in a modern sans serif
- If you later add the real SVG logo from the repo, you can replace the square mark while keeping the structure.

### 3.3 Footer

**File:** `src/components/marketing/footer.tsx`

**Content:**

- Left:
  - Logo and product name
  - Short description summarizing Delight as an emotionally intelligent AI companion focused on goals and missions
  - Single sentence about trust, control, and exportability
- Right side columns (responsive stack on mobile):
  - Links:
    - GitHub repo (placeholder URL currently, ensure it points to the real repo)
    - Twitter or other social placeholder
    - Optional future link like Docs when public docs exist
- Small text row with:
  - Copyright line
  - Very short note on privacy philosophy

The footer is intentionally compact and understated to keep focus on the content.

---

## 4. Design system updates

### 4.1 Tailwind theme tokens

**File:** `packages/frontend/src/app/globals.css`

**Area:** `@layer base { :root { ... } }`

The color system already used HSL design tokens. We adjusted them to line up with the UX spec and created a success token:

- `--primary`
  - Warm amber or gold tone used for progress, streaks, and key CTAs
- `--secondary`
  - Soft purple used to represent the companion presence and more reflective states
- `--success` and `--success-foreground`
  - Warm green pair for growth and positive feedback surfaces

**Tailwind config then exposes:**

**File:** `packages/frontend/tailwind.config.ts`

```ts
extend: {
  colors: {
    // existing colors...
    success: {
      DEFAULT: "hsl(var(--success))",
      foreground: "hsl(var(--success-foreground))",
    },
  },
},
plugins: [require("tailwindcss-animate")],
```

**Note:** `tailwindcss-animate` was added as a dev dependency.

### 4.2 Typography

**File:** `src/app/layout.tsx` and `globals.css`

Previously the app used the Inter font via `next/font` and applied `inter.className` to body. For easier compatibility and less coupling:

- We set body to use `className="font-sans"` in `layout.tsx`.
- We defined a robust system font stack in `globals.css`:

```css
body {
  @apply bg-background text-foreground;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}
```

If you want to restore Inter or another custom font, you can reintroduce `next/font` at the root and keep marketing pages unchanged. The marketing layout does not depend on a specific font, only on Tailwind typography classes.

### 4.3 shadcn and animations

The marketing pages follow the existing shadcn/ui conventions:

- Button styles reused for "Join waitlist" and secondary actions
- Cards for structured content sections

**For motion:**

- `framer-motion` is used in `HeroAnimation` and some section reveals
- `tailwindcss-animate` provides simple utility classes for fade and slide animations where needed

**Animations respect accessibility:**

- They are subtle and not constant
- The design is compatible with `prefers-reduced-motion` checks if you add them later

### 4.4 ESLint configuration

Vercel deployment failed on lint due to the default `react/no-unescaped-entities` rule. The marketing copy uses natural language with apostrophes and quotes, and manually escaping everything would harm readability.

**To fix this at the package level:**

**File:** `packages/frontend/.eslintrc.json`

```json
{
  "extends": "next/core-web-vitals",
  "rules": {
    "react/no-unescaped-entities": "off"
  }
}
```

The root `.eslintrc.json` that was briefly created has been removed. Only the frontend package config remains.

This approach keeps marketing content clean while still enforcing other Next core web vital rules.

---

## 5. Page by page breakdown

### 5.1 Landing page `/`

**File:** `src/app/(marketing)/page.tsx`

**Sections in order:**

#### Hero section

- Left side:
  - Headline like:
    - "An emotionally intelligent AI companion that turns overwhelming goals into daily missions"
  - Subheading:
    - Emphasizes emotional awareness, remembered context, and visible yet respectful progress
  - Primary CTA: "Join waitlist" pointing to `/waitlist`
  - Secondary link: "Why we are building this" pointing to `/why`
- Right side: `<HeroAnimation />`

#### HeroAnimation component

**File:** `src/components/marketing/hero-animation.tsx`

**Responsibilities:**

- Show a narrative line with a typewriter effect
  - Example text sequence:
    - "Day 5: You open Delight, feeling overwhelmed by your project backlog..."
    - "Eliza greets you: 'Let us turn that anxiety into action. What matters most today?'"
    - (Names and phrasing can be adjusted to match the canonical UX copy.)
- Show a progress visualization
  - A ring or bar that fills to a percentage such as "Today: 64% toward Craft and 40% toward Health"
- Show a mission breakdown panel
  - One large goal title (for example "Prepare investor update")
  - Three mission cards beneath it, with:
    - Title
    - Approximate time
    - Points or Essence value

**Implementation details:**

- Uses `useState` to track current narrative phase and progress
- Uses `useEffect` with intervals to:
  - Advance phases on a timer
  - Adjust progress value
  - Animate typewriter text by slicing a string over time
- Uses `framer-motion` for:
  - Fade and slide transitions between phases
  - Slight hover lifts on mission cards
- Should be wrapped in a check for `prefers-reduced-motion` if you want to tone it down further for some users

#### Who it is for

**Section:** three personas, each rendered as a card:

1. Founder and operator with multiple projects
2. Ambitious student juggling class, research, and side projects
3. Overloaded person in a life transition such as job change or relocation

Each card includes:

- Short context sentence about their situation
- One sentence describing how a typical Delight session changes their day

#### Three pillars

**Section:** three columns on desktop, stacked on mobile.

**Pillars:**

1. **Emotion first guidance**
   - Short heading
   - Two to three sentences about starting with emotional state and friction, not just a todo list
2. **Living memory that compounds**
   - Explanation of how Delight accumulates context over days and weeks
3. **Adaptive micro missions**
   - How the system cuts large goals into adaptive missions that feel doable

Each pillar includes a small icon or SVG illustration that matches the concept.

#### Visible progress and the game layer

**Section explains:**

- Streaks and highlight reels
- Progress constellations
- Essence or similar long term progress metric

**Visuals:**

- A row of three cards:
  - "3 day streak" card
  - "Highlight reel" mock showing a week of wins
  - "Constellation" mini diagram made of dots and lines

Messaging clarifies that the game layer exists to support real work, not to turn everything into points for their own sake.

#### How Delight works

A short five step product tour, either horizontal or vertical:

1. Check in with how you feel
2. Triage what matters next
3. Pick a mission sized task
4. Work in a focused way with gentle support
5. Capture proof and watch your world change over time

Each step rendered as a card or timeline item with a small UI preview and one short sentence.

#### For developers and technical buyers

**Compact technical section with:**

- Stack highlights such as:
  - FastAPI
  - Postgres with pgvector
  - Redis and or Chroma
  - LangGraph multi agent orchestration
  - Cost awareness and token accounting
- Optional code style block or pseudo snippet that mirrors the architecture doc in a friendly way

#### Final CTA

Restates the core promise in one or two sentences and repeats:

- Primary "Join waitlist" button
- Secondary link to `/future` for people who care about long term direction

### 5.2 Why Delight `/why`

**File:** `src/app/(marketing)/why/page.tsx`

This page is a manifesto written as if the founders are speaking directly to the reader. Structure:

- Narrow content column for easier reading
- Sectioned layout with titles such as:
  - "Ambition is not the problem. Emotional friction is."
  - "Why tools that ignore your state keep failing you."
  - "What it means to be a companion with memory."
  - "Why we built a world instead of another list."
  - "How we think about privacy, cost, and trust."

Each section:

- One clear opening statement
- One to three short paragraphs expanding it

**Pull quotes:**

- Key sentences surfaced in a slightly larger or lighter card to break up the text

**At the bottom:**

- Short line: "If this resonates, you are exactly who we are building for."
- Primary CTA: "Join waitlist"
- Secondary link: "Back to product" pointing to `/`

The content here should stay aligned with the `manifesto.md` and product brief. If those change significantly, revisit this page first.

### 5.3 Waitlist `/waitlist`

**File:** `src/app/(marketing)/waitlist/page.tsx`

**Purpose:** capture intent for early access and pilot cohorts.

**Structure:**

#### Intro hero

- Title: "Join the Delight waitlist"
- Short descriptive paragraph that promises:
  - Early access when the product is ready
  - Possibility of joining a pilot cohort
  - No daily spam

#### Form area

- Embeds the Google Form:
  - URL: `https://forms.gle/uouMuAKw4p2BqHw77`
  - Implemented as an `<iframe>` inside a responsive container
  - Width and height tuned for typical forms, with full width on mobile
- Fallback:
  - A button "Open waitlist form" with `target="_blank"` that opens the form in a new tab
  - Raw link displayed below for accessibility and link copying

#### Benefits and expectations

- Small icon bullets explaining:
  - What being on the waitlist means
  - How often emails will be sent (low frequency)
  - What kind of feedback and collaboration is expected during beta

#### Mini FAQ

Three typical questions, for example:

- When is the beta starting
- How often will you email me
- Who is the best fit for early access

Each has a one paragraph answer that keeps expectations reasonable and honest.

### 5.4 Future `/future`

**File:** `src/app/(marketing)/future/page.tsx`

**Goal:** show a transparent "future lab" of ideas that are not in MVP but are on the radar.

**Content structure:**

#### Intro

- Explains why the team cares about:
  - Future of work
  - Companions and narrative
  - Long horizon thinking

#### Themes

An array of themed "future cards". Each theme has:

- Title (for example "Social and guild features")
- Icon (from lucide-react)
- Status badge:
  - `exploring`
  - `prototyping`
  - `long term`

**Example themes:**

- Social and guild features
- Deeper narrative and RPG systems
- Voice and multimodal interactions
- Advanced analytics and reflection tools
- Integrations with calendars, code, and creative tools
- Autonomous agent networks
- Community and matchmaking
- Emotion aware sensory inputs

Under each theme, individual items:

- Title
- Two to three sentence description
- Status label

#### Status legend

- Clarifies what each status means, so people understand what to expect.

#### Closing CTA

- Invites visitors to:
  - Join the waitlist if this direction resonates
  - Reach out if a particular idea is important to them

---

## 6. Middleware and authentication

**File:** `packages/frontend/src/middleware.ts`

Clerk integration originally protected most routes by default. Marketing pages need to be public.

**We updated the public route matcher:**

```ts
const isPublicRoute = createRouteMatcher([
  "/",
  "/why",
  "/waitlist",
  "/future",
  "/sign-up(.*)",
  "/api/v1/webhooks(.*)",
]);
```

This allows:

- Anonymous visitors to access all marketing surfaces
- Clerk to still guard the dashboard and other private routes

**Known quirk:**

Next.js 15 and Clerk can produce warnings such as:

```
Route "/" used headers() or similar iteration. headers() should be awaited before using its value.
```

This comes from Clerk internals and does not block rendering. Pages still return HTTP 200. Once Clerk and Next converge on the same async APIs, this should settle down.

---

## 7. Dependencies added

The marketing work introduced the following dependencies into `packages/frontend`:

- `lucide-react`
  - Icon set used across marketing pages for consistent, lightweight SVG visuals
- `tailwindcss-animate`
  - Utility classes for simple entrance and exit animations

These are installed via `pnpm` and wired in `tailwind.config.ts`.

No new runtime API dependencies were added. All product details come from existing docs and static copy.

---

## 8. Local development and deployment

### 8.1 Running locally

From repo root:

```bash
cd packages/frontend
pnpm install         # once
pnpm dev
```

Then visit:

- `http://localhost:3000` - Landing page
- `http://localhost:3000/why` - Manifesto
- `http://localhost:3000/waitlist`
- `http://localhost:3000/future`

### 8.2 Building locally

```bash
cd packages/frontend
pnpm build
```

**If the build fails:**

- Check for duplicate route definitions under `src/app`
- Ensure `tailwindcss-animate` is installed
- Ensure ESLint is picking up `packages/frontend/.eslintrc.json`

### 8.3 Vercel notes

**Common issues that were encountered and fixed:**

#### Missing tailwindcss-animate

- **Symptom:** module not found error during build
- **Fix:** `pnpm add -D tailwindcss-animate` in `packages/frontend`

#### Duplicate homepage

- **Symptom:** `ENOENT` for `page_client-reference-manifest.js` inside `(marketing)`
- **Cause:** both `src/app/page.tsx` and `src/app/(marketing)/page.tsx` mapping to `/`
- **Fix:** remove the old `src/app/page.tsx`

#### Lint failures for unescaped entities

- **Symptom:** Vercel build fails with `react/no-unescaped-entities`
- **Fix:** turn off this ESLint rule in `packages/frontend/.eslintrc.json`

If Vercel is using a cached build, clearing the build cache or pushing a new commit after these fixes usually resolves the errors.

---

## 9. Future improvements

Some obvious follow ups that would keep the site aligned with the product:

### Connect real logo assets

- Replace the temporary gradient square with the canonical Delight logo SVG where available.

### Anchor scroll for "Product"

- On the landing page, wire "Product" in the header to scroll to the "How Delight works" section rather than top of page.

### Better reduced motion support

- Wrap Framer Motion animations in a hook that checks `prefers-reduced-motion` and disables non essential motion.

### Docs link

- When docs are public, add a lower priority "Docs" link in the footer or as a secondary header item.

### Analytics and A/B testing

- Add minimal instrumentation to measure scroll depth and CTA click rates.
- Experiment with alternative hero narrative variants.

### In app handoff

- Once the logged in experience is fully defined, add a coherent path from marketing to app, for example:
  - Sign in from header that respects redirect back to marketing or dashboard.

---

## 10. Quick reference

### Routes

- `/` - Marketing landing page
- `/why` - Manifesto and philosophy
- `/waitlist` - Early access form and FAQ
- `/future` - Future ideas and roadmap themes

### Key files

#### Layout and structure

- `src/app/(marketing)/layout.tsx`
- `src/app/(marketing)/page.tsx`
- `src/app/(marketing)/why/page.tsx`
- `src/app/(marketing)/waitlist/page.tsx`
- `src/app/(marketing)/future/page.tsx`

#### Components

- `src/components/marketing/header.tsx`
- `src/components/marketing/footer.tsx`
- `src/components/marketing/hero-animation.tsx`

#### Config

- `packages/frontend/tailwind.config.ts`
- `packages/frontend/src/app/globals.css`
- `packages/frontend/.eslintrc.json`
- `packages/frontend/src/middleware.ts`

---

## Maintenance notes

This doc should be updated whenever:

- The Delight brand palette changes
- The Hero narrative or mission framing changes significantly
- New top level routes are added under `(marketing)`
- The product philosophy or manifesto changes in a way that affects the `/why` page


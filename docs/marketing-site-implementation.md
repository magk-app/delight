# Marketing Site Implementation Guide

**Version:** 1.0
**Date:** November 2025
**Status:** Complete and Deployed

---

## Overview

This document provides a complete reference for the Delight marketing website, built as a separate layer from the main application. The marketing site is designed to communicate the product's unique positioning as an emotionally intelligent AI companion while maintaining a balance between serious SaaS aesthetics and narrative energy.

## Design Philosophy

The marketing site follows these core principles:

- **60% serious modern SaaS, 40% narrative/game energy** - Professional without being sterile
- **Essay-like depth** - Inspired by roam.lol's thoughtful long-form content
- **Sleek polish** - Visual treatment similar to cluely.com
- **Natural language** - Direct, intelligent copy without hype or fluff
- **Accessible and responsive** - Works beautifully on all devices

---

## Architecture

### Route Structure

The marketing site uses Next.js 15 App Router with a route group pattern:

```
src/app/
├── (marketing)/              # Marketing route group (shared layout)
│   ├── layout.tsx           # Marketing-specific layout with footer
│   ├── page.tsx             # Landing page (/)
│   ├── why/
│   │   └── page.tsx         # Manifesto page (/why)
│   ├── waitlist/
│   │   └── page.tsx         # Waitlist page (/waitlist)
│   └── future/
│       └── page.tsx         # Future vision page (/future)
├── layout.tsx               # Root layout with MainNav
├── globals.css              # Global styles and CSS variables
└── [other app routes]       # Dashboard, sign-in, etc.
```

**Key Insight:** The `(marketing)` route group allows shared layouts without affecting URL paths. All marketing pages use the root path (e.g., `/`, `/why`) while sharing common components.

### Navigation Architecture

Navigation is handled at two levels:

1. **Root Layout (`app/layout.tsx`):**
   - Contains `MainNav` component (unified header for entire site)
   - Wraps all pages including marketing and app pages
   - Handles Clerk authentication UI

2. **Marketing Layout (`app/(marketing)/layout.tsx`):**
   - Contains `MarketingFooter` component
   - Applies to all marketing pages only
   - Provides consistent footer across marketing routes

This two-tier approach ensures:
- Consistent header across marketing AND logged-in app
- Marketing-specific footer only on public pages
- Clean separation of concerns

---

## Design System

### Color Palette

The color system is defined in `globals.css` using HSL CSS variables:

```css
--primary: 30 100% 63%;        /* Warm amber/gold - Progress, wins, CTAs */
--secondary: 272 72% 65%;       /* Soft purple - Eliza presence, wisdom */
--success: 145 69% 52%;         /* Warm green - Growth, completion */
--foreground: 210 24% 16%;      /* Dark text */
--background: 0 0% 100%;        /* White background */
--muted: 210 17% 93%;           /* Light gray backgrounds */
--border: 210 17% 90%;          /* Subtle borders */
```

**Usage in Tailwind:**

```tsx
// Primary button
<button className="bg-primary text-primary-foreground">
  Join Waitlist
</button>

// Secondary accent
<div className="bg-secondary/10 border border-secondary/20">
  Eliza content
</div>
```

### Typography

**System Font Stack:**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;
```

**Size Scale:**
- Headings: `text-4xl` to `text-6xl` (36px to 60px)
- Body: `text-base` to `text-lg` (16px to 18px)
- Small: `text-sm` to `text-xs` (14px to 12px)

**Font Weights:**
- Normal text: `font-normal` (400)
- Semibold headings: `font-semibold` (600)
- Bold titles: `font-bold` (700)

### Spacing System

Uses Tailwind's default spacing scale (4px base unit):
- Sections: `py-20` (80px) to `py-32` (128px)
- Container: `px-4 sm:px-6 lg:px-8` (responsive padding)
- Component gaps: `gap-4` to `gap-12` (16px to 48px)

---

## Components Reference

### 1. MainNav (`components/navigation/main-nav.tsx`)

**Purpose:** Unified navigation header for entire site (marketing + app)

**Features:**
- Responsive design with mobile hamburger menu
- Clerk authentication integration (Sign In/Sign Up/User Button)
- Logo with favicon
- Desktop and mobile navigation links
- Sticky header with backdrop blur

**Props:** None (self-contained)

**Key Implementation Details:**
```tsx
// Shows different links when signed in
<SignedIn>
  <Link href="/companion">Companion</Link>
</SignedIn>

// Mobile menu state
const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
```

**Styling:**
- Fixed position: `fixed top-0 left-0 right-0`
- Background: `bg-background/80 backdrop-blur-md`
- Border: `border-b border-border`
- Z-index: `z-50`

### 2. MarketingFooter (`components/marketing/footer.tsx`)

**Purpose:** Marketing-specific footer with links and branding

**Features:**
- Brand description
- Link groups (Product, Connect)
- GitHub link
- Copyright notice

**Layout:**
- 4-column grid on desktop
- Single column on mobile
- 2 columns for brand, 1 each for link groups

### 3. HeroAnimation (`components/marketing/hero-animation.tsx`)

**Purpose:** Interactive demonstration on landing page

**Features:**
- Typewriter effect showing narrative generation
- Progress ring animation
- Mission card breakdown
- Auto-looping animation

**Technical Implementation:**

```tsx
// Typewriter effect
useEffect(() => {
  const targetText = narrativePhases[currentPhase];
  let charIndex = 0;

  const typeInterval = setInterval(() => {
    if (charIndex < targetText.length) {
      setNarrativeText(targetText.slice(0, charIndex + 1));
      charIndex++;
    }
  }, 30); // 30ms per character

  return () => clearInterval(typeInterval);
}, [currentPhase]);
```

**State Management:**
- `currentPhase`: Tracks which narrative to show
- `narrativeText`: Current typed text
- `progress`: Progress bar percentage

**Animation Phases:**
1. Typewriter shows user opening Delight
2. Eliza greeting message
3. Breaking down goal into missions
4. Mission cards appear
5. Loop restarts

---

## Page Implementations

### Landing Page (`/`)

**Purpose:** Primary entry point showcasing product value

**Sections (in order):**

1. **Hero Section**
   - Two-column layout (copy left, animation right)
   - Headline with gradient text
   - Dual CTAs (Join Waitlist, Why Building)
   - Interactive HeroAnimation component

2. **Who It's For**
   - Three persona cards (Founders, Students, Life Transitions)
   - Real user story examples
   - Icon differentiation (Zap, Brain, Heart)

3. **Three Core Pillars**
   - Emotion-first guidance
   - Living memory that compounds
   - Adaptive micro missions
   - Each with detailed explanation and visual accent

4. **Visible Progress**
   - Four feature cards (Streaks, Highlight Reels, Constellation, DCI)
   - Grid layout with hover effects
   - Icon-based visualization

5. **How It Works**
   - 5-step product tour
   - Numbered progression
   - Clear descriptions of each step

6. **Technical Section**
   - For developers and technical buyers
   - 6-item grid (FastAPI, PostgreSQL, LangGraph, etc.)
   - Compact presentation

7. **Final CTA**
   - Restated value proposition
   - Dual CTAs (Waitlist, Future)
   - Gradient background accent

**Key Code Patterns:**

```tsx
// Gradient text
<span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
  adaptive daily missions
</span>

// Card with hover effect
<div className="bg-card border border-border rounded-xl p-6
                hover:border-primary/50 transition-all hover:shadow-lg">
  {/* content */}
</div>
```

### Why Page (`/why`)

**Purpose:** Deep manifesto explaining product philosophy

**Structure:**
- Narrow reading column (max-w-2xl)
- Hero section with centered title
- 5 thematic sections
- Pull quotes for emphasis
- Closing CTA

**Sections:**

1. **Ambition is not the problem. Emotional friction is.**
   - Defines the core problem
   - Explains emotional friction
   - Why traditional tools fail

2. **Why tools that ignore your state keep failing you**
   - DIY productivity systems
   - Generic AI assistants
   - Professional coaching limitations

3. **What it means to be a companion with memory**
   - Three-tier memory architecture
   - Compounding value over time
   - Anticipatory intelligence

4. **Why we built a world instead of another list**
   - Narrative vs. lifeless lists
   - Meaningful gamification
   - Genuine motivation

5. **How we think about privacy, cost, and trust**
   - Transparency and control
   - Cost efficiency rationale
   - Trust as defensible moat

**Styling Notes:**

```tsx
// Pull quote style
<blockquote className="border-l-4 border-primary pl-6 py-2
                       italic text-xl text-foreground/80">
  Quote text
</blockquote>

// Body text with readable line-height
<p className="text-foreground/90 leading-relaxed">
  Paragraph text
</p>
```

### Waitlist Page (`/waitlist`)

**Purpose:** Capture early access signups

**Layout:**
- Two-column grid (benefits left, form right)
- Sticky form on desktop
- Single column on mobile

**Components:**

1. **Benefits Section**
   - Early access
   - Thoughtful updates
   - Product direction input
   - "Best fit" criteria list

2. **Google Form Embed**
   - Iframe embedded at 800px height
   - Fallback link if iframe doesn't load
   - Responsive container

3. **FAQ Section**
   - 4 common questions
   - Beta timing
   - Email frequency
   - Free access
   - Feedback expectations

**Form Implementation:**

```tsx
<iframe
  src="https://docs.google.com/forms/d/e/[FORM_ID]/viewform?embedded=true"
  width="100%"
  height="800"
  frameBorder="0"
  className="w-full"
>
  Loading…
</iframe>
```

**Note:** The Google Form ID is currently set to the actual Delight waitlist form. Update the `src` URL if form changes.

### Future Page (`/future`)

**Purpose:** Transparency about roadmap and vision

**Structure:**
- 8 themed feature categories
- 3 feature cards per category (24 total features)
- Status badges (exploring, prototyping, long-term)
- Status legend explaining phases

**Feature Categories:**

1. Social & Guild Features
2. Deeper Narrative & RPG Systems
3. Voice & Multimodal Interactions
4. Advanced Analytics & Reflection
5. Calendar & Tool Integrations
6. Autonomous Agent Network
7. Community & Matchmaking
8. Emotion-Aware Sensory Inputs

**Status Badge Implementation:**

```tsx
const statusColors = {
  exploring: "bg-secondary/10 text-secondary border-secondary/20",
  prototyping: "bg-primary/10 text-primary border-primary/20",
  "long-term": "bg-muted text-muted-foreground border-border",
};

<span className={`px-3 py-1 rounded-full text-xs font-medium
                   border ${statusColors[status]}`}>
  {status}
</span>
```

---

## Responsive Design

### Breakpoints

Following Tailwind's default breakpoints:

- **Mobile:** < 640px (default)
- **Tablet:** >= 640px (`sm:`)
- **Desktop:** >= 768px (`md:`)
- **Large:** >= 1024px (`lg:`)
- **XL:** >= 1280px (`xl:`)

### Responsive Patterns

**Grid Layouts:**
```tsx
// Single column mobile, 2 columns tablet, 3 columns desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

**Typography:**
```tsx
// Responsive text sizes
<h1 className="text-4xl sm:text-5xl lg:text-6xl">
  Headline
</h1>
```

**Spacing:**
```tsx
// More padding on larger screens
<div className="px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
```

**Navigation:**
```tsx
// Hide on mobile, show on desktop
<div className="hidden md:flex">
  Desktop nav
</div>

// Show on mobile, hide on desktop
<button className="md:hidden">
  Mobile menu toggle
</button>
```

---

## Authentication Integration

### Clerk Setup

The marketing site integrates with Clerk for authentication:

**Public Routes (middleware.ts):**
```tsx
const isPublicRoute = createRouteMatcher([
  "/",           // Landing page
  "/why",        // Manifesto
  "/waitlist",   // Waitlist form
  "/future",     // Future vision
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/v1/webhooks(.*)",
]);
```

**Authentication UI:**
- Sign In/Sign Up buttons in MainNav when signed out
- UserButton in MainNav when signed in
- Modal mode (overlay) for auth flows

**Environment Variables Required:**

```env
# Frontend (.env.local)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

---

## Styling Conventions

### Tailwind Utility Classes

**Layout:**
```tsx
// Flexbox
flex flex-col items-center justify-between gap-4

// Grid
grid grid-cols-1 md:grid-cols-3 gap-8

// Container
container mx-auto px-4 sm:px-6 lg:px-8
```

**Colors:**
```tsx
// Background
bg-background bg-card bg-muted/30

// Text
text-foreground text-muted-foreground

// Borders
border border-border rounded-xl

// Accents
bg-primary text-primary-foreground
bg-secondary/10 border-secondary/20
```

**Effects:**
```tsx
// Transitions
transition-colors transition-all

// Hover states
hover:bg-primary/90 hover:shadow-lg hover:scale-105

// Backdrop blur
backdrop-blur-md
```

### Custom CSS Variables

Defined in `globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 210 24% 16%;
  --primary: 30 100% 63%;
  --secondary: 272 72% 65%;
  --success: 145 69% 52%;
  /* ... more variables */
}
```

**Extending Colors in Tailwind:**

Already configured in `tailwind.config.ts`:

```ts
colors: {
  primary: {
    DEFAULT: "hsl(var(--primary))",
    foreground: "hsl(var(--primary-foreground))",
  },
  success: {
    DEFAULT: "hsl(var(--success))",
    foreground: "hsl(var(--success-foreground))",
  },
}
```

---

## Content Guidelines

### Tone and Voice

**Dos:**
- Be direct and intelligent
- Use specific examples
- Acknowledge real struggles
- Explain the "why" behind decisions
- Use "we" when talking about the team
- Use "you" when addressing users

**Don'ts:**
- Use hype language or superlatives
- Make unrealistic promises
- Use jargon without explanation
- Be generic or vague
- Use salesy pressure tactics

### Example Good Copy:

```
✅ "You know what to do. You just can't start."
✅ "Trust isn't built in a single conversation."
✅ "When you're overwhelmed, another task list isn't the answer."
```

### Example Bad Copy:

```
❌ "Revolutionary AI-powered productivity breakthrough!"
❌ "10X your productivity in just 5 minutes!"
❌ "The world's best goal-tracking system!"
```

### Apostrophes and Quotes

**ESLint Configuration:**

The marketing pages have `react/no-unescaped-entities` disabled in `.eslintrc.json`:

```json
{
  "extends": "next/core-web-vitals",
  "rules": {
    "react/no-unescaped-entities": "off"
  }
}
```

This allows natural contractions (you're, don't, can't) and quotes without HTML entity escaping for better readability.

---

## Dependencies

### Core Dependencies

```json
{
  "@clerk/nextjs": "^5.0.0",       // Authentication
  "framer-motion": "^11.0.0",      // Animations
  "lucide-react": "^0.554.0",      // Icons
  "next": "^15.0.0",               // Framework
  "react": "^19.0.0",              // UI library
  "tailwindcss": "^3.4.0",         // Styling
  "tailwindcss-animate": "^1.0.7"  // Animation utilities
}
```

### Icon System (Lucide React)

Used throughout for consistent iconography:

```tsx
import { Heart, Brain, Target, Menu, X } from "lucide-react";

<Heart className="w-6 h-6 text-secondary" />
```

**Commonly Used Icons:**
- `Heart` - Emotion, care
- `Brain` - Intelligence, memory
- `Target` - Goals, missions
- `Zap` - Energy, founders
- `Sparkles` - Delight, magic
- `Menu` / `X` - Mobile menu toggle
- `Users` - Community
- `Calendar` - Time, streaks

---

## Performance Considerations

### Image Optimization

Currently using Next.js Image component for the logo:

```tsx
import Image from "next/image";

<Image
  src="/favicon-32x32.png"
  alt="Delight Logo"
  width={32}
  height={32}
/>
```

**Future:** Replace placeholder favicon with branded logo SVG.

### Animation Performance

Framer Motion is configured for optimal performance:

```tsx
// Respect reduced motion preferences
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8, ease: "easeOut" }}
>
```

**Best Practices:**
- Use transform properties (translateY) over top/left
- Keep duration under 1 second
- Use easeOut for enter animations
- Limit concurrent animations

### Route Optimization

All marketing pages are statically generated:

```tsx
// No dynamic data fetching
// Next.js automatically optimizes at build time
```

---

## Deployment

### Vercel Configuration

The site is configured to deploy from the monorepo:

**Root Directory:** `packages/frontend`
**Build Command:** `pnpm build`
**Output Directory:** `.next`

### Environment Variables

Required in Vercel dashboard:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### Build Process

1. Vercel detects `pnpm-lock.yaml`
2. Runs `pnpm install --frozen-lockfile`
3. Runs `pnpm build` in frontend package
4. Next.js compiles and optimizes
5. Deployment succeeds

---

## Common Issues and Solutions

### Issue: Build fails with "ENOENT: no such file or directory"

**Cause:** Duplicate page files competing for same route
**Solution:** Ensure only one `page.tsx` per route

```bash
# Wrong - both try to render at "/"
src/app/page.tsx
src/app/(marketing)/page.tsx

# Correct - only one homepage
src/app/(marketing)/page.tsx
```

### Issue: Clerk headers() warning in console

**Cause:** Next.js 15 async API compatibility with Clerk
**Solution:** This is a known issue that doesn't affect functionality. Pages render correctly. Clerk will update their library.

**Warning:**
```
Error: Route "/" used `headers()` should be awaited...
```

**Status:** Can be safely ignored. Does not prevent deployment.

### Issue: ESLint errors about unescaped quotes

**Cause:** Marketing content has natural language quotes
**Solution:** Disabled rule in `.eslintrc.json`

```json
{
  "rules": {
    "react/no-unescaped-entities": "off"
  }
}
```

### Issue: Mobile menu doesn't close on navigation

**Cause:** Missing `onClick` handler
**Solution:** Add state reset to each mobile link

```tsx
<Link
  href="/why"
  onClick={() => setMobileMenuOpen(false)}
>
  Why Delight
</Link>
```

---

## Customization Guide

### Changing Colors

1. Update CSS variables in `globals.css`:

```css
:root {
  --primary: 30 100% 63%;  /* Change hue/saturation/lightness */
}
```

2. Colors automatically update throughout site via Tailwind

### Adding New Pages

1. Create page in marketing group:

```bash
src/app/(marketing)/new-page/page.tsx
```

2. Add to navigation in `MainNav`:

```tsx
<Link href="/new-page">New Page</Link>
```

3. Add to public routes in `middleware.ts`:

```tsx
const isPublicRoute = createRouteMatcher([
  "/",
  "/why",
  "/new-page",  // Add here
]);
```

### Changing Footer Links

Edit `components/marketing/footer.tsx`:

```tsx
<Link href="/new-link" className="text-sm text-muted-foreground...">
  New Link
</Link>
```

### Updating Hero Animation

Edit `components/marketing/hero-animation.tsx`:

```tsx
const narrativePhases = [
  "New first message...",
  "New second message...",
  "New third message...",
];
```

---

## Testing Checklist

Before deploying changes:

- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Verify all links work
- [ ] Check authentication flows (sign in/up)
- [ ] Test mobile navigation menu
- [ ] Verify color contrast meets WCAG AA
- [ ] Test form submissions (waitlist)
- [ ] Check build locally (`pnpm build`)
- [ ] Verify no console errors
- [ ] Test with reduced motion enabled
- [ ] Check loading performance

---

## Future Improvements

### Short Term

- [ ] Replace placeholder favicon with branded logo SVG
- [ ] Add more testimonials/social proof
- [ ] Implement scroll-based section animations
- [ ] Add newsletter signup in footer
- [ ] Create custom 404 page for marketing routes

### Medium Term

- [ ] Add blog section for product updates
- [ ] Implement dark mode toggle
- [ ] Create press kit / media page
- [ ] Add customer testimonial carousel
- [ ] Implement cookie consent banner (if needed)

### Long Term

- [ ] A/B testing framework for CTAs
- [ ] Analytics integration (privacy-focused)
- [ ] Localization/internationalization
- [ ] SEO optimization improvements
- [ ] Video embedding for product demos

---

## File Structure Reference

Complete file tree for marketing site:

```
packages/frontend/src/
├── app/
│   ├── (marketing)/
│   │   ├── layout.tsx              # Marketing layout with footer
│   │   ├── page.tsx                # Landing page (/)
│   │   ├── why/
│   │   │   └── page.tsx            # Manifesto (/why)
│   │   ├── waitlist/
│   │   │   └── page.tsx            # Waitlist (/waitlist)
│   │   └── future/
│   │       └── page.tsx            # Future vision (/future)
│   ├── layout.tsx                  # Root layout with MainNav
│   ├── globals.css                 # Global styles
│   └── middleware.ts               # Clerk auth middleware
│
├── components/
│   ├── marketing/
│   │   ├── header.tsx              # (Unused - nav in root layout)
│   │   ├── footer.tsx              # Marketing footer
│   │   └── hero-animation.tsx      # Landing page animation
│   └── navigation/
│       └── main-nav.tsx            # Unified header
│
└── [other app files]
```

---

## Maintenance

### Regular Updates

**Monthly:**
- Update dependencies (`pnpm update`)
- Review and update roadmap on `/future` page
- Check for broken links
- Review analytics (once implemented)

**Quarterly:**
- Refresh testimonials/social proof
- Update screenshots/demos
- Review and optimize SEO
- Update pricing/waitlist messaging

**As Needed:**
- Update Google Form if waitlist changes
- Modify copy based on user feedback
- A/B test headline variations
- Add new features to `/future` roadmap

---

## Support and Contact

For questions about the marketing site implementation:

- **Documentation Issues:** Open issue in GitHub repo
- **Design Questions:** Reference UX Design Specification doc
- **Technical Issues:** Check Common Issues section above
- **Content Updates:** Follow Content Guidelines section

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Author:** Claude (AI Assistant)
**Maintained By:** Delight Team

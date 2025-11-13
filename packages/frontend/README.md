# Delight Frontend

**A story for ambitious people who want to transform their lives**

The frontend application for Delight, a self-improvement companion platform that blends emotionally-aware AI coaching with narrative world-building. Built with Next.js 15, React 19, and TypeScript.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Getting Started](#getting-started)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Component Architecture](#component-architecture)
7. [Styling & Theming](#styling--theming)
8. [API Integration](#api-integration)
9. [Authentication](#authentication)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Contributing](#contributing)
13. [Troubleshooting](#troubleshooting)
14. [Shared Types](#shared-types)
15. [Quick Reference](#quick-reference)
16. [Related Documentation](#related-documentation)

---

## Overview

### Vision

Delight is **not just a companion app**—it's **a story for ambitious people who want to transform their lives**. The product blends real-world goal achievement with narrative world-building, where users' actual work drives a personalized, AI-generated story with persistent characters, meaningful stakes, and visible transformation.

### Core Features

- **Eliza Companion**: An empathetic AI companion that guides users through their journey
- **Mission System**: Adaptive micro-quests that correspond to real-world goals
- **Narrative World**: Living story world with zones (Arena, Observatory, Commons) that adapt to user progress
- **Progress Dashboard**: Multi-dimensional progress tracking with streaks, Essence, and attribute levels
- **Time-Aware World**: World state changes based on real-world time (morning, afternoon, evening, night)
- **Multiple Scenarios**: Choose from Modern Reality, Medieval Fantasy, Sci-Fi, Cyberpunk, and more
- **Character Relationships**: Build relationships with AI characters (Lyra, Thorne, Elara) through meaningful interactions

### Key Differentiators

- **Story-driven productivity**: Real work generates narrative progression
- **AI-generated personalization**: Stories adapt to user context and goals
- **Living world with time dynamics**: World state changes based on real-world time
- **Deep companion relationships**: Named protagonist (Eliza) + attribute-based characters
- **Multiple narrative scenarios**: Rich, pre-planned storylines with hidden quests

---

## Tech Stack

### Core Framework

- **Next.js 15** - React framework with App Router, Server Components, and streaming support
- **React 19** - UI library with latest hooks (`useActionState`, `useOptimistic`)
- **TypeScript** - Type safety across the entire frontend

### UI & Styling

- **Tailwind CSS** - Utility-first CSS framework with theme system
- **shadcn/ui** - Accessible component primitives (Radix UI + Tailwind)
- **Framer Motion** - Animation library for character breathing, transitions, and micro-interactions
- **class-variance-authority** - Component variant management
- **clsx** + **tailwind-merge** - Conditional class utilities

### Authentication

- **Clerk** - Managed authentication service (OAuth, 2FA, magic links)

### Testing

- **Playwright** - End-to-end testing framework
- **@faker-js/faker** - Test data generation

### Development Tools

- **ESLint** - Code linting (Next.js config)
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

---

## Getting Started

### Prerequisites

- **Node.js** 20.x or higher
- **pnpm** 8.x or higher (or npm/yarn)
- **Clerk Account** - For authentication (free tier available)
- **Backend API** - Running FastAPI backend (see `packages/backend/README.md`)

### Installation

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.local.example .env.local

# Edit .env.local with your configuration:
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Environment Variables

Create a `.env.local` file in the `packages/frontend` directory:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Clerk Secret Key (for server-side operations)
CLERK_SECRET_KEY=sk_test_...
```

### Running the Development Server

```bash
# Start development server (http://localhost:3000)
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linting
pnpm lint
```

### Verifying Setup

1. Open http://localhost:3000
2. You should see the Delight homepage
3. Click "Sign Up" to test Clerk authentication
4. After signing in, you should be redirected to `/dashboard`

---

## Project Structure

```
packages/frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Auth routes (sign-in, sign-up)
│   │   ├── (world)/           # World/zone routes (future)
│   │   │   ├── arena/        # Arena zone
│   │   │   ├── observatory/  # Observatory zone
│   │   │   └── commons/      # Commons zone
│   │   ├── companion/         # Eliza chat interface (future)
│   │   ├── missions/         # Mission views (future)
│   │   ├── progress/         # Dashboard, DCI (future)
│   │   ├── dashboard/        # Main dashboard
│   │   ├── layout.tsx        # Root layout with ClerkProvider
│   │   ├── page.tsx          # Homepage
│   │   └── globals.css       # Global styles
│   │
│   ├── components/           # React components
│   │   ├── ui/               # shadcn/ui components (to be added)
│   │   ├── companion/        # Eliza, character components (future)
│   │   ├── missions/         # Mission cards, progress bars (future)
│   │   ├── world/            # Zone components, time display (future)
│   │   ├── narrative/       # Story text, dialogue (future)
│   │   └── layout/           # Layout components
│   │
│   ├── lib/                  # Utilities and helpers
│   │   ├── api/              # API client, SSE handlers (future)
│   │   ├── hooks/            # Custom React hooks (future)
│   │   ├── utils/            # Utility functions (future)
│   │   └── themes/           # Theme system (medieval, sci-fi, etc.) (future)
│   │
│   └── types/                # TypeScript type definitions (future)
│
├── public/                    # Static assets
│   ├── images/               # Images, illustrations
│   └── favicon.ico           # Favicon
│
├── tests/                     # Test files
│   ├── e2e/                  # Playwright E2E tests
│   │   ├── auth.spec.ts      # Authentication tests
│   │   └── example.spec.ts   # Example tests
│   └── support/              # Test utilities
│       ├── fixtures/         # Test data factories
│       └── helpers/          # Test helpers
│
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── next.config.js             # Next.js configuration
├── playwright.config.ts       # Playwright configuration
└── package.json               # Dependencies and scripts
```

### Key Directories

**`src/app/`** - Next.js App Router pages

- Uses file-based routing
- Server Components by default
- Supports layouts, loading states, error boundaries

**`src/components/`** - Reusable React components

- Organized by feature domain
- Co-located with related components
- Follows component composition patterns

**`src/lib/`** - Shared utilities and helpers

- API clients, hooks, utilities
- Theme configuration
- Business logic helpers

**`public/`** - Static assets

- Images, fonts, icons
- Served at root URL (`/favicon.ico`)

---

## Development Workflow

### Code Style

- **TypeScript**: Strict mode enabled, prefer explicit types
- **ESLint**: Next.js recommended rules
- **Formatting**: Prettier (via ESLint integration)
- **Naming**:
  - Components: `PascalCase` (e.g., `MissionCard.tsx`)
  - Hooks: `camelCase` with `use` prefix (e.g., `useMission`)
  - Utils: `camelCase` (e.g., `formatEssence`)

### Component Development

1. **Create component file** in appropriate directory:

   ```tsx
   // src/components/missions/MissionCard.tsx
   export function MissionCard({ mission }: { mission: Mission }) {
     return <div>...</div>;
   }
   ```

2. **Add TypeScript types**:

   ```tsx
   import type { Mission } from "@/types/mission";
   ```

3. **Use Tailwind classes** for styling:

   ```tsx
   <div className="rounded-lg bg-card p-6 shadow">
   ```

4. **Export from index** (optional, for cleaner imports):
   ```tsx
   // src/components/missions/index.ts
   export { MissionCard } from "./MissionCard";
   ```

### Adding New Pages

1. **Create page file** in `src/app/`:

   ```tsx
   // src/app/missions/page.tsx
   export default function MissionsPage() {
     return <div>Missions</div>;
   }
   ```

2. **Add metadata** (optional):

   ```tsx
   import type { Metadata } from "next";

   export const metadata: Metadata = {
     title: "Missions - Delight",
   };
   ```

3. **Use Server Components** by default, add `'use client'` only when needed

### API Integration

See [API Integration](#api-integration) section for details on connecting to the backend.

### Git Workflow

1. Create feature branch: `git checkout -b feature/mission-card`
2. Make changes and commit: `git commit -m "Add MissionCard component"`
3. Push and create PR: `git push origin feature/mission-card`
4. Follow PR template and request review

---

## Component Architecture

### Design Principles

1. **Server Components First**: Use Server Components by default, only add `'use client'` when needed
2. **Component Composition**: Build complex UIs from simple, reusable components
3. **Type Safety**: Leverage TypeScript for props, state, and API responses
4. **Accessibility**: Use semantic HTML and ARIA attributes (shadcn/ui handles this)
5. **Performance**: Optimize images, lazy load components, use React Suspense

### Component Categories

#### 1. UI Components (`components/ui/`)

Base components from shadcn/ui:

- Button, Card, Input, Dialog, etc.
- Accessible, customizable, theme-aware

**Example:**

```tsx
import { Button } from "@/components/ui/button";

<Button variant="primary" size="lg">
  Start Mission
</Button>;
```

#### 2. Feature Components (`components/{feature}/`)

Domain-specific components:

- `components/companion/` - Eliza chat interface
- `components/missions/` - Mission cards, progress bars
- `components/world/` - Zone navigation, time display
- `components/narrative/` - Story paragraphs, dialogue

**Example:**

```tsx
// components/missions/MissionCard.tsx
export function MissionCard({ mission }: MissionCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{mission.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <MissionProgress mission={mission} />
      </CardContent>
    </Card>
  );
}
```

#### 3. Layout Components (`components/layout/`)

Page structure components:

- Header, Footer, Sidebar
- Navigation, Breadcrumbs

### Component Patterns

#### Server Component Pattern

```tsx
// Server Component (default)
export default async function MissionsPage() {
  const missions = await fetchMissions(); // Server-side fetch

  return <MissionList missions={missions} />;
}
```

#### Client Component Pattern

```tsx
"use client";

import { useState } from "react";

export function MissionCard({ mission }: MissionCardProps) {
  const [isActive, setIsActive] = useState(false);

  return <div onClick={() => setIsActive(!isActive)}>...</div>;
}
```

#### Compound Component Pattern

```tsx
// MissionCard.tsx
export function MissionCard({ children }: { children: React.ReactNode }) {
  return <Card>{children}</Card>
}

MissionCard.Header = function Header({ title }: { title: string }) {
  return <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
}

MissionCard.Content = function Content({ children }: { children: React.ReactNode }) {
  return <CardContent>{children}</CardContent>
}

// Usage:
<MissionCard>
  <MissionCard.Header title="Morning Workout" />
  <MissionCard.Content>...</MissionCard.Content>
</MissionCard>
```

---

## Styling & Theming

### Tailwind CSS

Delight uses Tailwind CSS with a custom theme system that supports multiple narrative scenarios.

#### Base Theme (Efficient Mode)

```css
/* Base colors */
--background: 248 249 250; /* Soft whites */
--foreground: 44 62 80; /* Dark charcoal */

/* Primary (warm amber/gold) */
--primary: 255 159 67; /* #FF9F43 */

/* Secondary (soft purple/blue) */
--secondary: 165 94 234; /* #A55EEA */
```

#### Scenario Themes

The theme system supports multiple narrative scenarios:

- **Modern Reality**: Urban blues, neon accents
- **Medieval Fantasy**: Earth tones, gold accents
- **Star Trek 2000s**: Cool blues, cyan holographic
- **Cyberpunk**: Dark backgrounds, neon pink/cyan
- **Zombie Apocalypse**: Desaturated colors, red accents

#### Using Themes

```tsx
// Theme is applied via data attribute on <html>
<html data-theme="medieval">
  {/* Components automatically adapt */}
</html>

// Or use Tailwind classes with theme variables
<div className="bg-primary text-primary-foreground">
  {/* Uses current theme's primary color */}
</div>
```

### Custom Utilities

```tsx
// Tailwind utilities
<div className="rounded-lg bg-card p-6 shadow">
  <h2 className="text-2xl font-bold text-foreground">Mission Title</h2>
</div>;

// Custom animations (Framer Motion)
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>;
```

### Responsive Design

```tsx
// Mobile-first approach
<div
  className="
  p-4           /* Mobile: 1rem */
  md:p-6        /* Tablet: 1.5rem */
  lg:p-8        /* Desktop: 2rem */
"
>
  Content
</div>
```

**Breakpoints:**

- Mobile: `< 768px` (default)
- Tablet: `768px - 1279px` (`md:`)
- Desktop: `≥ 1280px` (`lg:`)

---

## API Integration

### API Client Setup

Create an API client utility for backend communication:

```tsx
// src/lib/api/client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

### Server-Side API Calls

```tsx
// src/app/missions/page.tsx (Server Component)
async function fetchMissions() {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/missions`,
    {
      cache: "no-store", // Or 'force-cache' for static data
    }
  );
  return res.json();
}

export default async function MissionsPage() {
  const missions = await fetchMissions();
  return <MissionList missions={missions} />;
}
```

### Client-Side API Calls

```tsx
// src/components/missions/MissionCard.tsx (Client Component)
"use client";

import { useState } from "react";
import { apiRequest } from "@/lib/api/client";

export function MissionCard({ mission }: MissionCardProps) {
  const [status, setStatus] = useState(mission.status);

  async function startMission() {
    try {
      await apiRequest(`/missions/${mission.id}/start`, {
        method: "POST",
      });
      setStatus("active");
    } catch (error) {
      console.error("Failed to start mission:", error);
    }
  }

  return <button onClick={startMission}>Start Mission</button>;
}
```

### SSE Streaming (AI Responses)

```tsx
// src/lib/api/sse.ts
export function createSSEStream(
  endpoint: string,
  onMessage: (data: string) => void
) {
  const eventSource = new EventSource(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sse${endpoint}`
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data.content);
  };

  return () => eventSource.close();
}

// Usage in component:
("use client");

import { useEffect, useState } from "react";
import { createSSEStream } from "@/lib/api/sse";

export function CompanionChat() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const cleanup = createSSEStream("/companion/stream", (token) => {
      setMessage((prev) => prev + token);
    });

    return cleanup;
  }, []);

  return <div>{message}</div>;
}
```

### Error Handling

```tsx
// src/lib/api/errors.ts
export class APIError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
    this.name = "APIError";
  }
}

// Usage:
try {
  await apiRequest("/missions/123/start", { method: "POST" });
} catch (error) {
  if (error instanceof APIError) {
    // Handle specific error
    toast.error(error.message);
  } else {
    // Handle generic error
    toast.error("Something went wrong");
  }
}
```

---

## Authentication

Delight uses **Clerk** for authentication. Clerk handles OAuth, 2FA, magic links, and session management.

### Setup

1. **Create Clerk Application**: https://dashboard.clerk.com
2. **Get API Keys**: Copy publishable key and secret key
3. **Configure Environment Variables**: Add to `.env.local`
4. **Wrap App with ClerkProvider**: Already done in `src/app/layout.tsx`

### Using Authentication

#### Server Components

```tsx
import { auth } from "@clerk/nextjs/server";

export default async function DashboardPage() {
  const { userId } = await auth();

  if (!userId) {
    redirect("/sign-in");
  }

  return <div>Dashboard for user {userId}</div>;
}
```

#### Client Components

```tsx
"use client";

import { useUser } from "@clerk/nextjs";

export function UserProfile() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) return <div>Loading...</div>;

  return <div>Hello, {user?.firstName}!</div>;
}
```

#### Protected Routes

Routes are protected by default via `src/middleware.ts`. Public routes are:

- `/` (homepage)
- `/sign-in`
- `/sign-up`
- `/api/v1/webhooks/*`

All other routes require authentication.

### User Data

Clerk user IDs are used as the primary identifier in the backend database. User data is stored in Clerk, not in our database.

---

## Testing

### E2E Testing with Playwright

```bash
# Run all E2E tests
pnpm test:e2e

# Run tests in UI mode
pnpm test:e2e:ui

# Run tests in headed mode (see browser)
pnpm test:e2e:headed

# Debug tests
pnpm test:e2e:debug

# View test report
pnpm test:report
```

### Test Structure

```
tests/
├── e2e/
│   ├── auth.spec.ts          # Authentication tests
│   ├── missions.spec.ts      # Mission flow tests (future)
│   └── companion.spec.ts     # Companion chat tests (future)
└── support/
    ├── fixtures/             # Test data factories
    │   ├── user-factory.ts
    │   ├── mission-factory.ts
    │   └── companion-factory.ts
    └── helpers/             # Test utilities
        ├── auth.ts          # Auth helpers
        └── wait.ts          # Wait utilities
```

### Writing Tests

```tsx
// tests/e2e/missions.spec.ts
import { test, expect } from "@playwright/test";
import { login } from "../support/helpers/auth";

test.describe("Missions", () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto("/missions");
  });

  test("should display mission list", async ({ page }) => {
    await expect(page.locator('[data-testid="mission-list"]')).toBeVisible();
  });

  test("should start a mission", async ({ page }) => {
    await page.click('[data-testid="start-mission-button"]');
    await expect(page.locator('[data-testid="mission-active"]')).toBeVisible();
  });
});
```

### Test Data Factories

```tsx
// tests/support/fixtures/mission-factory.ts
import { faker } from "@faker-js/faker";

export function createMission(overrides?: Partial<Mission>): Mission {
  return {
    id: faker.string.uuid(),
    title: faker.lorem.sentence(),
    description: faker.lorem.paragraph(),
    duration_minutes: faker.number.int({ min: 10, max: 60 }),
    essence_reward: faker.number.int({ min: 10, max: 100 }),
    attribute_type: faker.helpers.arrayElement([
      "Growth",
      "Health",
      "Craft",
      "Connection",
    ]),
    status: "pending",
    ...overrides,
  };
}
```

---

## Deployment

### Vercel (Recommended)

Delight frontend is optimized for Vercel deployment:

1. **Connect Repository**: Link GitHub repo to Vercel
2. **Configure Environment Variables**: Add `.env.local` variables in Vercel dashboard
3. **Deploy**: Automatic deployments on push to `main`

**Vercel Configuration:**

```json
// vercel.json (optional)
{
  "buildCommand": "pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install",
  "framework": "nextjs",
  "regions": ["iad1"] // US East (or your preference)
}
```

### Environment Variables

Set these in Vercel dashboard:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_API_URL` (production backend URL)
- `CLERK_SECRET_KEY` (for server-side operations)

### Build & Deploy

```bash
# Build locally to test
pnpm build

# Start production server locally
pnpm start

# Deploy to Vercel (via Git push)
git push origin main
```

### Performance Optimization

- **Image Optimization**: Use `next/image` for all images
- **Code Splitting**: Automatic via Next.js App Router
- **Static Generation**: Use `generateStaticParams` where possible
- **Caching**: Configure `revalidate` for ISR (Incremental Static Regeneration)

---

## Contributing

### Development Setup

1. **Fork and Clone**: Fork the repo and clone locally
2. **Install Dependencies**: `pnpm install`
3. **Set Up Environment**: Copy `.env.local.example` to `.env.local`
4. **Start Dev Server**: `pnpm dev`

### Code Standards

- **TypeScript**: Use strict mode, prefer explicit types
- **Components**: Server Components by default, Client Components only when needed
- **Styling**: Tailwind CSS utility classes, avoid inline styles
- **Testing**: Write E2E tests for critical user flows
- **Accessibility**: Use semantic HTML, ARIA attributes where needed

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Make Changes**: Follow code standards
3. **Write Tests**: Add E2E tests for new features
4. **Update Documentation**: Update README if needed
5. **Create PR**: Fill out PR template, request review

### PR Checklist

- [ ] Code follows TypeScript and ESLint rules
- [ ] Components are accessible (keyboard navigation, screen readers)
- [ ] E2E tests pass
- [ ] No console errors or warnings
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Documentation updated if needed

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Windows
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :3000

# Kill process or use different port
PORT=3001 pnpm dev
```

#### Clerk Authentication Not Working

1. Check `.env.local` has correct Clerk keys
2. Verify Clerk dashboard has correct redirect URLs
3. Check browser console for errors
4. Ensure middleware is configured correctly

#### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
pnpm install

# Rebuild
pnpm build
```

#### Type Errors

```bash
# Regenerate TypeScript types
pnpm build

# Check tsconfig.json paths are correct
```

### Getting Help

1. Check [Architecture Docs](../../docs/ARCHITECTURE.md)
2. Review [UX Design Spec](../../docs/ux-design-specification.md)
3. Ask in project Discord/Slack
4. Create GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Node version, etc.)

---

## Shared Types

Delight uses a monorepo structure with shared TypeScript types between frontend and backend.

### Using Shared Types

```tsx
// Import from shared package
import type { Mission, Character, NarrativeState } from "@delight/shared/types";

// Use in components
export function MissionCard({ mission }: { mission: Mission }) {
  return <div>{mission.title}</div>;
}
```

### Type Definitions

Shared types are located in `packages/shared/types/`:

- `mission.ts` - Mission types (status, attributes, rewards)
- `character.ts` - Character types (personality, relationships)
- `narrative.ts` - Narrative state types (chapters, quests)
- `progress.ts` - Progress tracking types (DCI, streaks, Essence)

### Adding New Types

1. **Add type definition** in `packages/shared/types/`:

   ```ts
   // packages/shared/types/mission.ts
   export interface Mission {
     id: string;
     title: string;
     // ...
   }
   ```

2. **Export from index**:

   ```ts
   // packages/shared/index.ts
   export * from "./types/mission";
   ```

3. **Use in frontend**:
   ```tsx
   import type { Mission } from "@delight/shared";
   ```

---

## Quick Reference

### Common Commands

```bash
# Development
pnpm dev                    # Start dev server (localhost:3000)
pnpm build                  # Build for production
pnpm start                  # Start production server
pnpm lint                   # Run ESLint

# Testing
pnpm test:e2e               # Run E2E tests
pnpm test:e2e:ui            # Run tests in UI mode
pnpm test:e2e:headed        # Run tests with browser visible
pnpm test:report            # View test report
```

### File Paths

```bash
# Pages
src/app/page.tsx            # Homepage
src/app/dashboard/page.tsx   # Dashboard
src/app/sign-in/...         # Sign in page

# Components
src/components/ui/          # shadcn/ui components
src/components/missions/     # Mission components (future)
src/components/companion/    # Eliza components (future)

# Utilities
src/lib/api/                # API client
src/lib/hooks/              # Custom hooks
src/lib/utils/              # Utility functions
```

### Environment Variables

```env
# Required
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional (server-side)
CLERK_SECRET_KEY=sk_test_...
```

### Key URLs

- **Frontend Dev**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Clerk Dashboard**: https://dashboard.clerk.com

### Component Patterns

```tsx
// Server Component (default)
export default async function Page() {
  const data = await fetchData()
  return <div>{data}</div>
}

// Client Component (when needed)
'use client'
import { useState } from 'react'
export function InteractiveComponent() {
  const [state, setState] = useState()
  return <div onClick={() => setState(...)}>...</div>
}
```

### Styling Patterns

```tsx
// Tailwind utilities
<div className="rounded-lg bg-card p-6 shadow">

// Theme-aware colors
<div className="bg-primary text-primary-foreground">

// Responsive
<div className="p-4 md:p-6 lg:p-8">
```

---

## Related Documentation

- **Architecture Overview**: [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md)
- **UX Design Specification**: [`docs/ux-design-specification.md`](../../docs/ux-design-specification.md)
- **Product Brief**: [`docs/brainstorming/product-brief-Delight-2025-11-09.md`](../../docs/brainstorming/product-brief-Delight-2025-11-09.md)
- **Backend README**: [`packages/backend/README.md`](../backend/README.md)
- **Setup Guide**: [`docs/dev/SETUP.md`](../../docs/dev/SETUP.md)

---

## License

[Add your license here]

---

**Version:** 0.1.0  
**Last Updated:** 2025-11-12
**Maintainer:** Delight Team

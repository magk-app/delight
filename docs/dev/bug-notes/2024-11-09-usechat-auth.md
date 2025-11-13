# Bug Note: useChat triggers `useAuth` outside `ClerkProvider`

## Symptom

Visiting the Companion chat page (`/companion`) in the frontend raises a runtime error: `@clerk/clerk-react: useAuth can only be used within the <ClerkProvider /> component.` The stack trace points to `src/lib/hooks/useChat.ts` line 28 when the hook executes.

## Scope

The failure blocks the entire Companion chat UI in the Next.js frontend (`packages/frontend`). Other routes remain functional. The issue affects authenticated experiences because the Clerk context is not available when `useChat` runs.

## Minimal Reproducer

1. Start the frontend (`pnpm dev` in `packages/frontend`).

2. Navigate to `http://localhost:3000/companion` after signing in with Clerk.

3. The page throws an error and displays the Clerk runtime exception.

## Hypotheses

1. **Layout loses Clerk context** — the app layout may not wrap children with `<ClerkProvider>` due to recent async header handling changes. I will inspect `src/app/layout.tsx` and confirm the provider hierarchy matches Clerk's Next.js 15 guidance.

2. **`useChat` imported on the server** — the hook might be evaluated during server rendering (e.g., via an async data fetch) before the provider exists. I will verify the hook is only used inside client components (`'use client'`) and that no server modules import it.

3. **Hook file drift** — prior edits may have deleted or relocated `src/lib/hooks/useChat.ts`, causing bundler fallbacks or stale compiled code. I will check the filesystem and ensure the hook file exists at the expected path and exports a client-safe implementation.

Next, I will falsify each hypothesis to isolate the root cause.

## Findings

- **Hypothesis 1 (Layout loses Clerk context): Confirmed.** `src/app/layout.tsx` wrapped `<ClerkProvider>` around `<html>`, which meant the provider did not mount inside the document body. Next.js 15 discarded the wrapper and the Clerk context never reached client components.

- **Hypothesis 2 (Hook imported on the server): Rejected.** `useChat` is only consumed inside `'use client'` components (`CompanionChat`, `MessageList`, `Message`).

- **Hypothesis 3 (Hook file drift): Confirmed.** `src/lib/hooks/useChat.ts` was absent from the repository, so earlier deploys served stale compiled output. Recreating the hook restores the client-side logic.

## Resolution

1. Restructured `RootLayout` so `<ClerkProvider>` renders inside `<body>`, guaranteeing every client component receives Clerk context.

2. Restored `useChat` with a client-safe implementation that waits for `useAuth` to load before requesting history or sending messages and that hardens SSE parsing.

3. Added a cleanup guard that always closes open EventSource streams when the hook unmounts, preventing leaked connections.

These changes ensure `useAuth` always executes within the provider tree, resolving the runtime error.

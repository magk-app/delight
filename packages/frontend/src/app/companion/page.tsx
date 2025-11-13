/**
 * Companion Page - Chat with Eliza
 *
 * Full-screen chat interface following UX spec design principles:
 * - Full-screen primary panel (not sidebar)
 * - Modern warmth: Clean lines + warm colors
 * - Mobile-responsive
 * - Protected by Clerk authentication
 */

import { CompanionChat } from '@/components/companion/CompanionChat';

/**
 * Companion Page
 *
 * Main entry point for chat with Eliza.
 * Protected by Clerk middleware (see middleware.ts).
 */
export default function CompanionPage() {
  return (
    <main className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            {/* Eliza Avatar */}
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center text-white text-lg font-bold">
              E
            </div>

            {/* Title */}
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Eliza</h1>
              <p className="text-sm text-gray-500">Your AI Companion</p>
            </div>
          </div>

          {/* Optional: User menu or settings */}
          <div className="flex items-center gap-2">
            {/* Placeholder for future features */}
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <CompanionChat />
    </main>
  );
}

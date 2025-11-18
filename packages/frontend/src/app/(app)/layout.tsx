/**
 * App Layout - Authenticated area layout with navigation
 * Wraps all authenticated pages (/dashboard, /missions, /memory, etc.)
 */

import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { AppNav } from "@/components/app/AppNav";

// Force dynamic rendering for Clerk
export const dynamic = "force-dynamic";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="container relative flex h-16 items-center justify-between px-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="text-2xl">✨</div>
            <span className="text-xl font-bold text-gray-900">Delight</span>
          </Link>

          {/* Navigation */}
          <AppNav />

          {/* User Menu */}
          <div className="flex items-center">
            <UserButton afterSignOutUrl="/" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}

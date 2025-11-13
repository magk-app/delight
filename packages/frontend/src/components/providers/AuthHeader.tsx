"use client";

import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";

/**
 * AuthHeader Component
 *
 * Client component for authentication UI.
 * Separated from layout to prevent server-side header access issues.
 */
export function AuthHeader() {
  return (
    <header className="fixed top-0 right-0 p-4 z-50">
      <SignedOut>
        <div className="flex gap-2">
          <SignInButton mode="modal">
            <button className="px-4 py-2 text-sm font-medium text-foreground hover:text-foreground/80 transition-colors">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
              Sign Up
            </button>
          </SignUpButton>
        </div>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </header>
  );
}

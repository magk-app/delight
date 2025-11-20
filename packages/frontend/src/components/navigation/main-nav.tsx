"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, MoveUpRight } from "lucide-react";
import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";

export function MainNav() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-6 flex justify-between items-center bg-transparent">
      {/* Logo and Brand */}
      <Link href="/" className="flex items-center gap-2 group">
        <div className="w-4 h-4 bg-white rounded-sm transition-transform group-hover:scale-105" />
        <div className="text-lg font-display font-bold tracking-tight text-white">
          Delight.
        </div>
      </Link>

      {/* Desktop Navigation */}
      <div className="hidden md:flex items-center gap-8">
        <Link
          href="/#product"
          className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
        >
          Product
        </Link>
        <Link
          href="/why"
          className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
        >
          Why Delight
        </Link>
        <Link
          href="/future"
          className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
        >
          Future
        </Link>
        <SignedIn>
          <Link
            href="/companion"
            className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
          >
            Companion
          </Link>
        </SignedIn>
        <Link
          href="/waitlist"
          className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
        >
          Waitlist
        </Link>
      </div>

      {/* Desktop CTA */}
      <div className="hidden md:flex items-center gap-4">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="text-xs font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="text-xs bg-white text-black px-6 py-3 rounded-full font-medium hover:bg-zinc-200 transition-colors flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)] transform hover:scale-105 duration-300">
              Enter Simulation <MoveUpRight size={12} />
            </button>
          </SignUpButton>
        </SignedOut>
        <SignedIn>
          <div className="text-white">
            <UserButton
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8",
                },
              }}
            />
          </div>
        </SignedIn>
      </div>

      {/* Mobile menu button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="md:hidden p-2 text-white transition-colors"
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="fixed top-0 left-0 right-0 bottom-0 bg-black z-50 pointer-events-auto md:hidden">
          <div className="px-6 py-6 flex flex-col h-full">
            {/* Mobile Header */}
            <div className="flex items-center justify-between mb-12">
              <Link
                href="/"
                className="flex items-center gap-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <div className="w-4 h-4 bg-white rounded-sm" />
                <div className="text-lg font-display font-bold tracking-tight text-white">
                  Delight.
                </div>
              </Link>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 text-white"
                aria-label="Close menu"
              >
                <X size={24} />
              </button>
            </div>

            {/* Mobile Navigation Links */}
            <div className="flex flex-col space-y-6 flex-1">
              <Link
                href="/#product"
                className="text-base font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
                onClick={() => setMobileMenuOpen(false)}
              >
                Product
              </Link>
              <Link
                href="/why"
                className="text-base font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
                onClick={() => setMobileMenuOpen(false)}
              >
                Why Delight
              </Link>
              <Link
                href="/future"
                className="text-base font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
                onClick={() => setMobileMenuOpen(false)}
              >
                Future
              </Link>
              <SignedIn>
                <Link
                  href="/companion"
                  className="text-base font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Companion
                </Link>
              </SignedIn>
              <Link
                href="/waitlist"
                className="text-base font-medium text-white/80 hover:text-white transition-colors uppercase tracking-widest"
                onClick={() => setMobileMenuOpen(false)}
              >
                Waitlist
              </Link>

              {/* Mobile Auth Buttons */}
              <div className="pt-8 border-t border-white/10 flex flex-col space-y-4 mt-auto">
                <SignedOut>
                  <SignInButton mode="modal">
                    <button
                      className="w-full text-base font-medium text-center text-white/80 hover:text-white transition-colors uppercase tracking-widest py-3"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Sign In
                    </button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <button
                      className="w-full text-xs bg-white text-black px-6 py-3 rounded-full font-medium hover:bg-zinc-200 transition-colors flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.2)]"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Enter Simulation <MoveUpRight size={12} />
                    </button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <div className="flex justify-center py-3">
                    <UserButton afterSignOutUrl="/" />
                  </div>
                </SignedIn>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}

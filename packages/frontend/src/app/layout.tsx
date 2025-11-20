import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { MainNav } from "@/components/navigation/main-nav";
import { Space_Grotesk } from "next/font/google";
import "./globals.css";

// Only load Space Grotesk for headings - MUCH faster!
// Body text uses system fonts (no download needed)
const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "700"], // Only 2 weights instead of 11!
  variable: "--font-display",
  display: "optional", // Don't block render waiting for fonts
  preload: true,
  fallback: ["system-ui", "sans-serif"],
});

export const metadata: Metadata = {
  title: "Delight - AI-Powered Self-Improvement Companion",
  description:
    "Transform your ambitions into achievement, one mission at a time",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className={`${spaceGrotesk.variable}`} suppressHydrationWarning>
          <MainNav />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}

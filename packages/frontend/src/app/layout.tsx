import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { MainNav } from "@/components/navigation/main-nav";
import { Inter, Space_Grotesk, Dancing_Script } from "next/font/google";
import "./globals.css";

// Optimized font loading - self-hosted, no external requests
const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

const dancingScript = Dancing_Script({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-signature",
  display: "swap",
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
        <body className={`font-sans ${inter.variable} ${spaceGrotesk.variable} ${dancingScript.variable}`} suppressHydrationWarning>
          <MainNav />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}

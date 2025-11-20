import type { Metadata } from "next";
// import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { MainNav } from "@/components/navigation/main-nav";
import "./globals.css";

// const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Delight - AI-Powered Self-Improvement Companion",
  description:
    "Transform your ambitions into achievement, one mission at a time",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5, // Allow zoom for accessibility, but inputs are 16px+ to prevent auto-zoom
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
        <body className="font-sans bg-slate-950" suppressHydrationWarning>
          <MainNav />
          <div className="pt-16">{children}</div>
        </body>
      </html>
    </ClerkProvider>
  );
}

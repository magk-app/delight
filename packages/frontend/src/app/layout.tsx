import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { MainNav } from "@/components/navigation/main-nav";
import "./globals.css";

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
        <body className="font-sans" suppressHydrationWarning>
          <MainNav />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}

import { MarketingFooter } from "@/components/marketing/footer";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Navigation is handled by root layout MainNav */}
      <main className="flex-1">{children}</main>
      <MarketingFooter />
    </div>
  );
}

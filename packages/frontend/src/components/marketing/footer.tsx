import Link from "next/link";
import { Github } from "lucide-react";

export function MarketingFooter() {
  return (
    <footer className="border-t border-border bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center space-x-2 group mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <span className="text-xl font-semibold text-foreground">Delight</span>
            </Link>
            <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
              An emotionally intelligent AI companion that transforms overwhelming goals into achievable daily missions.
              Built with trust, control, and exportability at its core.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/#product" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  How it Works
                </Link>
              </li>
              <li>
                <Link href="/why" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Why Delight
                </Link>
              </li>
              <li>
                <Link href="/future" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Future Vision
                </Link>
              </li>
              <li>
                <Link href="/waitlist" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Join Waitlist
                </Link>
              </li>
            </ul>
          </div>

          {/* Connect */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">Connect</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/magk-app/delight"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
                >
                  <Github size={14} />
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            © {new Date().getFullYear()} Delight. Built with care for ambitious people transforming their lives.
          </p>
        </div>
      </div>
    </footer>
  );
}

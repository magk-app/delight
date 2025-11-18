'use client';

/**
 * AppNav - Main navigation component for authenticated app
 * Shows top-level navigation: Dashboard, Missions, Memory, Narrative, Progress, Lab
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { href: '/missions', label: 'Missions', icon: '⚔️' },
  { href: '/memory', label: 'Memory', icon: '🧠' },
  { href: '/narrative', label: 'Narrative', icon: '📖' },
  { href: '/progress', label: 'Progress', icon: '📊' },
  { href: '/lab', label: 'Lab', icon: '🧪' },
];

export function AppNav() {
  const pathname = usePathname();

  return (
    <nav className="hidden md:flex items-center space-x-6">
      {NAV_ITEMS.map((item) => {
        const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center space-x-1.5 text-sm font-medium transition-colors hover:text-primary',
              isActive ? 'text-primary' : 'text-muted-foreground'
            )}
          >
            <span className="text-base">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

/**
 * QuickJumpTiles - Quick access tiles to main app sections
 */

'use client';

import Link from 'next/link';

const QUICK_JUMP_TILES = [
  {
    href: '/memory',
    icon: '🧠',
    title: 'Memory Studio',
    description: 'Explore and organize your 3-tier memory',
  },
  {
    href: '/narrative',
    icon: '📖',
    title: 'View My Story',
    description: 'Read your personalized narrative journey',
  },
  {
    href: '/lab',
    icon: '🧪',
    title: 'Open Lab',
    description: 'Experiment with AI agents and memory',
  },
  {
    href: '/progress',
    icon: '📊',
    title: 'Progress Dashboard',
    description: 'Deep dive into analytics and insights',
  },
];

export function QuickJumpTiles() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Quick Jump</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_JUMP_TILES.map((tile) => (
          <Link
            key={tile.href}
            href={tile.href}
            className="group rounded-lg border bg-white p-6 shadow-sm transition-all hover:shadow-md hover:border-primary/50"
          >
            <div className="mb-3 text-4xl">{tile.icon}</div>
            <h3 className="mb-1 text-lg font-semibold text-gray-900 group-hover:text-primary transition-colors">
              {tile.title}
            </h3>
            <p className="text-sm text-gray-600">{tile.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

/**
 * Landing Page - Root of the application
 * Redirects authenticated users to /dashboard
 * Shows welcome screen for unauthenticated users
 */

import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function LandingPage() {
  // Check if user is authenticated
  const { userId } = await auth();

  // Redirect authenticated users to dashboard
  if (userId) {
    redirect('/dashboard');
  }

  // Show landing page for unauthenticated users
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 text-6xl">✨</div>
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to Delight
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Transform your ambitions into achievement, one mission at a time.
            <br />
            Your emotionally intelligent AI companion for meaningful progress.
          </p>

          {/* CTA Buttons */}
          <div className="flex gap-4 justify-center">
            <Link
              href="/sign-up"
              className="px-8 py-4 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 transition-colors shadow-lg"
            >
              Get Started
            </Link>
            <Link
              href="/sign-in"
              className="px-8 py-4 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-50 transition-colors border-2 border-gray-200"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          <FeatureCard
            icon="🎯"
            title="Goal Management"
            description="Break down overwhelming goals into achievable daily missions"
          />
          <FeatureCard
            icon="🧠"
            title="3-Tier Memory"
            description="AI that remembers your journey and adapts to your patterns"
          />
          <FeatureCard
            icon="📖"
            title="Living Narrative"
            description="Your progress becomes a personalized story that evolves"
          />
          <FeatureCard
            icon="📊"
            title="Progress Analytics"
            description="Track consistency with DCI scores, streaks, and insights"
          />
        </div>

        {/* Value Categories */}
        <div className="mt-24 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">
            Four Dimensions of Growth
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <ValueCard
              icon="💪"
              title="Health"
              description="Physical wellness, exercise, nutrition"
              color="bg-green-100 text-green-700"
            />
            <ValueCard
              icon="🎨"
              title="Craft"
              description="Creative output, building, making"
              color="bg-amber-100 text-amber-700"
            />
            <ValueCard
              icon="🌱"
              title="Growth"
              description="Learning, wisdom, self-development"
              color="bg-purple-100 text-purple-700"
            />
            <ValueCard
              icon="🤝"
              title="Connection"
              description="Relationships, community, meaning"
              color="bg-indigo-100 text-indigo-700"
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-24 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-gray-600">
          <p>Delight - Your companion for meaningful progress</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="p-6 rounded-lg border bg-white hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}

function ValueCard({
  icon,
  title,
  description,
  color,
}: {
  icon: string;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div className={`p-6 rounded-lg ${color}`}>
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm opacity-90">{description}</p>
    </div>
  );
}

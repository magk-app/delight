// Force dynamic rendering to work with Clerk middleware (Next.js 15)
export const dynamic = "force-dynamic";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div data-testid="user-menu">
            {/* User menu components can go here */}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">Welcome to Delight!</h2>
          <p className="text-gray-600 mb-8">
            Your personalized dashboard is coming soon. We&apos;re building
            something special for you.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="p-6 border rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Your Progress</h3>
              <p className="text-sm text-gray-600">
                Track your goals and achievements
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Active Missions</h3>
              <p className="text-sm text-gray-600">
                See your current quests and missions
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Companion</h3>
              <p className="text-sm text-gray-600">
                Chat with your AI companion
              </p>
            </div>
          </div>

          {/* Link to experimental features */}
          <div className="mt-8 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🧪</span>
              <div>
                <h3 className="font-semibold text-purple-900">Try Experimental Features</h3>
                <p className="text-sm text-purple-700 mt-1">
                  Want to test the AI chat with memory? Check out the experimental lab!
                </p>
                <a
                  href="/experimental"
                  className="inline-block mt-3 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Go to Experimental Lab →
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

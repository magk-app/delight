export default function DashboardPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-center">
        <h1 className="text-4xl font-bold mb-4">Dashboard 🎯</h1>
        <p className="text-lg text-muted-foreground mb-8">
          Welcome to your Delight dashboard
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Your Progress</h2>
            <p className="text-sm text-muted-foreground">
              Track your goals and achievements
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Active Missions</h2>
            <p className="text-sm text-muted-foreground">
              See your current quests and missions
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Companion</h2>
            <p className="text-sm text-muted-foreground">
              Chat with your AI companion
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

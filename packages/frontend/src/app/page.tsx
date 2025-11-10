export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-center">
        <h1 className="text-4xl font-bold mb-4">
          Welcome to Delight 🎮✨
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Your AI-powered self-improvement companion
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Remembered Context</h2>
            <p className="text-sm text-muted-foreground">
              Every session starts with full awareness of your goals and progress
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Adaptive Missions</h2>
            <p className="text-sm text-muted-foreground">
              Break down overwhelming goals into achievable micro-quests
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Visible Progress</h2>
            <p className="text-sm text-muted-foreground">
              Streaks, highlights, and consistency tracking that builds trust
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}


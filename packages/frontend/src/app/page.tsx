import Link from "next/link";
import { HeroAnimation } from "@/components/marketing/hero-animation";
import {
  Brain,
  Sparkles,
  Target,
  TrendingUp,
  Heart,
  Zap,
  Calendar,
  BarChart3,
  Code2,
  Database,
  Cpu,
} from "lucide-react";

// Force dynamic rendering to work with Clerk middleware (Next.js 15)
export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background via-primary/5 to-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Copy */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
                  Turn overwhelming goals into{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                    adaptive daily missions
                  </span>
                </h1>

                <p className="text-lg text-muted-foreground leading-relaxed">
                  An emotionally intelligent AI companion that remembers your
                  journey, understands when you&apos;re stuck, and helps you
                  build momentum when stress threatens to derail your ambitions.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/waitlist"
                  className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl hover:scale-105"
                >
                  Join Waitlist
                </Link>
                <Link
                  href="/why"
                  className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-foreground border-2 border-border rounded-xl hover:border-primary/50 hover:bg-accent transition-all"
                >
                  Why we&apos;re building this
                </Link>
              </div>

              <p className="text-sm text-muted-foreground">
                For founders, students, and ambitious people navigating life
                transitions
              </p>
            </div>

            {/* Right: Interactive Animation */}
            <div className="lg:pl-8">
              <HeroAnimation />
            </div>
          </div>
        </div>
      </section>

      {/* Who It's For */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Built for ambitious people who stall
            </h2>
            <p className="text-lg text-muted-foreground">
              You know what to do. You just can&apos;t start. Or you start and
              immediately drift. Delight meets you there.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Founders */}
            <div className="bg-card border border-border rounded-2xl p-8 hover:border-primary/50 transition-all hover:shadow-lg">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                Founders & Operators
              </h3>
              <p className="text-muted-foreground mb-4">
                Juggling multiple projects, investors, and team leadership. You
                stall when stress spikes and priorities blur.
              </p>
              <p className="text-sm text-foreground/80 italic">
                &quot;After a tough board meeting, Eliza helped me break down a
                product launch into three focused missions. I shipped by
                Friday.&quot;
              </p>
            </div>

            {/* Students */}
            <div className="bg-card border border-border rounded-2xl p-8 hover:border-primary/50 transition-all hover:shadow-lg">
              <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                Ambitious Students
              </h3>
              <p className="text-muted-foreground mb-4">
                Balancing classes, side projects, and skill-building. You need
                structure that adapts to exam stress and creative bursts.
              </p>
              <p className="text-sm text-foreground/80 italic">
                &quot;Between midterms and my startup, I was drowning. Delight
                helped me maintain a 12-day streak without burning out.&quot;
              </p>
            </div>

            {/* Life Transitions */}
            <div className="bg-card border border-border rounded-2xl p-8 hover:border-primary/50 transition-all hover:shadow-lg">
              <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center mb-4">
                <Heart className="w-6 h-6 text-success" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                People in Transition
              </h3>
              <p className="text-muted-foreground mb-4">
                Career changes, relocations, or relationship goals that
                don&apos;t fit traditional task lists. You need nuanced
                coaching, not checkboxes.
              </p>
              <p className="text-sm text-foreground/80 italic">
                &quot;Moving to a new city felt abstract. Delight helped me
                decompose &apos;build community&apos; into weekly coffee chats
                and hobby meetups.&quot;
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Three Core Pillars */}
      <section id="product" className="py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              What makes Delight different
            </h2>
            <p className="text-lg text-muted-foreground">
              Most tools lead with structure and expect you to adapt. Delight
              leads with empathy, then layers structure.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Emotion-First */}
            <div className="space-y-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-secondary/20 to-primary/20 rounded-2xl blur-xl" />
                <div className="relative bg-card border border-border rounded-2xl p-8">
                  <div className="w-14 h-14 rounded-2xl bg-secondary/10 flex items-center justify-center mb-6">
                    <Heart className="w-8 h-8 text-secondary" />
                  </div>
                  <h3 className="text-2xl font-semibold text-foreground mb-4">
                    Emotion-first guidance
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    When you open Delight, it asks how you feel. Stressed? It
                    suggests smaller missions. Energized? It offers ambitious
                    challenges. The system meets you where you are instead of
                    demanding you meet rigid requirements.
                  </p>
                </div>
              </div>
              <div className="bg-secondary/5 border border-secondary/20 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-secondary mt-2" />
                  <div className="flex-1">
                    <p className="text-sm text-foreground/90 font-medium mb-1">
                      Learns your patterns
                    </p>
                    <p className="text-xs text-muted-foreground">
                      When you&apos;re most productive, what drains you, which
                      goals matter most
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Living Memory */}
            <div className="space-y-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-success/20 rounded-2xl blur-xl" />
                <div className="relative bg-card border border-border rounded-2xl p-8">
                  <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
                    <Brain className="w-8 h-8 text-primary" />
                  </div>
                  <h3 className="text-2xl font-semibold text-foreground mb-4">
                    Living memory that compounds
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Unlike chatbots that forget or productivity apps that
                    don&apos;t connect dots, Delight maintains a three-tier
                    memory system. Personal memories capture values and fears.
                    Project memories track goal context. Task memories ensure
                    mission-specific understanding.
                  </p>
                </div>
              </div>
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                  <div className="flex-1">
                    <p className="text-sm text-foreground/90 font-medium mb-1">
                      Remembers your journey
                    </p>
                    <p className="text-xs text-muted-foreground">
                      When you mention feeling stuck three weeks later, it
                      recalls the context and what worked before
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Adaptive Missions */}
            <div className="space-y-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-success/20 to-secondary/20 rounded-2xl blur-xl" />
                <div className="relative bg-card border border-border rounded-2xl p-8">
                  <div className="w-14 h-14 rounded-2xl bg-success/10 flex items-center justify-center mb-6">
                    <Target className="w-8 h-8 text-success" />
                  </div>
                  <h3 className="text-2xl font-semibold text-foreground mb-4">
                    Adaptive micro missions
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Abstract goals like &quot;get healthier&quot; don&apos;t
                    translate to action. Delight excels at collaborative goal
                    decomposition—breaking overwhelming ambitions into concrete,
                    time-boxed missions that fit your current energy level.
                  </p>
                </div>
              </div>
              <div className="bg-success/5 border border-success/20 rounded-xl p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 rounded-full bg-success mt-2" />
                  <div className="flex-1">
                    <p className="text-sm text-foreground/90 font-medium mb-1">
                      Flexes with you
                    </p>
                    <p className="text-xs text-muted-foreground">
                      10 minutes when exhausted, ambitious sprints when in flow
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Visible Progress */}
      <section className="py-20 bg-gradient-to-b from-background to-primary/5">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
                Visible progress that builds trust
              </h2>
              <p className="text-lg text-muted-foreground">
                Nothing kills motivation faster than invisible progress. Delight
                makes your effort tangible.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-card border border-border rounded-xl p-6 text-center hover:border-primary/50 transition-all">
                <div className="inline-flex w-12 h-12 rounded-full bg-primary/10 items-center justify-center mb-4">
                  <Calendar className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">Streaks</h3>
                <p className="text-sm text-muted-foreground">
                  Daily consistency without being punitive
                </p>
              </div>

              <div className="bg-card border border-border rounded-xl p-6 text-center hover:border-primary/50 transition-all">
                <div className="inline-flex w-12 h-12 rounded-full bg-secondary/10 items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-secondary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">
                  Highlight Reels
                </h3>
                <p className="text-sm text-muted-foreground">
                  Proof of work with notes and photos
                </p>
              </div>

              <div className="bg-card border border-border rounded-xl p-6 text-center hover:border-primary/50 transition-all">
                <div className="inline-flex w-12 h-12 rounded-full bg-success/10 items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-success" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">
                  Constellation
                </h3>
                <p className="text-sm text-muted-foreground">
                  Growth across four dimensions
                </p>
              </div>

              <div className="bg-card border border-border rounded-xl p-6 text-center hover:border-primary/50 transition-all">
                <div className="inline-flex w-12 h-12 rounded-full bg-primary/10 items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">
                  Consistency Index
                </h3>
                <p className="text-sm text-muted-foreground">
                  Nuanced scoring beyond streaks
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              How Delight works in practice
            </h2>
            <p className="text-lg text-muted-foreground">
              A simple loop that turns overwhelm into momentum
            </p>
          </div>

          <div className="max-w-4xl mx-auto space-y-8">
            {[
              {
                step: 1,
                title: "Check in with how you feel",
                description:
                  "Delight greets you and asks about your emotional state. Stressed, energized, or somewhere in between—your answer shapes what happens next.",
              },
              {
                step: 2,
                title: "Triage what matters next",
                description:
                  "Based on your goals, recent work, and current energy, Delight suggests three meaningful priorities. You're not choosing from an endless list—just what's important now.",
              },
              {
                step: 3,
                title: "Pick a mission-sized task",
                description:
                  "Select a mission that fits your bandwidth. The companion adjusts duration and difficulty. 10 minutes or 2 hours—you decide what feels right.",
              },
              {
                step: 4,
                title: "Work with gentle support",
                description:
                  "Complete your mission while the companion stays present. If you drift, it checks in: intentional break, or pulled away? No judgment, just awareness.",
              },
              {
                step: 5,
                title: "Capture proof and watch your world change",
                description:
                  "Mark the mission complete, optionally add notes or photos. Watch your streak grow, earn progress points, and see your constellation expand. The proof compounds over time.",
              },
            ].map((item) => (
              <div key={item.step} className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-lg">
                    {item.step}
                  </div>
                </div>
                <div className="flex-1 pt-1">
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    {item.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
                Built for developers and technical buyers
              </h2>
              <p className="text-lg text-muted-foreground">
                Modern architecture designed for cost efficiency and emotional
                intelligence
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  icon: Code2,
                  label: "FastAPI + Next.js 15",
                  desc: "Async-first, type-safe",
                },
                {
                  icon: Database,
                  label: "PostgreSQL + pgvector",
                  desc: "Unified semantic memory",
                },
                {
                  icon: Cpu,
                  label: "LangGraph Multi-Agent",
                  desc: "Stateful AI orchestration",
                },
                {
                  icon: Brain,
                  label: "Three-Tier Memory",
                  desc: "Personal, project, task",
                },
                {
                  icon: Zap,
                  label: "Cost-Aware",
                  desc: "<$0.10/user/day target",
                },
                {
                  icon: Heart,
                  label: "Privacy-First",
                  desc: "Opt-in context tracking",
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all"
                >
                  <item.icon className="w-8 h-8 text-primary mb-3" />
                  <h3 className="font-semibold text-foreground mb-1">
                    {item.label}
                  </h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-br from-primary/10 via-secondary/10 to-success/10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-8">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
              Ready to transform overwhelm into momentum?
            </h2>
            <p className="text-lg text-muted-foreground">
              Join ambitious people who are building trust in themselves, one
              mission at a time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/waitlist"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl hover:scale-105"
              >
                Join Waitlist
              </Link>
              <Link
                href="/future"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-foreground border-2 border-border rounded-xl hover:border-primary/50 hover:bg-accent transition-all"
              >
                Explore the future →
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

import Link from "next/link";
import {
  Users,
  Gamepad2,
  Mic,
  BarChart3,
  Calendar,
  Sparkles,
  Network,
  Cpu,
  Heart,
  Globe
} from "lucide-react";

export default function FuturePage() {
  const futureFeatures = [
    {
      theme: "Social & Guild Features",
      icon: Users,
      status: "exploring",
      items: [
        {
          title: "Shared accountability zones",
          description: "Create private spaces where small groups track progress together, celebrate wins, and hold each other accountable without judgment.",
        },
        {
          title: "Guild economies",
          description: "Earn guild-specific currency through mentorship, collaboration, and consistent effort. Unlock exclusive story arcs and zones.",
        },
        {
          title: "Mentor matching",
          description: "When you've mastered a skill, guide newcomers. Teaching deepens your understanding while unlocking the Connection attribute.",
        },
      ],
    },
    {
      theme: "Deeper Narrative & RPG Systems",
      icon: Gamepad2,
      status: "prototyping",
      items: [
        {
          title: "Multi-chapter story arcs",
          description: "Your progress drives 3-5 chapter narratives with planned endings, plot twists, and callbacks to earlier events. Feel like the protagonist of your own epic.",
        },
        {
          title: "Character relationship systems",
          description: "Build trust with AI companions through consistent interaction. Unlock deeper conversations, hidden quests, and character-specific story branches.",
        },
        {
          title: "World zones and exploration",
          description: "Your consistency unlocks new locations—the Arena, Observatory, Commons, Grand Hall—each with unique missions and characters.",
        },
      ],
    },
    {
      theme: "Voice & Multimodal Interactions",
      icon: Mic,
      status: "long-term",
      items: [
        {
          title: "Voice-first mission briefings",
          description: "Start your day hands-free. Ask Eliza what matters most while making coffee. Complete missions via voice during walks or commutes.",
        },
        {
          title: "Emotional tone detection",
          description: "The companion adjusts its approach based not just on what you say, but how you say it. Detect stress, excitement, or fatigue from vocal patterns.",
        },
        {
          title: "Visual evidence capture",
          description: "Take photos of your work—whiteboard sketches, code screens, gym progress photos. Build a visual portfolio of your journey.",
        },
      ],
    },
    {
      theme: "Advanced Analytics & Reflection",
      icon: BarChart3,
      status: "exploring",
      items: [
        {
          title: "Consistency deep dives",
          description: "Understand your patterns at a granular level. When are you most productive? Which mission types drain you? What triggers slumps?",
        },
        {
          title: "Weekly cinematic recaps",
          description: "Auto-generated highlight reels that show your week's journey: the missions completed, obstacles overcome, and growth achieved.",
        },
        {
          title: "Goal trajectory predictions",
          description: "Based on your current momentum, see projected completion dates and milestones. Adjust intensity to hit targets without burnout.",
        },
      ],
    },
    {
      theme: "Calendar & Tool Integrations",
      icon: Calendar,
      status: "exploring",
      items: [
        {
          title: "Calendar sync for context",
          description: "Let Delight see your calendar (opt-in) to suggest missions around meetings, respect deep work blocks, and avoid overcommitting.",
        },
        {
          title: "GitHub/GitLab integration",
          description: "Automatically track coding missions via commits. See your constellation grow as you ship features, close issues, and review PRs.",
        },
        {
          title: "Creative tool connections",
          description: "Track writing in Google Docs, designs in Figma, music in Ableton. Your creative output drives narrative progression.",
        },
      ],
    },
    {
      theme: "Autonomous Agent Network",
      icon: Cpu,
      status: "long-term",
      items: [
        {
          title: "Delegated research agents",
          description: "Ask Delight to research topics, compile resources, and synthesize findings while you focus on execution. Reclaim your cognitive bandwidth.",
        },
        {
          title: "Logistics orchestration",
          description: "Schedule appointments, book travel, coordinate meetings. The companion handles operational overhead so you can focus on meaningful work.",
        },
        {
          title: "Multi-agent collaboration",
          description: "Different AI characters specialize in different domains—Lyra for craft, Thorne for health, Elara for wisdom. They coordinate behind the scenes.",
        },
      ],
    },
    {
      theme: "Community & Matchmaking",
      icon: Network,
      status: "exploring",
      items: [
        {
          title: "Skill-based introductions",
          description: "When you're stuck on a problem someone in the community has solved, Delight facilitates introductions. Build genuine relationships around shared challenges.",
        },
        {
          title: "Cohort-based rituals",
          description: "Join time-bound cohorts working on similar goals. Shared start dates, weekly check-ins, and group celebrations create accountability without pressure.",
        },
        {
          title: "Mentorship matching",
          description: "Connect experienced practitioners with eager learners. Both benefit—mentees get guidance, mentors deepen their understanding through teaching.",
        },
      ],
    },
    {
      theme: "Emotion-Aware Sensory Inputs",
      icon: Heart,
      status: "long-term",
      items: [
        {
          title: "Screen time awareness",
          description: "Opt-in tracking of app/tab behavior helps the companion detect context switching patterns and suggest focus interventions.",
        },
        {
          title: "Wearable integration",
          description: "Connect fitness trackers to let Delight suggest rest when HRV drops, or ambitious missions when your energy is high.",
        },
        {
          title: "Mood journaling prompts",
          description: "Periodic emotional check-ins build a longitudinal dataset. The companion learns to predict slumps and proactively offer support.",
        },
      ],
    },
  ];

  const statusColors = {
    exploring: "bg-secondary/10 text-secondary border-secondary/20",
    prototyping: "bg-primary/10 text-primary border-primary/20",
    "long-term": "bg-muted text-muted-foreground border-border",
  };

  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-20 lg:py-32 bg-gradient-to-b from-success/10 to-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success/10 border border-success/20 text-success text-sm font-medium mb-4">
              <Sparkles className="w-4 h-4" />
              Living roadmap
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
              The future of Delight
            </h1>
            <p className="text-xl text-muted-foreground leading-relaxed">
              Where we're headed and what we're exploring. This is our notebook of possibilities—
              ideas that could reshape how ambitious people approach their goals.
            </p>
          </div>
        </div>
      </section>

      {/* Intro */}
      <section className="py-12 border-b border-border">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto">
            <p className="text-lg text-foreground/90 leading-relaxed">
              Delight's MVP focuses on proving a humane single-player loop: remembered context, adaptive missions,
              visible progress, and compassionate outreach. But our vision extends far beyond that foundation.
              Below are features and experiments we're exploring—grouped by theme, with rough statuses.
              Nothing here is promised. Some ideas will ship. Some will evolve. Some we'll abandon entirely
              based on what you tell us actually works.
            </p>
          </div>
        </div>
      </section>

      {/* Future Feature Cards */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto space-y-16">
            {futureFeatures.map((theme, idx) => (
              <div key={idx} className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                      <theme.icon className="w-6 h-6 text-foreground" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold text-foreground">
                        {theme.theme}
                      </h2>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[theme.status as keyof typeof statusColors]}`}>
                        {theme.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                  {theme.items.map((item, itemIdx) => (
                    <div
                      key={itemIdx}
                      className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all hover:shadow-md"
                    >
                      <h3 className="font-semibold text-foreground mb-3">
                        {item.title}
                      </h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {item.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Status Legend */}
      <section className="py-12 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-lg font-semibold text-foreground mb-6 text-center">
              What these statuses mean
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="inline-flex px-3 py-1 rounded-full text-xs font-medium border bg-secondary/10 text-secondary border-secondary/20 mb-3">
                  exploring
                </div>
                <p className="text-sm text-muted-foreground">
                  We're researching feasibility, gathering user feedback, and sketching prototypes.
                  These ideas feel promising but aren't actively being built yet.
                </p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="inline-flex px-3 py-1 rounded-full text-xs font-medium border bg-primary/10 text-primary border-primary/20 mb-3">
                  prototyping
                </div>
                <p className="text-sm text-muted-foreground">
                  We're building early versions to test with pilot users. Expect rough edges and iteration.
                  These features are closer to reality.
                </p>
              </div>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="inline-flex px-3 py-1 rounded-full text-xs font-medium border bg-muted text-muted-foreground border-border mb-3">
                  long-term
                </div>
                <p className="text-sm text-muted-foreground">
                  Ambitious ideas that require more infrastructure, research, or user maturity.
                  These are on the horizon but not immediate priorities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="py-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-foreground">
                Help shape what gets built next
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                The features that ship will be the ones that resonate most with early users.
                If something on this page excites you—or if you have ideas we haven't considered—
                we want to hear from you.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/waitlist"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl"
              >
                Join the Waitlist
              </Link>
              <Link
                href="/why"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-foreground border-2 border-border rounded-xl hover:border-primary/50 hover:bg-accent transition-all"
              >
                Read the Manifesto
              </Link>
            </div>
            <p className="text-sm text-muted-foreground">
              Want to suggest a feature or give feedback on these ideas?
              <br />
              Join the waitlist and you'll get a direct line to the team.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

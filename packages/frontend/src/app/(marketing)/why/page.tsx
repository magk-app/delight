import Link from "next/link";

export default function WhyPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-20 lg:py-32 bg-gradient-to-b from-secondary/10 to-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
              Why we're building Delight
            </h1>
            <p className="text-xl text-muted-foreground leading-relaxed">
              A manifesto for ambitious people who know what to do but can't seem to start
            </p>
          </div>
        </div>
      </section>

      {/* Content */}
      <article className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto space-y-16">
            {/* Section 1 */}
            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-foreground">
                Ambition is not the problem. Emotional friction is.
              </h2>
              <div className="prose prose-lg prose-slate max-w-none">
                <p className="text-foreground/90 leading-relaxed">
                  You're ambitious. You set audacious goals. You know exactly what needs to be done.
                  But after lunch, or after a break, starting feels impossible. Five minutes into focused work,
                  you're checking another tab. Your to-do list sprawls across three tools, and the thought of
                  prioritizing feels paralyzing.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  This isn't laziness. It's not a character flaw. It's emotional friction—the cognitive and
                  affective resistance that emerges when stress, overwhelm, and context switching collide with
                  complex goals. Your brain is protecting you from perceived threats. The problem is, your
                  brain can't tell the difference between a difficult presentation and a physical danger.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Traditional productivity tools don't address this. They focus on structure—lists, timers,
                  Kanban boards—but ignore the emotional state that determines whether you can even engage
                  with that structure. When you're overwhelmed, another task list isn't the answer.
                  Understanding and acknowledgment is.
                </p>
              </div>
            </section>

            {/* Pull Quote */}
            <blockquote className="border-l-4 border-primary pl-6 py-2 italic text-xl text-foreground/80">
              "The gap between knowing what to do and actually doing it is where most ambitious projects die."
            </blockquote>

            {/* Section 2 */}
            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-foreground">
                Why tools that ignore your state keep failing you
              </h2>
              <div className="prose prose-lg prose-slate max-w-none">
                <p className="text-foreground/90 leading-relaxed">
                  DIY productivity systems—Notion templates, habit trackers, elaborate frameworks—demand constant
                  maintenance exactly when you have the least bandwidth. They're built for the version of you
                  who has energy to spare. When life gets chaotic, they collapse. You return three weeks later
                  to a graveyard of abandoned boards and outdated goals.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Generic AI assistants provide surface-level advice without understanding your unique context.
                  They reset every conversation, forcing you to re-explain your situation repeatedly. They can't
                  remember that three weeks ago you mentioned your fear of public speaking, or that last month
                  you tried a similar approach and it didn't work.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Professional coaching is effective but expensive—and unavailable during the exact moments of
                  hesitation when you need support most. That 3pm slump where you're staring at your screen,
                  knowing you should start the report but opening Twitter instead? Your coach isn't there.
                  Your accountability buddy is in their own meeting. You're alone with your avoidance.
                </p>
              </div>
            </section>

            {/* Section 3 */}
            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-foreground">
                What it means to be a companion with memory
              </h2>
              <div className="prose prose-lg prose-slate max-w-none">
                <p className="text-foreground/90 leading-relaxed">
                  Delight is designed to be what those other tools aren't: a companion that remembers. Not just
                  your tasks, but your journey. Your values. Your fears. Your patterns. When you open Delight
                  after a difficult week, it doesn't greet you with a generic "What can I do for you today?"
                  It says: "You've been quiet. Last time we talked, you were stressed about the presentation.
                  How did it go?"
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  This memory system operates on three tiers. Personal memories capture long-term context:
                  your career aspirations, your tendency to procrastinate on creative work, your preference for
                  morning focus sessions. Project memories track each major goal's evolution: what you've tried,
                  what worked, what obstacles emerged. Task memories ensure the AI understands specific mission
                  details: that "finish design mockups" actually means three screens with interactive prototypes,
                  not just static images.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Over time, this creates a relationship that compounds in value. The companion doesn't just
                  respond—it anticipates. It notices when you're slipping into old patterns. It remembers what
                  helped you push through similar challenges before. It becomes more useful precisely when you
                  need it most: when you're too overwhelmed to articulate what you need.
                </p>
              </div>
            </section>

            {/* Pull Quote */}
            <blockquote className="border-l-4 border-secondary pl-6 py-2 italic text-xl text-foreground/80">
              "Trust isn't built in a single conversation. It's built when someone remembers—and acts on—what you told them last time."
            </blockquote>

            {/* Section 4 */}
            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-foreground">
                Why we built a world instead of another list
              </h2>
              <div className="prose prose-lg prose-slate max-w-none">
                <p className="text-foreground/90 leading-relaxed">
                  Productivity shouldn't feel like paperwork. For some people, tracking progress in a spreadsheet
                  is satisfying. But for many ambitious people—especially those with ADHD tendencies or creative
                  mindsets—lists feel lifeless. They don't inspire. They don't create meaning.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  This is why Delight includes a narrative layer. Your work unfolds in a living world that
                  responds to your real-world progress. Complete missions to earn Essence (in-game currency),
                  build relationships with AI characters, unlock new zones, and progress through story chapters.
                  The narrative serves your real goals—"prepare for job interview" becomes "prove yourself to
                  the Guild Council," making preparation feel like meaningful progression in a larger story.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  This isn't superficial gamification. Points and badges alone don't work—they feel hollow.
                  But when your actual work drives a story that surprises you, when characters you've grown to
                  care about acknowledge your effort, when the world visibly changes based on your consistency—
                  that creates genuine motivation. It turns "I should work on this" into "I want to see what
                  happens next."
                </p>
              </div>
            </section>

            {/* Section 5 */}
            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-foreground">
                How we think about privacy, cost, and trust
              </h2>
              <div className="prose prose-lg prose-slate max-w-none">
                <p className="text-foreground/90 leading-relaxed">
                  When you share your emotional state, your goals, and your struggles with a tool, you're
                  extending enormous trust. We don't take that lightly.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Privacy in Delight means transparency and control. Any context signals—like tab focus or
                  activity patterns—are explicitly opt-in. You always know what we're tracking. You can review
                  everything stored about you, revoke permissions anytime, and export your complete data on demand.
                  Your emotional check-ins, goals, and progress belong to you. We're caretakers, not owners.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Cost efficiency matters because it determines accessibility. We're targeting operational costs
                  under $0.10 per user per day—using smart architecture choices like PostgreSQL with pgvector
                  for unified storage, GPT-4o-mini for most interactions, and careful prompt engineering to
                  minimize API calls. This isn't about maximizing profit margins. It's about building something
                  that students, freelancers, and early-stage founders can actually afford.
                </p>
                <p className="text-foreground/90 leading-relaxed">
                  Trust is the only defensible moat for a companion. If we betray that trust—through dark patterns,
                  surveillance, or exploitative pricing—we lose everything that makes Delight valuable. Your
                  autonomy stays front and center. Always.
                </p>
              </div>
            </section>

            {/* Closing */}
            <section className="border-t border-border pt-12 space-y-8">
              <div className="space-y-4">
                <p className="text-xl text-foreground/90 leading-relaxed">
                  If this resonates—if you've felt the gap between ambition and execution, if you've wished for
                  a tool that understands the emotional dimension of getting things done—you're exactly who we're
                  building for.
                </p>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  We're in early development. The core loop is taking shape. The memory system works. The narrative
                  engine is generating personalized stories. But we need people willing to trust us with their goals
                  and give honest feedback when something doesn't work.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  href="/waitlist"
                  className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl"
                >
                  Join the Waitlist
                </Link>
                <Link
                  href="/"
                  className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-foreground border-2 border-border rounded-xl hover:border-primary/50 hover:bg-accent transition-all"
                >
                  ← Back to Product
                </Link>
              </div>
            </section>
          </div>
        </div>
      </article>
    </div>
  );
}

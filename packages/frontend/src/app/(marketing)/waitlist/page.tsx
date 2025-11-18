import Link from "next/link";
import { CheckCircle2, Mail, Clock, Users } from "lucide-react";

export default function WaitlistPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="py-20 lg:py-32 bg-gradient-to-b from-primary/10 to-background">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
              Join the Delight waitlist
            </h1>
            <p className="text-xl text-muted-foreground leading-relaxed">
              Be among the first to experience an AI companion that truly
              understands your journey
            </p>
          </div>
        </div>
      </section>

      {/* Content */}
      <section className="py-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-start">
              {/* Left: Benefits */}
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-bold text-foreground mb-4">
                    What to expect
                  </h2>
                  <p className="text-muted-foreground leading-relaxed">
                    When you join our waitlist, you&apos;re not just signing up
                    for updates—you&apos;re expressing interest in helping shape
                    a tool that could genuinely change how you approach your
                    goals.
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Users className="w-6 h-6 text-primary" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-2">
                        Early access to the beta
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Waitlist members get first access when we open up pilot
                        cohorts. You&apos;ll be using Delight before the general
                        public, helping us refine the experience.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                        <Mail className="w-6 h-6 text-secondary" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-2">
                        Thoughtful, infrequent updates
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        We&apos;ll send you meaningful progress updates when we
                        hit major milestones. No daily spam. No sales pressure.
                        Just honest communication about where we are.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-success" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground mb-2">
                        Shape the product direction
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Your feedback will directly influence features,
                        priorities, and design decisions. We&apos;re building
                        this for people like you—not for abstract personas.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-muted/50 border border-border rounded-xl p-6">
                  <h3 className="font-semibold text-foreground mb-3">
                    Who&apos;s the best fit for early access?
                  </h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>
                        Ambitious people who routinely set big goals but
                        struggle with consistency
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>
                        Founders, students, or creators juggling multiple
                        priorities
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>
                        People willing to give honest feedback, even when
                        it&apos;s critical
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>
                        Anyone who believes productivity tools should understand
                        emotion, not ignore it
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Right: Form Embed */}
              <div className="lg:sticky lg:top-24">
                <div className="bg-card border-2 border-primary/20 rounded-2xl p-8 shadow-lg">
                  <div className="mb-6">
                    <h3 className="text-xl font-bold text-foreground mb-2">
                      Reserve your spot
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Takes less than a minute. We respect your inbox.
                    </p>
                  </div>

                  {/* Google Form Embed */}
                  <div className="rounded-xl overflow-hidden border border-border">
                    <iframe
                      src="https://docs.google.com/forms/d/e/1FAIpQLSek-5i4Kdd6iRTKEhTVD3pjI0AAtnZ9_cGajk6oFeEXlb998g/viewform?embedded=true"
                      width="100%"
                      height="800"
                      frameBorder="0"
                      marginHeight={0}
                      marginWidth={0}
                      className="w-full"
                    >
                      Loading…
                    </iframe>
                  </div>

                  <div className="mt-6">
                    <p className="text-xs text-muted-foreground text-center">
                      Can&apos;t see the form?{" "}
                      <a
                        href="https://docs.google.com/forms/d/e/1FAIpQLSek-5i4Kdd6iRTKEhTVD3pjI0AAtnZ9_cGajk6oFeEXlb998g/viewform"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        Open in new tab →
                      </a>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* FAQ */}
            <div className="mt-20 max-w-3xl mx-auto">
              <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
                Common questions
              </h2>
              <div className="space-y-6">
                <div className="border border-border rounded-xl p-6">
                  <h3 className="font-semibold text-foreground mb-2">
                    When will the beta start?
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    We&apos;re targeting early pilot cohorts in Q1 2026. The
                    exact timing depends on core loop stability and memory
                    system performance. Waitlist members will get at least 2
                    weeks notice before their cohort starts.
                  </p>
                </div>

                <div className="border border-border rounded-xl p-6">
                  <h3 className="font-semibold text-foreground mb-2">
                    How often will you email me?
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Very rarely. Expect 1-2 emails per month at most, and only
                    when there&apos;s something meaningful to share— like beta
                    access opening, major feature launches, or requests for
                    specific feedback. You can unsubscribe anytime.
                  </p>
                </div>

                <div className="border border-border rounded-xl p-6">
                  <h3 className="font-semibold text-foreground mb-2">
                    Will early access be free?
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Yes. Pilot cohort members will have free access during the
                    beta period. We&apos;re not asking you to pay for an
                    unfinished product—we&apos;re asking you to invest time
                    giving us feedback. That&apos;s valuable enough.
                  </p>
                </div>

                <div className="border border-border rounded-xl p-6">
                  <h3 className="font-semibold text-foreground mb-2">
                    What if Delight doesn&apos;t work for me?
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    That&apos;s important data. If the core loop doesn&apos;t
                    resonate, if the narrative feels gimmicky, if the AI
                    misunderstands you—we want to know. Critical feedback is
                    more valuable than polite praise. Help us build something
                    that actually works.
                  </p>
                </div>
              </div>
            </div>

            {/* Bottom CTA */}
            <div className="mt-16 text-center">
              <p className="text-muted-foreground mb-6">
                Want to learn more before joining?
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/"
                  className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-foreground border border-border rounded-lg hover:border-primary/50 hover:bg-accent transition-all"
                >
                  ← Explore the Product
                </Link>
                <Link
                  href="/why"
                  className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-foreground border border-border rounded-lg hover:border-primary/50 hover:bg-accent transition-all"
                >
                  Read the Manifesto
                </Link>
                <Link
                  href="/future"
                  className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-foreground border border-border rounded-lg hover:border-primary/50 hover:bg-accent transition-all"
                >
                  See the Future →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

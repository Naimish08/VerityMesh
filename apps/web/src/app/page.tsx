import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { ArrowRight, Sparkles, Activity, ShieldCheck, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col gap-16 py-12 animate-fade-in">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium border border-primary/20 mb-4">
          <Sparkles size={16} /> VerityMesh Phase 1 MVP
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-foreground">
          Autonomous Research & <br className="hidden sm:block" />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-emerald-400">
            Fact-Verification
          </span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
          Deploy multi-agent swarms to deeply research topics, cross-check claims against reliable sources, and generate verified reports with confidence scoring.
        </p>
        <div className="pt-4">
          <Link
            href="/research/new"
            className="inline-flex items-center justify-center text-lg px-8 gap-2 group h-14 rounded-full bg-primary text-primary-foreground font-medium shadow-[0_0_30px_rgba(59,130,246,0.3)] hover:shadow-[0_0_40px_rgba(59,130,246,0.5)] transition-all"
          >
            Start New Research <ArrowRight className="group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <FeatureCard 
          icon={<Activity className="text-blue-400" size={24} />}
          title="Deep Research Pipeline"
          description="Agents recursively search the web, papers, and docs to build a comprehensive knowledge base."
        />
        <FeatureCard 
          icon={<ShieldCheck className="text-emerald-400" size={24} />}
          title="Claim Verification"
          description="Every claim is extracted, cross-referenced, and scored for confidence with exact source citations."
        />
        <FeatureCard 
          icon={<Zap className="text-amber-400" size={24} />}
          title="Real-time Streaming"
          description="Watch the agents think, plan, and execute live via an event stream and dynamic pipeline stepper."
        />
      </section>

      {/* Recent Runs (Empty State for MVP) */}
      <section className="max-w-5xl mx-auto w-full space-y-6 pt-12 border-t border-border/40">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Recent Research</h2>
        </div>
        <Card className="flex flex-col items-center justify-center p-12 text-center border-dashed border-2 bg-transparent">
          <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Activity className="text-muted-foreground" size={24} />
          </div>
          <h3 className="text-lg font-medium text-foreground mb-2">No research runs yet</h3>
          <p className="text-muted-foreground max-w-sm mb-6">
            Start your first autonomous research query to see VerityMesh in action.
          </p>
          <Link
            href="/research/new"
            className="inline-flex items-center justify-center text-sm font-medium px-4 py-2 rounded-md border border-border bg-background hover:bg-muted transition-colors"
          >
            Initialize Run
          </Link>
        </Card>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <Card className="p-6 bg-card/40 border-border/40 hover:bg-card/80 transition-colors">
      <div className="w-12 h-12 rounded-lg bg-background/80 border border-border/50 flex items-center justify-center mb-4 shadow-sm">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed">
        {description}
      </p>
    </Card>
  );
}

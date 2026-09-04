import Link from 'next/link';
import { Activity } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto flex h-16 items-center px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 group">
          <Activity className="h-6 w-6 text-primary group-hover:animate-pulse-subtle" />
          <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 group-hover:to-primary transition-all duration-500">
            VerityMesh
          </span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link href="/" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Dashboard
          </Link>
          <Link href="/research/new" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            New Research
          </Link>
        </nav>
      </div>
    </header>
  );
}

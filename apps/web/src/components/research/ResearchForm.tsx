"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Textarea';
import { Toggle } from '@/components/ui/Toggle';
import { Sparkles, Globe, FileText, BookOpen } from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { z } from 'zod';

const formSchema = z.object({
  question: z.string().min(10, 'Question must be at least 10 characters long'),
  depth: z.enum(['Quick', 'Standard', 'Deep']),
  sources: z.array(z.string()).min(1, 'Select at least one source type'),
  max_sources: z.number().min(5).max(50),
});

export function ResearchForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [question, setQuestion] = useState('');
  const [depth, setDepth] = useState<'Quick' | 'Standard' | 'Deep'>('Standard');
  const [sources, setSources] = useState<string[]>(['web']);
  const [maxSources, setMaxSources] = useState(20);
  const [verifyCitations, setVerifyCitations] = useState(true);
  const [autonomousMode, setAutonomousMode] = useState(false);

  const handleSourceToggle = (source: string) => {
    setSources(prev => 
      prev.includes(source) ? prev.filter(s => s !== source) : [...prev, source]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      formSchema.parse({ question, depth, sources, max_sources: maxSources });
      setLoading(true);
      
      const res = await apiFetch<{ id: string }>('/api/research', {
        method: 'POST',
        body: JSON.stringify({
          question,
          depth: depth.toLowerCase(),
          sources,
          max_sources: maxSources,
          require_citation_verification: verifyCitations,
          allow_autonomous_research: autonomousMode,
        }),
      });
      
      router.push(`/research/${res.id}`);
    } catch (err: any) {
      if (err instanceof z.ZodError) {
        setError(err.errors[0].message);
      } else {
        setError(err.message || 'Failed to start research');
      }
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 animate-fade-in">
      <Card className="p-6">
        <div className="space-y-4">
          <label className="block text-lg font-medium text-foreground">
            What do you want to research?
          </label>
          <Textarea 
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Should Kafka or RabbitMQ be used for high-throughput order processing in a distributed e-commerce architecture?"
            className="text-base min-h-[120px] bg-background/80"
          />
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-3">
              Research Depth
            </label>
            <div className="flex gap-3">
              {(['Quick', 'Standard', 'Deep'] as const).map(d => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDepth(d)}
                  className={`flex-1 py-2 px-3 rounded-full text-sm font-medium transition-all ${
                    depth === d 
                      ? 'bg-primary text-primary-foreground shadow-[0_0_15px_rgba(59,130,246,0.5)] border-transparent' 
                      : 'bg-muted text-muted-foreground border border-border/50 hover:bg-muted/80'
                  }`}
                >
                  {d === 'Quick' ? '⚡ ' : d === 'Standard' ? '🔬 ' : '🔍 '}{d}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-3">
              Source Types
            </label>
            <div className="flex flex-wrap gap-3">
              <SourceButton 
                active={sources.includes('web')} 
                onClick={() => handleSourceToggle('web')}
                icon={<Globe size={16} />} 
                label="Web" 
              />
              <SourceButton 
                active={sources.includes('papers')} 
                onClick={() => handleSourceToggle('papers')}
                icon={<BookOpen size={16} />} 
                label="Papers" 
              />
              <SourceButton 
                active={sources.includes('docs')} 
                onClick={() => handleSourceToggle('docs')}
                icon={<FileText size={16} />} 
                label="Documents" 
              />
            </div>
          </div>
        </Card>

        <Card className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-3 flex justify-between">
              <span>Max Sources</span>
              <span className="text-foreground">{maxSources}</span>
            </label>
            <div className="flex items-center gap-4">
              <input 
                type="range" 
                min="5" max="50" 
                value={maxSources} 
                onChange={e => setMaxSources(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>
          </div>

          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Require Citation Verification</p>
                <p className="text-xs text-muted-foreground">Cross-check all claims against sources</p>
              </div>
              <Toggle checked={verifyCitations} onChange={setVerifyCitations} />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Autonomous Mode</p>
                <p className="text-xs text-muted-foreground">Allow agents to pivot based on findings</p>
              </div>
              <Toggle checked={autonomousMode} onChange={setAutonomousMode} />
            </div>
          </div>
        </Card>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="flex justify-end">
        <Button 
          type="submit" 
          size="lg" 
          isLoading={loading}
          className="w-full sm:w-auto text-lg gap-2"
        >
          <Sparkles size={20} />
          Start Research ✦
        </Button>
      </div>
    </form>
  );
}

function SourceButton({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-2 py-2 px-4 rounded-lg border text-sm font-medium transition-all ${
        active 
          ? 'border-primary bg-primary/10 text-primary' 
          : 'border-border/50 bg-background/50 text-muted-foreground hover:bg-muted'
      }`}
    >
      {icon} {label}
    </button>
  );
}

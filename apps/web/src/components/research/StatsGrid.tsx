"use client";

import { useResearchStore } from '@/stores/useResearchStore';
import { Card } from '@/components/ui/Card';
import { formatDuration } from '@/lib/utils';
import { BookOpen, FileText, Clock, Hash } from 'lucide-react';
import { useEffect, useState } from 'react';

export function StatsGrid() {
  const stats = useResearchStore(state => state.stats);
  const currentStep = useResearchStore(state => state.currentStep);
  
  // Local timer for active duration display
  const [activeDuration, setActiveDuration] = useState(stats.duration_ms);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (currentStep !== 'completed' && currentStep !== 'failed' && currentStep !== 'pending') {
      interval = setInterval(() => {
        setActiveDuration(prev => prev + 1000);
      }, 1000);
    } else {
      setActiveDuration(stats.duration_ms);
    }
    return () => clearInterval(interval);
  }, [currentStep, stats.duration_ms]);

  return (
    <div className="grid grid-cols-2 gap-4">
      <StatCard 
        icon={<BookOpen size={18} className="text-blue-400" />} 
        label="Sources Analyzed" 
        value={stats.sources_analyzed} 
      />
      <StatCard 
        icon={<FileText size={18} className="text-amber-400" />} 
        label="Claims Extracted" 
        value={stats.claims_extracted} 
      />
      <StatCard 
        icon={<Clock size={18} className="text-emerald-400" />} 
        label="Duration" 
        value={formatDuration(activeDuration)} 
      />
      <StatCard 
        icon={<Hash size={18} className="text-purple-400" />} 
        label="Tokens Used" 
        value={stats.tokens_used.toLocaleString()} 
      />
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string | number }) {
  return (
    <Card className="p-4 flex flex-col items-start gap-2 bg-card/40 border-border/40 hover:bg-card/60 transition-colors">
      <div className="flex items-center gap-2 text-muted-foreground text-sm font-medium">
        {icon}
        {label}
      </div>
      <div className="text-2xl font-bold text-foreground tracking-tight">
        {value}
      </div>
    </Card>
  );
}

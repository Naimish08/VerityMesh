"use client";

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useSSE } from '@/hooks/useSSE';
import { useResearchStore } from '@/stores/useResearchStore';
import { PipelineStepper } from '@/components/research/PipelineStepper';
import { LiveEventLog } from '@/components/research/LiveEventLog';
import { StatsGrid } from '@/components/research/StatsGrid';
import { Card } from '@/components/ui/Card';
import { StatusBadge } from '@/components/research/StatusBadge';
import { Button } from '@/components/ui/Button';
import { ArrowRight, AlertCircle, FileText } from 'lucide-react';
import { apiFetch } from '@/lib/api';

export default function LiveResearchPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const { currentResearch, setResearch, addEvent, currentStep } = useResearchStore();
  
  // Connect to SSE
  const { connectionState } = useSSE(id, {
    onEvent: addEvent,
    autoReconnect: true,
  });

  // Initial fetch
  useEffect(() => {
    async function fetchDetails() {
      try {
        const data = await apiFetch<any>(`/research/${id}`);
        setResearch(data);
      } catch (err) {
        console.error('Failed to fetch research details', err);
      }
    }
    fetchDetails();
  }, [id, setResearch]);

  const isComplete = currentStep === 'completed';

  return (
    <div className="max-w-7xl mx-auto py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">Active Research Run</h1>
            <StatusBadge status={currentStep} />
          </div>
          <p className="text-lg text-muted-foreground max-w-3xl border-l-4 border-primary/50 pl-4 py-1 italic">
            "{currentResearch?.question || 'Loading question...'}"
          </p>
        </div>
        
        {isComplete && (
          <Button 
            size="lg" 
            onClick={() => router.push(`/research/${id}/report`)}
            className="shrink-0 gap-2 animate-pulse-subtle"
          >
            <FileText size={18} /> View Final Report <ArrowRight size={18} />
          </Button>
        )}
      </div>

      {connectionState === 'error' && !isComplete && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg flex items-center gap-3">
          <AlertCircle size={20} />
          <span>Connection to live stream lost. Attempting to reconnect...</span>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Pipeline (60% -> col-span-7) */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="p-6 md:p-8">
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <ActivityIcon /> Pipeline Status
            </h2>
            <PipelineStepper />
          </Card>
        </div>

        {/* Right Column: Stats (40% -> col-span-5) */}
        <div className="lg:col-span-5 space-y-6">
          <StatsGrid />
        </div>
      </div>

      {/* Bottom: Event Log */}
      <div className="space-y-3 pt-4">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Live Event Stream</h3>
        <LiveEventLog />
      </div>
    </div>
  );
}

function ActivityIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

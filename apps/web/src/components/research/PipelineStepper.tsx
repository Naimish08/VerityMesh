"use client";

import { useResearchStore } from '@/stores/useResearchStore';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';

const STEPS = [
  { id: 'planning', label: 'Planning & Strategy' },
  { id: 'researching', label: 'Gathering Literature & Web Sources' },
  { id: 'extracting', label: 'Extracting Atomic Claims' },
  { id: 'synthesizing', label: 'Synthesizing Verified Report' },
  { id: 'completed', label: 'Complete' },
];

export function PipelineStepper() {
  const currentStep = useResearchStore(state => state.currentStep);
  
  const currentIndex = STEPS.findIndex(s => s.id === currentStep);
  const isFailed = currentStep === 'failed';
  const isPending = currentStep === 'pending';

  return (
    <div className="flex flex-col space-y-6">
      {STEPS.map((step, index) => {
        // If pending, first step is active indicator
        const isActive = (index === currentIndex || (isPending && index === 0)) && !isFailed && currentStep !== 'completed';
        const isCompleted = currentStep === 'completed' || (currentIndex > -1 && index < currentIndex);
        
        return (
          <div key={step.id} className="flex items-start gap-4 relative">
            {/* Connecting line */}
            {index < STEPS.length - 1 && (
              <div 
                className={`absolute left-[11px] top-8 bottom-[-24px] w-[2px] transition-colors ${
                  isCompleted ? 'bg-primary' : 'bg-border/50 border-dashed border-l-2'
                }`}
              />
            )}
            
            <div className="relative z-10 flex-shrink-0 mt-1">
              {isCompleted ? (
                <CheckCircle2 className="text-emerald-400 w-6 h-6 bg-background rounded-full" />
              ) : isActive ? (
                <div className="relative">
                  <Loader2 className="text-primary w-6 h-6 animate-spin" />
                  <div className="absolute inset-0 bg-primary/20 rounded-full blur-md animate-pulse" />
                </div>
              ) : (
                <Circle className="text-muted-foreground/40 w-6 h-6 bg-background rounded-full" />
              )}
            </div>
            
            <div>
              <p className={`font-medium transition-colors ${
                isActive ? 'text-primary drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]' :
                isCompleted ? 'text-foreground' : 'text-muted-foreground/60'
              }`}>
                {step.label}
              </p>
              {isActive && (
                <p className="text-xs text-muted-foreground mt-1 animate-pulse">
                  {currentStep === 'pending' ? 'Initializing research agents...' : 'In progress...'}
                </p>
              )}
            </div>
          </div>
        );
      })}
      {isFailed && (
        <div className="flex items-start gap-4 text-red-400 mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">Pipeline Execution Halted</p>
            <p className="text-xs text-red-300/80 mt-0.5">An error occurred during agent execution. Check live event logs.</p>
          </div>
        </div>
      )}
    </div>
  );
}

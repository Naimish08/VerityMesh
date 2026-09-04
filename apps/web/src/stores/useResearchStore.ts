import { create } from 'zustand';
import { ResearchRun, ResearchStats, Claim, Source } from '@/types/research';
import { LogEntry, SSEEvent } from '@/types/events';

interface ResearchState {
  currentResearch: ResearchRun | null;
  events: LogEntry[];
  stats: ResearchStats;
  claims: Claim[];
  sources: Source[];
  connectionState: string;
  currentStep: string;
  
  setResearch: (research: ResearchRun) => void;
  addEvent: (event: SSEEvent) => void;
  updateStats: (stats: Partial<ResearchStats>) => void;
  addClaim: (claim: Claim) => void;
  addSource: (source: Source) => void;
  setStep: (step: string) => void;
  setConnectionState: (state: string) => void;
  reset: () => void;
}

const defaultStats: ResearchStats = {
  duration_ms: 0,
  sources_analyzed: 0,
  claims_extracted: 0,
  claims_verified: 0,
  contradictions_found: 0,
  citations_count: 0,
  avg_confidence: 0,
  tokens_used: 0,
};

export const useResearchStore = create<ResearchState>((set) => ({
  currentResearch: null,
  events: [],
  stats: defaultStats,
  claims: [],
  sources: [],
  connectionState: 'disconnected',
  currentStep: 'pending',

  setResearch: (research) => set({
    currentResearch: research,
    stats: research.stats || defaultStats,
    currentStep: research.status || 'pending',
  }),
  
  addEvent: (event) => set((state) => {
    const newEntry: LogEntry = {
      id: Math.random().toString(36).substring(7),
      timestamp: new Date().toISOString(),
      event,
    };
    const newEvents = [...state.events, newEntry].slice(-200); // Bounded to 200 max
    
    // Auto-update step based on event type
    let step = state.currentStep;
    if (event.type === 'planning') step = 'planning';
    if (event.type === 'status_change') step = event.data?.status || step;
    if (
      event.type === 'research_start' || 
      event.type === 'source_found' || 
      event.type === 'chunk_stored' ||
      event.type === 'research_complete'
    ) {
      if (step !== 'synthesizing' && step !== 'completed') {
        step = 'researching';
      }
    }
    if (event.type === 'claim_extracted') step = 'extracting';
    if (event.type === 'synthesis_start' || event.type === 'report_ready') step = 'synthesizing';
    if (event.type === 'complete') step = 'completed';
    if (event.type === 'error' && !event.data?.recoverable) step = 'failed';

    // Update stats counters dynamically
    const updatedStats = { ...state.stats };
    if (event.type === 'source_found') {
      updatedStats.sources_analyzed = (updatedStats.sources_analyzed || 0) + 1;
    }
    if (event.type === 'claim_extracted') {
      updatedStats.claims_extracted = (updatedStats.claims_extracted || 0) + 1;
    }
    if (event.type === 'complete' && event.data?.stats) {
      Object.assign(updatedStats, event.data.stats);
    }

    return { events: newEvents, currentStep: step, stats: updatedStats };
  }),

  updateStats: (stats) => set((state) => ({ stats: { ...state.stats, ...stats } })),
  
  addClaim: (claim) => set((state) => ({ claims: [...state.claims, claim] })),
  
  addSource: (source) => set((state) => ({ sources: [...state.sources, source] })),
  
  setStep: (step) => set({ currentStep: step }),
  
  setConnectionState: (state) => set({ connectionState: state }),
  
  reset: () => set({
    currentResearch: null,
    events: [],
    stats: defaultStats,
    claims: [],
    sources: [],
    connectionState: 'disconnected',
    currentStep: 'pending',
  }),
}));

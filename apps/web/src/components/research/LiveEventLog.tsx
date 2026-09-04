"use client";

import { useEffect, useRef } from 'react';
import { useResearchStore } from '@/stores/useResearchStore';

export function LiveEventLog() {
  const events = useResearchStore(state => state.events);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events]);

  const formatEventContent = (type: string, data: any) => {
    if (!data) return '';
    if (typeof data === 'string') return data;
    if (data.message) return data.message;
    if (data.error) return data.error;
    if (type === 'source_found' && data.url) return `Discovered: ${data.url}`;
    if (type === 'planning' && data.sub_questions) {
      return `Decomposed into ${data.sub_questions.length} sub-questions: ${data.sub_questions.slice(0, 2).join('; ')}...`;
    }
    if (type === 'status_change' && data.status) return `Transitioned status to: ${data.status}`;
    if (type === 'research_complete') return `Collected ${data.sources_count || 0} primary sources`;
    if (type === 'report_ready') return `Synthesis complete (${data.report_length || 0} chars)`;
    if (type === 'complete') return `Research completed successfully in ${data.stats?.duration_ms || 0}ms`;

    try {
      return JSON.stringify(data);
    } catch (_) {
      return String(data);
    }
  };

  return (
    <div className="bg-zinc-950 rounded-xl border border-border/50 p-4 font-mono text-sm h-64 overflow-y-auto custom-scrollbar shadow-inner relative">
      {events.length === 0 && (
        <div className="text-muted-foreground flex items-center justify-center h-full text-xs">
          Awaiting events from research runtime...
        </div>
      )}
      
      <div className="space-y-1.5">
        {events.map((entry) => {
          const time = new Date(entry.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' });
          let colorClass = 'text-foreground';
          let icon = '>';
          
          switch(entry.event.type) {
            case 'error': colorClass = 'text-red-400'; icon = '✖'; break;
            case 'planning': colorClass = 'text-purple-400'; icon = '◆'; break;
            case 'source_found': colorClass = 'text-blue-400'; icon = 'ⓘ'; break;
            case 'claim_extracted': colorClass = 'text-amber-400'; icon = '⚡'; break;
            case 'status_change': colorClass = 'text-sky-400'; icon = '↻'; break;
            case 'report_ready': colorClass = 'text-emerald-300'; icon = '★'; break;
            case 'complete': colorClass = 'text-emerald-400'; icon = '✓'; break;
            default: colorClass = 'text-foreground/80'; icon = '›'; break;
          }

          return (
            <div key={entry.id} className="flex items-start gap-2.5 hover:bg-white/5 p-1 rounded transition-colors text-xs">
              <span className="text-zinc-500 shrink-0 font-mono">[{time}]</span>
              <span className={`${colorClass} shrink-0 font-bold`}>{icon}</span>
              <span className={`${colorClass} break-all flex-1`}>
                <span className="font-semibold uppercase text-[11px] mr-2 px-1 py-0.5 rounded bg-white/5 opacity-90">
                  {entry.event.type}
                </span>
                {formatEventContent(entry.event.type, entry.event.data)}
              </span>
            </div>
          );
        })}
        <div ref={logEndRef} />
      </div>
      
      {/* Overlay gradient for fade effect at top */}
      <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-zinc-950 to-transparent pointer-events-none" />
    </div>
  );
}

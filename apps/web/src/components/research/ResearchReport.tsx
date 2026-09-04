"use client";

import { useState } from 'react';
import { Claim } from '@/types/research';
import { ClaimDrawer } from './ClaimDrawer';
import { formatConfidence } from '@/lib/utils';

interface ResearchReportProps {
  content: string | any;
  claims?: Claim[];
}

export function ResearchReport({ content, claims = [] }: ResearchReportProps) {
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);

  // Normalize content to string
  const textContent = typeof content === 'string'
    ? content
    : (content?.report || (content ? JSON.stringify(content, null, 2) : "No report content generated."));

  // Parse markdown and claim badges
  const renderContent = () => {
    // Split by claims [CLAIM:id] or source citations [Source N]
    const tokenRegex = /(\[CLAIM:[a-zA-Z0-9-]+\]|\[Source\s+\d+\])/g;
    const parts = textContent.split(tokenRegex);

    return (
      <div className="space-y-4 text-foreground/90 leading-relaxed">
        {parts.map((part: string, index: number) => {
          if (!part) return null;

          // Check if claim
          if (part.startsWith('[CLAIM:')) {
            const claimId = part.replace('[CLAIM:', '').replace(']', '');
            const claim = claims.find(c => c.id === claimId);

            if (claim) {
              const conf = claim.confidence || 0.85;
              const colorClass = conf > 0.8
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/30'
                : conf > 0.6
                ? 'bg-amber-500/20 text-amber-400 border-amber-500/30 hover:bg-amber-500/30'
                : 'bg-rose-500/20 text-rose-400 border-rose-500/30 hover:bg-rose-500/30';

              return (
                <button
                  key={index}
                  onClick={() => setSelectedClaim(claim)}
                  className={`inline-flex items-center gap-1 mx-1 px-2 py-0.5 rounded border text-xs font-bold transition-all align-middle cursor-pointer ${colorClass}`}
                  title="Click to view verified evidence"
                >
                  ✓ {formatConfidence(conf)}
                </button>
              );
            }

            return (
              <span key={index} className="inline-flex items-center mx-1 px-1.5 py-0.5 rounded bg-primary/20 text-primary text-xs font-mono border border-primary/30">
                [Claim]
              </span>
            );
          }

          // Check if source citation [Source N]
          if (part.startsWith('[Source')) {
            return (
              <span
                key={index}
                className="inline-flex items-center mx-1 px-2 py-0.5 rounded bg-primary/15 text-primary text-xs font-medium border border-primary/25 hover:bg-primary/25 transition-colors cursor-default"
              >
                {part}
              </span>
            );
          }

          // Render formatted markdown blocks
          return (
            <div
              key={index}
              className="inline"
              dangerouslySetInnerHTML={{ __html: formatMarkdown(part) }}
            />
          );
        })}
      </div>
    );
  };

  return (
    <>
      <div className="bg-card border border-border/50 rounded-2xl p-6 md:p-10 shadow-xl relative overflow-hidden">
        {/* Top gradient accent bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-emerald-400 to-primary opacity-80" />
        <div className="prose prose-invert max-w-none">
          {renderContent()}
        </div>
      </div>

      <ClaimDrawer 
        claim={selectedClaim} 
        isOpen={!!selectedClaim} 
        onClose={() => setSelectedClaim(null)} 
      />
    </>
  );
}

function formatMarkdown(text: string): string {
  return text
    .replace(/^### (.*$)/gim, '<h3 class="text-xl font-bold mt-6 mb-2 text-foreground">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-bold mt-8 mb-3 border-b border-border/40 pb-2 text-foreground">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-extrabold mt-8 mb-4 text-foreground">$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-foreground">$1</strong>')
    .replace(/\n\n/g, '<br /><br />');
}

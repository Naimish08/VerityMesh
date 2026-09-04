"use client";

import { Drawer } from '@/components/ui/Drawer';
import { Claim } from '@/types/research';
import { VerdictBadge } from '@/components/research/StatusBadge';
import { formatConfidence } from '@/lib/utils';
import { ExternalLink, ShieldCheck, FileText, Link2 } from 'lucide-react';

interface ClaimDrawerProps {
  claim: Claim | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ClaimDrawer({ claim, isOpen, onClose }: ClaimDrawerProps) {
  if (!claim) return null;

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="Claim Verification Details">
      <div className="space-y-6">
        
        {/* Verification Status */}
        <div className="space-y-2 bg-muted/30 p-4 rounded-xl border border-border/50">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground font-medium">Verdict</span>
            <VerdictBadge verdict={claim.verdict} />
          </div>
          
          <div className="pt-2">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-muted-foreground font-medium">Confidence Score</span>
              <span className="font-bold">{formatConfidence(claim.confidence)}</span>
            </div>
            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ease-out ${
                  claim.confidence > 0.8 ? 'bg-[#10b981]' : 
                  claim.confidence > 0.6 ? 'bg-[#f59e0b]' : 'bg-[#ef4444]'
                }`}
                style={{ width: `${claim.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Claim Text */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <ShieldCheck size={16} /> Extracted Claim
          </h3>
          <p className="text-foreground font-medium text-lg leading-relaxed">
            "{claim.text}"
          </p>
        </div>

        {/* Evidence */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <FileText size={16} /> Supporting Evidence
          </h3>
          <blockquote className="border-l-2 border-primary pl-4 py-1 italic text-muted-foreground bg-primary/5 rounded-r-lg">
            {claim.evidence_span}
          </blockquote>
        </div>

        {/* Source Link */}
        <div className="space-y-2 pt-4 border-t border-border/50">
          <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Link2 size={16} /> Source Context
          </h3>
          <div className="p-3 bg-card rounded-lg border border-border/50 flex flex-col gap-1">
            <span className="text-sm font-semibold truncate" title={claim.source_title}>
              {claim.source_title || 'Unknown Source'}
            </span>
            <span className="text-xs text-muted-foreground font-mono truncate">
              ID: {claim.source_id}
            </span>
          </div>
        </div>

      </div>
    </Drawer>
  );
}

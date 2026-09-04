"use client";

import { Badge } from '@/components/ui/Badge';
import { Claim } from '@/types/research';

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  switch (status) {
    case 'completed':
      return <Badge variant="verified" className="uppercase tracking-wider">Completed</Badge>;
    case 'failed':
      return <Badge variant="refuted" className="uppercase tracking-wider">Failed</Badge>;
    case 'pending':
      return <Badge variant="outline" className="uppercase tracking-wider">Pending</Badge>;
    default:
      return (
        <Badge variant="info" className="uppercase tracking-wider animate-pulse flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping mr-1" />
          {status}
        </Badge>
      );
  }
}

export function VerdictBadge({ verdict }: { verdict: Claim['verdict'] }) {
  switch (verdict) {
    case 'SUPPORTED':
      return <Badge variant="verified">Supported</Badge>;
    case 'PARTIALLY_SUPPORTED':
      return <Badge variant="inconclusive">Partially Supported</Badge>;
    case 'CONTRADICTED':
      return <Badge variant="refuted">Contradicted</Badge>;
    case 'UNVERIFIED':
      return <Badge variant="outline">Unverified</Badge>;
    default:
      return <Badge variant="default">{verdict}</Badge>;
  }
}

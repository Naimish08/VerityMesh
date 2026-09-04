"use client";

import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Source } from '@/types/research';
import { ExternalLink, Globe, BookOpen, FileText, Calendar, User } from 'lucide-react';
import { formatDate } from '@/lib/utils';

interface SourceCardProps {
  source: Source;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const getIcon = () => {
    switch (source.source_type) {
      case 'web': return <Globe size={16} />;
      case 'research_paper':
      case 'paper': return <BookOpen size={16} />;
      case 'official_documentation':
      case 'doc': return <FileText size={16} />;
      default: return <Globe size={16} />;
    }
  };

  let hostname = source.url;
  try {
    if (source.url.startsWith('http')) {
      hostname = new URL(source.url).hostname;
    }
  } catch (_) {
    hostname = source.url;
  }

  return (
    <Card className="flex flex-col h-full group hover:border-primary/50 transition-colors">
      <div className="p-4 flex gap-4">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm font-bold text-muted-foreground group-hover:bg-primary/20 group-hover:text-primary transition-colors">
          {index}
        </div>
        <div className="flex-1 min-w-0 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-semibold text-sm leading-tight text-foreground line-clamp-2" title={source.title}>
              {source.title || 'Untitled Source'}
            </h4>
            <Badge variant="outline" className="flex-shrink-0 flex items-center gap-1 bg-background text-xs">
              {getIcon()} <span className="capitalize">{source.source_type || 'web'}</span>
            </Badge>
          </div>
          
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
            {source.author && (
              <span className="flex items-center gap-1">
                <User size={12} /> {source.author}
              </span>
            )}
            {source.published_at && (
              <span className="flex items-center gap-1">
                <Calendar size={12} /> {formatDate(source.published_at)}
              </span>
            )}
          </div>
          
          {source.url && (
            <a 
              href={source.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              {hostname} <ExternalLink size={12} />
            </a>
          )}
        </div>
      </div>
    </Card>
  );
}

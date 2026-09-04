export type ResearchStatus = 'pending' | 'planning' | 'researching' | 'extracting' | 'verifying' | 'synthesizing' | 'completed' | 'failed';

export interface ResearchConfig {
  depth: 'quick' | 'standard' | 'deep' | string;
  sources: string[];
  max_sources: number;
  require_citation_verification: boolean;
  allow_autonomous_research: boolean;
}

export interface ResearchStats {
  duration_ms: number;
  sources_analyzed: number;
  claims_extracted: number;
  claims_verified: number;
  contradictions_found: number;
  citations_count: number;
  avg_confidence: number;
  tokens_used: number;
}

export interface ResearchRun {
  id: string;
  question: string;
  status: ResearchStatus;
  depth: string;
  config: ResearchConfig;
  result?: string | { report?: string; sources_count?: number; [key: string]: any };
  stats: ResearchStats;
  created_at: string;
  updated_at?: string;
  claims?: Claim[];
  sources?: Source[];
}

export interface Claim {
  id: string;
  text: string;
  verdict: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'CONTRADICTED' | 'UNVERIFIED' | string;
  confidence: number;
  evidence_span?: string;
  source_id?: string;
  source_title?: string;
  created_at?: string;
}

export interface Source {
  id: string;
  url: string;
  title?: string;
  author?: string;
  source_type?: string;
  published_at?: string;
  quality_score?: number;
  created_at?: string;
}

export interface Citation {
  id: string;
  claim_id: string;
  source_id: string;
  passage?: string;
  relevance_score?: number;
}

export type SSEEvent =
  | { type: 'planning'; data: { sub_questions?: string[]; strategy?: string; [key: string]: any } }
  | { type: 'research_start'; data: { agent?: string; sub_question?: string; [key: string]: any } }
  | { type: 'source_found'; data: { source_id?: string; title?: string; url?: string; type?: string; [key: string]: any } }
  | { type: 'chunk_stored'; data: { source_id?: string; chunks_count?: number; [key: string]: any } }
  | { type: 'claim_extracted'; data: { claim_id?: string; text?: string; confidence?: number; [key: string]: any } }
  | { type: 'synthesis_start'; data: Record<string, any> }
  | { type: 'report_ready'; data: Record<string, any> }
  | { type: 'status_change'; data: { status: string; [key: string]: any } }
  | { type: 'research_complete'; data: { sources_count?: number; [key: string]: any } }
  | { type: 'error'; data: { message: string; recoverable?: boolean; [key: string]: any } }
  | { type: 'complete'; data: { stats?: any; [key: string]: any } }
  | { type: string; data: any };

export interface LogEntry {
  id: string;
  timestamp: string;
  event: SSEEvent;
}

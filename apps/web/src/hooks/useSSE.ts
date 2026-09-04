"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { SSEEvent } from '@/types/events';

export type ConnectionState = 'connecting' | 'connected' | 'reconnecting' | 'error' | 'disconnected';

interface UseSSEOptions {
  onEvent?: (event: SSEEvent) => void;
  autoReconnect?: boolean;
}

export function useSSE(researchId: string | null, options?: UseSSEOptions) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const abortControllerRef = useRef<AbortController | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Keep onEvent in a ref to prevent recreation of connect callback on every render
  const onEventRef = useRef(options?.onEvent);
  onEventRef.current = options?.onEvent;

  const autoReconnectRef = useRef(options?.autoReconnect ?? true);
  autoReconnectRef.current = options?.autoReconnect ?? true;

  const connect = useCallback(() => {
    if (!researchId) return;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    abortControllerRef.current?.abort();
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setConnectionState('connecting');

    const envApiUrl = process.env.NEXT_PUBLIC_API_URL;
    const base = envApiUrl ? envApiUrl.replace(/\/+$/, '') : '';
    const url = `${base}/api/research/${researchId}/events`;

    fetchEventSource(url, {
      method: 'GET',
      signal: abortController.signal,
      async onopen(res) {
        if (res.ok && res.headers.get('content-type')?.includes('text/event-stream')) {
          setConnectionState('connected');
        } else {
          setConnectionState('error');
        }
      },
      onmessage(msg) {
        if (!msg.data) return;
        try {
          const parsed = JSON.parse(msg.data);
          // Extract event type from msg.event or parsed payload
          const eventType = msg.event || parsed.event_type || parsed.type || 'message';
          const eventData = parsed.data !== undefined ? parsed.data : parsed;
          
          const sseEvent: SSEEvent = {
            type: eventType as any,
            data: eventData,
          };

          onEventRef.current?.(sseEvent);

          // If complete or fatal error, close connection cleanly
          if (eventType === 'complete' || (eventType === 'error' && !eventData?.recoverable)) {
            setConnectionState('disconnected');
            abortController.abort();
          }
        } catch (err) {
          console.error('Error parsing SSE event data:', err);
        }
      },
      onclose() {
        setConnectionState('disconnected');
      },
      onerror(err) {
        console.warn('SSE stream error:', err);
        setConnectionState('error');
        if (autoReconnectRef.current && !abortController.signal.aborted) {
          setConnectionState('reconnecting');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      },
    }).catch((err) => {
      if (!abortController.signal.aborted) {
        setConnectionState('error');
      }
    });
  }, [researchId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      abortControllerRef.current?.abort();
      setConnectionState('disconnected');
    };
  }, [connect]);

  return { connectionState, reconnect: connect };
}

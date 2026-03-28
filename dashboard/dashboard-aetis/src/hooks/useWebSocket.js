// src/hooks/useWebSocket.js
import { useEffect, useRef, useCallback } from "react";

/**
 * Connects to ws://{location.host}/ws, auto-reconnects every 3 s on close.
 * Calls the provided callbacks for each message type.
 *
 * @param {{ onOpen, onClose, onError, onMessage }} handlers
 */
export function useWebSocket({ onOpen, onClose, onError, onMessage }) {
  const wsRef    = useRef(null);
  const timerRef = useRef(null);

  const connect = useCallback(() => {
    const wsUrl = "ws://" + window.location.host + "/ws";
    const ws    = new WebSocket(wsUrl);

    ws.onopen = () => onOpen?.();

    ws.onclose = () => {
      onClose?.();
      timerRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => onError?.();

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        onMessage?.(msg);
      } catch {
        // ignore malformed frames
      }
    };

    wsRef.current = ws;
  }, [onOpen, onClose, onError, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}
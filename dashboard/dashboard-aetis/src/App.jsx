// src/App.jsx
import { useState, useCallback, useRef } from "react";
import Sidebar from "./components/sidebar";
import MapView from "./components/mapview";
import { useWebSocket } from "./hooks/useWebSocket.js";
import "./styles/dashboard.css";

// ── Signal config ─────────────────────────────────────────────────────────
// Map signal_id → display name.  Add more as your backend emits them.
const SIGNAL_CONFIG = {
  signal_1: { label: "SIG · 01", name: "North" },
  signal_2: { label: "SIG · 02", name: "Central" },
  signal_3: { label: "SIG · 03", name: "South" },
};

const defaultSignals = () =>
  Object.fromEntries(
    Object.entries(SIGNAL_CONFIG).map(([id, cfg]) => [
      id,
      { ...cfg, state: "red" },   // "red" | "yellow" | "green"
    ])
  );

let eventIdCounter = 0;

export default function App() {
  // ── Live state ────────────────────────────────────────────────────────
  const [wsStatus,  setWsStatus]  = useState("connecting"); // "live" | "connecting" | "error"
  const [signals,   setSignals]   = useState(defaultSignals);
  const [evCount,   setEvCount]   = useState(0);
  const [roadCount, setRoadCount] = useState(0);
  const [events,    setEvents]    = useState([]);

  // map markers live in MapView ref so we don't re-render the whole map
  const mapRefCb = useRef(null);

  // ── Helpers ───────────────────────────────────────────────────────────
  const updateSignal = useCallback((signalId, state) => {
    setSignals((prev) => ({
      ...prev,
      [signalId]: prev[signalId]
        ? { ...prev[signalId], state }
        : { label: signalId, name: signalId, state },
    }));
  }, []);

  const pushEvent = useCallback((event) => {
    setEvents((prev) => {
      const next = [{ ...event, id: eventIdCounter++ }, ...prev];
      return next.slice(0, 60); // keep last 60
    });
  }, []);

  // ── WebSocket handlers ────────────────────────────────────────────────
  const handleOpen  = useCallback(() => setWsStatus("live"),        []);
  const handleClose = useCallback(() => setWsStatus("connecting"),  []);
  const handleError = useCallback(() => setWsStatus("error"),       []);

  const handleMessage = useCallback(
    (msg) => {
      const t = new Date().toLocaleTimeString("en-GB", {
        hour: "2-digit", minute: "2-digit", second: "2-digit",
      });

      if (msg.type === "ev_detection") {
        const d = msg.data;
        setEvCount((c) => c + 1);
        pushEvent({
          emoji: "🚑",
          name:  d.vehicle_type || "Emergency Vehicle",
          badge: "EV",
          badgeClass: "blue",
          meta: [
            `CAM-${d.camera_id}`,
            d.direction,
            `${d.speed_kmh} km/h`,
            `${Math.round(d.confidence * 100)}% conf`,
          ].filter(Boolean),
          time: t,
        });

        // Schedule corridor signal changes
        if (d.corridor) {
          d.corridor.forEach((c) => {
            setTimeout(() => updateSignal(c.signal_id, "green"), c.delay_seconds * 1000);
            setTimeout(() => updateSignal(c.signal_id, "red"),   (c.delay_seconds + c.duration) * 1000);
          });
        }

        // Add map marker if GPS provided
        if (d.gps && mapRefCb.current) {
          mapRefCb.current.addMarker({
            position: d.gps,
            color: "#3b82f6",
            label: `🚑 ${d.vehicle_type || "EV"}`,
            sublabel: `${d.direction || ""} · ${d.speed_kmh || ""} km/h`,
          });
        }
      }

      else if (msg.type === "road_damage") {
        const d = msg.data;
        const isHigh = d.severity === "HIGH";
        setRoadCount((c) => c + 1);
        pushEvent({
          emoji: "🕳️",
          name:  d.damage_type || "Road Issue",
          badge: d.severity,
          badgeClass: isHigh ? "red" : "amber",
          meta: [
            `CAM-${d.camera_id}`,
            `${Math.round(d.confidence * 100)}% conf`,
          ].filter(Boolean),
          time: t,
        });

        if (d.gps && mapRefCb.current) {
          mapRefCb.current.addMarker({
            position: d.gps,
            color: isHigh ? "#ef4444" : "#f59e0b",
            label: d.damage_type || "Road Damage",
            sublabel: `${d.severity} severity`,
          });
        }
      }

      else if (msg.type === "signal_update") {
        updateSignal(msg.signal_id, msg.state);
      }
    },
    [pushEvent, updateSignal]
  );

  useWebSocket({
    onOpen:    handleOpen,
    onClose:   handleClose,
    onError:   handleError,
    onMessage: handleMessage,
  });

  // ── Reset ─────────────────────────────────────────────────────────────
  const handleReset = useCallback(() => {
    fetch("/reset").catch(() => {});          // fire-and-forget
    setSignals(defaultSignals());
  }, []);

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className="app">
      <Sidebar
        wsStatus={wsStatus}
        signals={signals}
        evCount={evCount}
        roadCount={roadCount}
        events={events}
        onReset={handleReset}
      />
      <MapView mapRef={mapRefCb} />
    </div>
  );
}
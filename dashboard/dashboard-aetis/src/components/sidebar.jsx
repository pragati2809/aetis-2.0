// src/components/Sidebar.jsx
import SignalCard from "./signalCard";
import Stats      from "./stats";
import Feed       from "./feed";

export default function Sidebar({ wsStatus, signals, evCount, roadCount, events, onReset }) {
  const statusLabel =
    wsStatus === "live"        ? "LIVE" :
    wsStatus === "error"       ? "ERROR" :
                                 "Connecting…";

  return (
    <div className="sidebar">

      {/* ── Header ────────────────────────────────────────────────────── */}
      <div className="header-card">
        <div className="logo-row">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24">
              <path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </div>
          <div>
            <div className="logo-text-title">AETIS</div>
            <div className="logo-text-sub">Adaptive Emergency Traffic Intelligence</div>
          </div>
        </div>
        <div className="status-bar">
          <div className="status-indicator">
            <div className={`status-dot ${wsStatus}`} />
            <span>{statusLabel}</span>
          </div>
          <button className="reset-btn" onClick={onReset}>↺ Reset</button>
        </div>
      </div>

      {/* ── Signals ───────────────────────────────────────────────────── */}
      <div className="signals-section">
        <p className="section-label">Signal Nodes</p>
        <div className="signal-row">
          {Object.entries(signals).map(([id, s]) => (
            <SignalCard key={id} id={id} label={s.label} name={s.name} state={s.state} />
          ))}
        </div>
      </div>

      {/* ── Stats ─────────────────────────────────────────────────────── */}
      <Stats evCount={evCount} roadCount={roadCount} />

      {/* ── Feed ──────────────────────────────────────────────────────── */}
      <Feed events={events} />

    </div>
  );
}
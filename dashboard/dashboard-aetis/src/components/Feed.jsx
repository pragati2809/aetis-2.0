// src/components/Feed.jsx

export default function Feed({ events }) {
  return (
    <div className="feed-wrapper">
      <div className="feed-header">
        <div className="feed-title">
          <div className="feed-title-dot" />
          Live Events
        </div>
        <div className="feed-count">
          {events.length} event{events.length !== 1 ? "s" : ""}
        </div>
      </div>

      <div className="feed-scroll">
        {events.length === 0 ? (
          <div className="feed-empty">
            <svg
              className="feed-empty-icon"
              width="32" height="32" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" strokeWidth="1.5"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <p>Awaiting live events…</p>
          </div>
        ) : (
          events.map((e) => (
            <div key={e.id} className="alert-card">
              <div className="alert-top">
                <div className="alert-icon-name">
                  <span className="alert-emoji">{e.emoji}</span>
                  <span className="alert-name">{e.name}</span>
                </div>
                <span className={`badge ${e.badgeClass}`}>{e.badge}</span>
              </div>
              <div className="alert-meta">
                {e.meta?.map((m, i) => (
                  <span key={i} className="alert-meta-item">{m}</span>
                ))}
                <span className="alert-time">{e.time}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
// src/components/SignalCard.jsx

/**
 * @param {string}  id
 * @param {string}  label   e.g. "SIG · 01"
 * @param {string}  name    e.g. "North"
 * @param {string}  state   "red" | "yellow" | "green"
 */
export default function SignalCard({ label, name, state }) {
  return (
    <div className={`signal-card ${state === "green" ? "active" : ""}`}>
      <div className="signal-card-label">{label}</div>

      {/* Traffic light housing */}
      <div className="lights-housing">
        <div className={`light red    ${state === "red"    ? "on" : ""}`} />
        <div className={`light yellow ${state === "yellow" ? "on" : ""}`} />
        <div className={`light green  ${state === "green"  ? "on" : ""}`} />
      </div>

      <div className="signal-card-name">{name}</div>
    </div>
  );
}
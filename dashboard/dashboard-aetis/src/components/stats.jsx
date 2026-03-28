export default function Stats({ ev, road }) {
  return (
    <div className="stats">
      <div className="stat">
        <h3>{ev}</h3>
        <p>EV Events</p>
      </div>
      <div className="stat">
        <h3>{road}</h3>
        <p>Road Issues</p>
      </div>
    </div>
  );
}
export default function HistoryTable({ history }) {
  if (history.length === 0) {
    return <p className="history-empty">No predictions yet this session.</p>;
  }

  return (
    <table className="history-table">
      <thead>
        <tr>
          <th>Time</th>
          <th>Service</th>
          <th>Flag</th>
          <th>Prediction</th>
          <th>Risk</th>
        </tr>
      </thead>
      <tbody>
        {history.map((entry) => (
          <tr key={entry.id}>
            <td>{entry.time}</td>
            <td>{entry.service}</td>
            <td>{entry.flag}</td>
            <td>
              <span className={`badge badge--small ${entry.classification === "attack" ? "badge--attack" : "badge--normal"}`}>
                {entry.classification}
              </span>
            </td>
            <td>{Math.round(entry.risk_score * 100)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function ResultPanel({ result, error, loading }) {
  if (loading) {
    return (
      <div className="result-panel result-panel--pending">
        <p>Scoring record...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-panel result-panel--error">
        <p className="result-heading">Request failed</p>
        <p>{error}</p>
        <p className="result-hint">
          Is the API running? (<code>python -m uvicorn src.backend.main:app --reload</code> from the repo root)
        </p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="result-panel result-panel--empty">
        <p>Fill in a record and click "Classify record" to see a prediction here.</p>
      </div>
    );
  }

  const isAttack = result.classification === "attack";
  const riskPct = Math.round(result.risk_score * 100);

  return (
    <div className={`result-panel ${isAttack ? "result-panel--attack" : "result-panel--normal"}`}>
      <span className={`badge ${isAttack ? "badge--attack" : "badge--normal"}`}>
        {isAttack ? "ATTACK" : "NORMAL"}
      </span>
      <div className="risk-meter">
        <div className="risk-meter-track">
          <div className="risk-meter-fill" style={{ width: `${riskPct}%` }} />
        </div>
        <span className="risk-meter-label">{riskPct}% predicted risk of attack</span>
      </div>
      <p className="result-hint">Model label: {result.label} (0 = normal, 1 = attack)</p>
    </div>
  );
}

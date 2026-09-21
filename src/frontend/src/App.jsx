import { useEffect, useState } from "react";
import RecordForm from "./components/RecordForm";
import ResultPanel from "./components/ResultPanel";
import HistoryTable from "./components/HistoryTable";
import { ALL_FIELDS, EXAMPLE_NORMAL, EXAMPLE_ATTACK } from "./fields";
import { classifyRecord, checkHealth, API_BASE_URL } from "./api";

// Form inputs are controlled as strings (HTML inputs are always strings
// under the hood); this converts a "real" record object into that shape.
function toFormValues(record) {
  const values = {};
  for (const field of ALL_FIELDS) {
    values[field.name] = String(record[field.name]);
  }
  return values;
}

// ...and this converts form strings back into the ints/floats/strings the
// API's NetworkLogRecord schema expects.
function toPayload(values) {
  const payload = {};
  for (const field of ALL_FIELDS) {
    const raw = values[field.name];
    if (field.type === "number-int") {
      payload[field.name] = parseInt(raw, 10) || 0;
    } else if (field.type === "number-float") {
      payload[field.name] = parseFloat(raw) || 0;
    } else {
      payload[field.name] = raw;
    }
  }
  return payload;
}
function makeId() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function App() {
  const [values, setValues] = useState(() => toFormValues(EXAMPLE_NORMAL));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    checkHealth()
      .then((health) => setApiStatus(health.model_loaded ? "ok" : "not_ready"))
      .catch(() => setApiStatus("down"));
  }, []);

  function handleFieldChange(name, value) {
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  function handleLoadExample(which) {
    setValues(toFormValues(which === "attack" ? EXAMPLE_ATTACK : EXAMPLE_NORMAL));
    setResult(null);
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = toPayload(values);

    try {
      const prediction = await classifyRecord(payload);
      setResult(prediction);
      setHistory((prev) => [
        {
          id: makeId(),
          time: new Date().toLocaleTimeString(),
          service: payload.service,
          flag: payload.flag,
          classification: prediction.classification,
          risk_score: prediction.risk_score,
        },
        ...prev,
      ].slice(0, 8));
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>NADTFE</h1>
          <p className="app-subtitle">Network Anomaly Detection &amp; Threat Forecasting Engine</p>
        </div>
        <div className={`api-status api-status--${apiStatus}`}>
          <span className="api-status-dot" />
          {apiStatus === "checking" && "Checking API..."}
          {apiStatus === "ok" && `API connected (${API_BASE_URL})`}
          {apiStatus === "not_ready" && "API up, model not loaded"}
          {apiStatus === "down" && `API unreachable (${API_BASE_URL})`}
        </div>
      </header>

      <main className="app-main">
        <section className="form-section">
          <RecordForm
            values={values}
            onChange={handleFieldChange}
            onSubmit={handleSubmit}
            onLoadExample={handleLoadExample}
            loading={loading}
          />
        </section>

        <section className="result-section">
          <h2>Prediction</h2>
          <ResultPanel result={result} error={error} loading={loading} />

          <h2>Recent predictions (this session)</h2>
          <HistoryTable history={history} />
        </section>
      </main>
    </div>
  );
}

// Base URL of the NADTFE FastAPI backend. Overridable at build/dev time via
// a .env file (VITE_API_BASE_URL=...) -- see .env.example -- so the same
// build can point at localhost during development and at a deployed URL
// later without code changes.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function parseErrorDetail(response) {
  try {
    const body = await response.json();
    return body?.detail || `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

// Posts one network connection record to POST /predict and returns
// { classification, label, risk_score }.
export async function classifyRecord(record) {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(record),
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  return response.json();
}

// Hits GET /health -- used on load to show whether the backend is reachable
// and whether it finished loading the model/encoder.
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

export { API_BASE_URL };

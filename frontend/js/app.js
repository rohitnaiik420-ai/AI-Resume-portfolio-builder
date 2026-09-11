/**
 * AI Resume Builder - Optional API Helper
 * Connects the frontend to the FastAPI backend when running with a server.
 * Falls back gracefully to local-only mode (localStorage) if no backend.
 */
const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : "";

async function apiScore(data) {
  try {
    const res = await fetch(`${API_BASE}/api/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null; // fallback to client-side scoring
  }
}

async function apiSuggestions(data) {
  try {
    const res = await fetch(`${API_BASE}/api/ai-suggestions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null;
  }
}

async function apiSample(id) {
  try {
    const res = await fetch(`${API_BASE}/api/sample/${id}`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null;
  }
}

async function apiHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

window.ResumeAPI = { apiScore, apiSuggestions, apiSample, apiHealth, API_BASE };

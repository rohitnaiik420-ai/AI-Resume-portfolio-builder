/**
 * AI Resume & Portfolio Builder
 * Frontend utility module (optional API integration layer)
 * 
 * The app works 100% offline using localStorage.
 * This module optionally connects to the FastAPI backend for:
 *   - Server-side score calculation
 *   - AI suggestions
 *   - Sample profile loading
 */

const API_BASE = "http://127.0.0.1:8000";

// Check if backend is reachable
async function checkBackend() {
  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET", signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      console.log("[Backend Connected]", data);
      return true;
    }
  } catch {
    console.log("[Backend] Not reachable - running in offline mode");
  }
  return false;
}

// Fetch AI score from backend
async function fetchServerScore(resumeData) {
  try {
    const res = await fetch(`${API_BASE}/api/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(resumeData)
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.log("[Score] Using client-side calculation:", e.message);
  }
  return null;
}

// Fetch AI suggestions from backend
async function fetchAISuggestions(resumeData) {
  try {
    const res = await fetch(`${API_BASE}/api/ai-suggestions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(resumeData)
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.log("[Suggestions] Using client-side mode:", e.message);
  }
  return null;
}

// Fetch a sample profile from backend
async function fetchSampleFromServer(id) {
  try {
    const res = await fetch(`${API_BASE}/api/sample/${id}`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.log("[Sample] Using built-in profiles");
  }
  return null;
}

// Export for use in index.html
window.ResumeAPI = { checkBackend, fetchServerScore, fetchAISuggestions, fetchSampleFromServer };

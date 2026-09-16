/**
 * AI Resume & Portfolio Builder - API Helper Client v3.0
 * Connects the frontend to the FastAPI backend with seamless local fallback.
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
    return null;
  }
}

async function apiJdTailor(resumeData, jdText) {
  try {
    const res = await fetch(`${API_BASE}/api/jd-tailor`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume: resumeData, job_description: jdText })
    });
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null;
  }
}

async function apiPublish(resumeData, customSlug = "") {
  try {
    const res = await fetch(`${API_BASE}/api/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume: resumeData, custom_slug: customSlug })
    });
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null;
  }
}

async function apiGithubImport(username) {
  try {
    const res = await fetch(`${API_BASE}/api/github-import/${username}`);
    if (!res.ok) throw new Error("API error");
    return await res.json();
  } catch {
    return null;
  }
}

async function apiAtsTest(resumeText, jdText, resumeData = null) {
  try {
    const res = await fetch(`${API_BASE}/api/ats-test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, job_description: jdText, resume_data: resumeData })
    });
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

window.ResumeAPI = {
  apiScore,
  apiJdTailor,
  apiPublish,
  apiGithubImport,
  apiAtsTest,
  apiHealth,
  API_BASE
};


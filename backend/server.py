"""
AI Resume & Portfolio Builder - FastAPI Backend
Run locally : uvicorn backend.server:app --reload --port 8000
Docs        : http://localhost:8000/docs
Health      : http://localhost:8000/health
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
import os

# ─────────────────────── APP ───────────────────────────────────────────
app = FastAPI(
    title="AI Resume & Portfolio Builder API",
    description="Backend API for resume generation, AI scoring, and portfolio export",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────── CORS ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────── MODELS ────────────────────────────────────────
class PersonalInfo(BaseModel):
    name: str
    title: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    website: Optional[str] = ""
    summary: Optional[str] = ""

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if v and "@" not in v:
            raise ValueError("Invalid email address")
        return v

class Education(BaseModel):
    degree: Optional[str] = ""
    inst: Optional[str] = ""
    start: Optional[str] = ""
    end: Optional[str] = ""
    gpa: Optional[str] = ""
    loc: Optional[str] = ""
    body: Optional[str] = ""

class Experience(BaseModel):
    title: Optional[str] = ""
    co: Optional[str] = ""
    start: Optional[str] = ""
    end: Optional[str] = ""
    loc: Optional[str] = ""
    type: Optional[str] = "Full-time"
    body: Optional[str] = ""

class Project(BaseModel):
    name: Optional[str] = ""
    tech: Optional[str] = ""
    url: Optional[str] = ""
    dur: Optional[str] = ""
    body: Optional[str] = ""

class Certification(BaseModel):
    name: Optional[str] = ""
    org: Optional[str] = ""
    date: Optional[str] = ""
    cid: Optional[str] = ""

class ResumeData(BaseModel):
    p: PersonalInfo
    edu: Optional[List[Education]] = []
    exp: Optional[List[Experience]] = []
    proj: Optional[List[Project]] = []
    cert: Optional[List[Certification]] = []
    sk: Optional[List[str]] = []
    ach: Optional[str] = ""
    lang: Optional[str] = ""
    vol: Optional[str] = ""
    int_: Optional[str] = ""
    tmpl: Optional[int] = 1


# ─────────────────────── HELPERS ───────────────────────────────────────
def _compute_score(data: ResumeData) -> dict:
    p = data.p
    profile_fields = [p.name, p.title, p.email, p.phone,
                      p.location, p.linkedin, p.github, p.summary]
    sc = {
        "Profile":    round(sum(1 for f in profile_fields if f and f.strip()) / len(profile_fields) * 100),
        "Experience": min(100, len([e for e in (data.exp or []) if e.title]) * 30
                          + (30 if data.exp and data.exp[0].body else 0)),
        "Skills":     min(100, len(data.sk or []) * 10),
        "Projects":   min(100, len([pr for pr in (data.proj or []) if pr.name]) * 35),
        "Education":  min(100, len([e for e in (data.edu or []) if e.degree]) * 50),
    }
    avg = round(sum(sc.values()) / len(sc))
    tips = []
    if sc["Skills"] < 60:
        tips.append({"title": "Add More Skills",
                     "text": "Aim for 8-12 relevant skills to boost ATS match rates."})
    if sc["Experience"] < 50:
        tips.append({"title": "Enhance Experience",
                     "text": "Add quantifiable achievements (numbers, %) to each role."})
    if not p.linkedin:
        tips.append({"title": "Add LinkedIn",
                     "text": "Recruiters check LinkedIn 75% of the time."})
    if not p.summary:
        tips.append({"title": "Write a Summary",
                     "text": "A strong summary is the first thing recruiters read!"})
    if sc["Projects"] < 40:
        tips.append({"title": "Showcase Projects",
                     "text": "Add 2-3 projects to demonstrate hands-on skills."})
    if not tips:
        tips.append({"title": "Excellent Work!",
                     "text": "Your resume looks comprehensive and strong!"})
    return {"overall": avg, "breakdown": sc, "tips": tips}


# ─────────────────────── ROUTES ────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    return """
    <!DOCTYPE html><html><head>
    <meta charset='UTF-8'>
    <title>AI Resume Builder API</title>
    <style>
      body{font-family:system-ui;background:#0a0e1a;color:#e2e8f0;
           display:flex;flex-direction:column;align-items:center;
           justify-content:center;min-height:100vh;margin:0;gap:24px}
      h1{font-size:2rem;background:linear-gradient(135deg,#00d4ff,#7c3aed);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent}
      .links{display:flex;gap:16px}
      a{color:#00d4ff;text-decoration:none;padding:10px 24px;
        border:1px solid #00d4ff;border-radius:50px;transition:0.2s}
      a:hover{background:#00d4ff;color:#000}
      .status{background:#111827;border:1px solid #1e3a5f;
              border-radius:12px;padding:16px 32px;font-size:0.9rem;color:#64748b}
    </style></head><body>
    <h1>&#x1F680; AI Resume &amp; Portfolio Builder API</h1>
    <p style="color:#64748b">Backend v2.0 running successfully</p>
    <div class="links">
      <a href="/docs">&#x1F4D6; Swagger Docs</a>
      <a href="/redoc">&#x1F4CB; ReDoc</a>
      <a href="/health">&#x2705; Health Check</a>
    </div>
    <div class="status">Server is live &#x2022; No errors &#x2022; CORS enabled for all origins</div>
    </body></html>
    """

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "AI Resume & Portfolio Builder API",
        "version": "2.0.0",
        "message": "All systems operational"
    }

@app.post("/api/score", tags=["AI"])
async def calculate_score(data: ResumeData):
    """Calculate AI resume score (0-100) with breakdown and tips."""
    return _compute_score(data)

@app.post("/api/validate", tags=["Resume"])
async def validate_resume(data: ResumeData):
    """Validate required fields before generating resume."""
    errors = []
    p = data.p
    if not p.name:
        errors.append("Full name is required")
    if not p.email:
        errors.append("Email address is required")
    if not p.title:
        errors.append("Job title is required")
    return {"valid": len(errors) == 0, "errors": errors}

@app.post("/api/ai-suggestions", tags=["AI"])
async def get_ai_suggestions(data: ResumeData):
    """Return prioritized AI suggestions to improve the resume."""
    suggestions = []
    p = data.p
    if p.summary and len(p.summary) < 100:
        suggestions.append({
            "section": "Summary", "priority": "high",
            "message": "Your summary is too short. Aim for 2-3 sentences (100+ characters) highlighting your experience, skills, and value."
        })
    for exp in (data.exp or []):
        if exp.title and exp.body and len(exp.body) < 80:
            suggestions.append({
                "section": "Experience", "priority": "medium",
                "message": f"Add more detail to your '{exp.title}' role — include numbers, percentages, and impact."
            })
    if len(data.sk or []) < 6:
        suggestions.append({
            "section": "Skills", "priority": "high",
            "message": "Add more relevant skills. Having 8-15 skills significantly improves ATS match rates."
        })
    if not data.proj:
        suggestions.append({
            "section": "Projects", "priority": "medium",
            "message": "Adding 2-3 personal or academic projects greatly strengthens your resume."
        })
    return {"suggestions": suggestions, "count": len(suggestions)}

@app.get("/api/sample/{profile_id}", tags=["Samples"])
async def get_sample_profile(profile_id: int):
    """Return a pre-built sample profile for testing (1=AI Engineer, 2=Designer, 3=Cloud Architect)."""
    profiles = {
        1: {
            "p": {"name": "Alex Rivera", "title": "Senior AI & Full-Stack Engineer",
                  "email": "alex.rivera@example.com", "phone": "+1 (555) 234-5678",
                  "location": "San Francisco, CA", "linkedin": "linkedin.com/in/alexrivera-ai",
                  "github": "github.com/alexrivera-dev", "website": "alexrivera.tech",
                  "summary": "Innovative Senior AI Engineer with 5+ years architecting LLM-powered applications serving 500k+ users."},
            "sk": ["Python", "TypeScript", "React", "FastAPI", "PyTorch", "LangChain", "Docker", "Kubernetes", "AWS", "PostgreSQL"],
            "tmpl": 1
        },
        2: {
            "p": {"name": "Sarah Chen", "title": "Lead Product Designer & UX Architect",
                  "email": "sarah.chen@example.com", "phone": "+1 (555) 345-6789",
                  "location": "New York, NY", "linkedin": "linkedin.com/in/sarahchen-ux",
                  "summary": "User-centric Product Designer with 6+ years driving UX/UI strategy for FinTech and SaaS products."},
            "sk": ["Figma", "Design Systems", "User Research", "Prototyping", "UI/UX", "Tailwind CSS", "Accessibility"],
            "tmpl": 2
        },
        3: {
            "p": {"name": "David Kumar", "title": "Principal Cloud & DevOps Architect",
                  "email": "david.kumar@example.com", "phone": "+1 (555) 789-0123",
                  "location": "Austin, TX", "linkedin": "linkedin.com/in/davidkumar-cloud",
                  "summary": "DevOps Architect with 8+ years specializing in multi-cloud infrastructure and Kubernetes orchestration."},
            "sk": ["AWS", "GCP", "Kubernetes", "Terraform", "Ansible", "Helm", "Python", "Go", "GitOps"],
            "tmpl": 3
        },
    }
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Sample {profile_id} not found. Use 1, 2, or 3.")
    return profiles[profile_id]

@app.get("/api/templates", tags=["Resume"])
async def get_templates():
    """Return available resume templates."""
    return {
        "templates": [
            {"id": 1, "name": "Modern Blue", "description": "Professional gradient header, ideal for tech & startups"},
            {"id": 2, "name": "Dark Minimal", "description": "Sleek dark theme, great for creative & design roles"},
            {"id": 3, "name": "Green Tech", "description": "Fresh green gradient, perfect for sustainability & tech"},
            {"id": 4, "name": "Classic B&W", "description": "Timeless black & white, ideal for finance & law"},
        ]
    }

# ─────────────────────── STATIC FILES ──────────────────────────────────
# Serve the frontend from /app when running as a full-stack server
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

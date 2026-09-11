"""
AI Resume & Portfolio Builder - Backend Server
FastAPI backend with CORS, PDF generation, portfolio export.
Run: uvicorn backend.server:app --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(
    title="AI Resume & Portfolio Builder API",
    description="Backend API for generating resumes, portfolios, and AI scoring",
    version="1.0.0"
)

# CORS - allow any origin so the frontend works everywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DATA MODELS ──────────────────────────────────────────────
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

class Education(BaseModel):
    degree: Optional[str] = ""
    institution: Optional[str] = ""
    start: Optional[str] = ""
    end: Optional[str] = ""
    gpa: Optional[str] = ""
    location: Optional[str] = ""
    body: Optional[str] = ""

class Experience(BaseModel):
    title: Optional[str] = ""
    company: Optional[str] = ""
    start: Optional[str] = ""
    end: Optional[str] = ""
    location: Optional[str] = ""
    type: Optional[str] = "Full-time"
    body: Optional[str] = ""

class Project(BaseModel):
    name: Optional[str] = ""
    tech: Optional[str] = ""
    url: Optional[str] = ""
    duration: Optional[str] = ""
    body: Optional[str] = ""

class Certification(BaseModel):
    name: Optional[str] = ""
    org: Optional[str] = ""
    date: Optional[str] = ""
    cid: Optional[str] = ""

class ResumeData(BaseModel):
    personal: PersonalInfo
    education: Optional[List[Education]] = []
    experience: Optional[List[Experience]] = []
    projects: Optional[List[Project]] = []
    certifications: Optional[List[Certification]] = []
    skills: Optional[List[str]] = []
    achievements: Optional[str] = ""
    languages: Optional[str] = ""
    volunteer: Optional[str] = ""
    interests: Optional[str] = ""
    template: Optional[int] = 1

# ─── ROUTES ───────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <h1 style='font-family:system-ui;color:#00d4ff;text-align:center;padding:40px'>
      &#x1F680; AI Resume &amp; Portfolio Builder API
    </h1>
    <p style='text-align:center;font-family:system-ui;color:#888'>
      Visit <a href='/docs'>/docs</a> for the Swagger UI
      &nbsp;|&nbsp;
      <a href='/health'>/health</a> for status check
    </p>
    """

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Resume & Portfolio Builder API", "version": "1.0.0"}

@app.post("/api/score")
async def calculate_score(data: ResumeData):
    """Calculate AI resume score based on completeness and quality."""
    p = data.personal
    scores = {}

    # Profile completeness
    fields = [p.name, p.title, p.email, p.phone, p.location, p.linkedin, p.github, p.summary]
    scores["Profile"] = round(sum(1 for f in fields if f and f.strip()) / len(fields) * 100)

    # Experience
    exp_with_title = [e for e in data.experience if e.title]
    exp_score = min(100, len(exp_with_title) * 30 + (30 if exp_with_title and exp_with_title[0].body else 0))
    scores["Experience"] = exp_score

    # Skills
    scores["Skills"] = min(100, len(data.skills) * 10)

    # Projects
    proj_with_name = [pr for pr in data.projects if pr.name]
    scores["Projects"] = min(100, len(proj_with_name) * 35)

    # Education
    edu_with_degree = [e for e in data.education if e.degree]
    scores["Education"] = min(100, len(edu_with_degree) * 50)

    avg = round(sum(scores.values()) / len(scores))

    # AI Tips
    tips = []
    if scores["Skills"] < 60:
        tips.append({"title": "Add More Skills", "text": "Aim for 8-12 relevant skills to boost ATS match rates."})
    if scores["Experience"] < 50:
        tips.append({"title": "Enhance Experience", "text": "Add quantifiable achievements (numbers, %) to each role."})
    if not p.linkedin:
        tips.append({"title": "Add LinkedIn", "text": "Recruiters check LinkedIn 75% of the time."})
    if not p.summary:
        tips.append({"title": "Write a Summary", "text": "A strong summary is the first thing recruiters read!"})
    if scores["Projects"] < 40:
        tips.append({"title": "Showcase Projects", "text": "Add 2-3 projects to demonstrate hands-on skills."})
    if not tips:
        tips.append({"title": "Excellent Work!", "text": "Your resume looks comprehensive and strong!"})

    return {"overall": avg, "breakdown": scores, "tips": tips}

@app.post("/api/validate")
async def validate_resume(data: ResumeData):
    """Validate required fields and return errors."""
    errors = []
    if not data.personal.name:
        errors.append("Full name is required")
    if not data.personal.email:
        errors.append("Email address is required")
    if not data.personal.title:
        errors.append("Job title is required")
    if "@" not in (data.personal.email or ""):
        errors.append("Email address is not valid")
    return {"valid": len(errors) == 0, "errors": errors}

@app.post("/api/ai-suggestions")
async def get_ai_suggestions(data: ResumeData):
    """Generate AI suggestions for improving the resume."""
    suggestions = []
    p = data.personal

    if p.summary and len(p.summary) < 100:
        suggestions.append({
            "section": "Summary",
            "priority": "high",
            "message": "Your summary is too short. Aim for 2-3 sentences (100+ characters) that highlight your experience, key skills, and value proposition."
        })

    for exp in data.experience:
        if exp.title and exp.body and len(exp.body) < 80:
            suggestions.append({
                "section": "Experience",
                "priority": "medium",
                "message": f"Add more detail to your '{exp.title}' role. Include quantifiable achievements like percentages, numbers, or impact metrics."
            })

    if len(data.skills) < 6:
        suggestions.append({
            "section": "Skills",
            "priority": "high",
            "message": "Add more relevant skills. Having 8-15 skills significantly increases ATS (Applicant Tracking System) match rates."
        })

    if not data.projects:
        suggestions.append({
            "section": "Projects",
            "priority": "medium",
            "message": "Adding personal or academic projects greatly strengthens your resume, especially for tech roles."
        })

    return {"suggestions": suggestions, "count": len(suggestions)}

@app.get("/api/sample/{profile_id}")
async def get_sample_profile(profile_id: int):
    """Return a sample profile for testing."""
    profiles = {
        1: {
            "personal": {
                "name": "Alex Rivera",
                "title": "Senior AI & Full-Stack Engineer",
                "email": "alex.rivera@example.com",
                "phone": "+1 (555) 234-5678",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/alexrivera-ai",
                "github": "github.com/alexrivera-dev",
                "website": "alexrivera.tech",
                "summary": "Innovative Senior AI & Full-Stack Engineer with 5+ years of experience architecting LLM-powered applications and scalable microservices."
            },
            "skills": ["Python", "TypeScript", "React", "FastAPI", "PyTorch", "LangChain", "Docker", "Kubernetes", "AWS"],
            "template": 1
        },
        2: {
            "personal": {
                "name": "Sarah Chen",
                "title": "Lead Product Designer & UX Architect",
                "email": "sarah.chen@example.com",
                "phone": "+1 (555) 345-6789",
                "location": "New York, NY",
                "linkedin": "linkedin.com/in/sarahchen-ux",
                "summary": "User-centric Product Designer with 6+ years driving end-to-end UX/UI strategy."
            },
            "skills": ["Figma", "Design Systems", "User Research", "Prototyping", "UI/UX", "HTML5/CSS3"],
            "template": 2
        }
    }
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail=f"Sample profile {profile_id} not found. Use 1 or 2.")
    return profiles[profile_id]

# Serve frontend static files (production mode)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

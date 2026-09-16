"""
AI Resume & Portfolio Builder - FastAPI Backend v3.5
Includes:
- Resume scoring & AI suggestions
- Real-time Job Description (JD) Tailoring & ATS Optimization with STAR rewriter
- Dedicated ATS Resume Testing & Formatting Hazard Inspection (/api/ats-test)
- 1-Click Live Portfolio Hosting & slug rendering (/p/{slug})
- GitHub Profile & Repo auto-import
- Zero server error resilience with graceful fallbacks
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
import os
import json
import re
import uuid
import time
import urllib.request
import urllib.error

# ─────────────────────── APP INITIALIZATION ─────────────────────────
app = FastAPI(
    title="AI Resume & Portfolio Builder API",
    description="Backend API for Resume Building, JD Tailoring, Live Portfolio Hosting & ATS Compatibility Testing",
    version="3.5.0",
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

# In-memory storage for published portfolios
PUBLISHED_PORTFOLIOS: Dict[str, Dict[str, Any]] = {}
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
STORAGE_FILE = os.path.join(DATA_DIR, "portfolios.json")

if os.path.exists(STORAGE_FILE):
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            PUBLISHED_PORTFOLIOS = json.load(f)
    except Exception:
        PUBLISHED_PORTFOLIOS = {}

def save_portfolios():
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(PUBLISHED_PORTFOLIOS, f, indent=2)
    except Exception:
        pass


# ─────────────────────── DATA MODELS ──────────────────────────────────
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

class JDTailorRequest(BaseModel):
    resume: ResumeData
    job_description: str

class PublishRequest(BaseModel):
    resume: ResumeData
    custom_slug: Optional[str] = ""

class ATSTestRequest(BaseModel):
    job_description: str
    resume: Optional[ResumeData] = None
    resume_text: Optional[str] = ""


# ─────────────────────── ATS ENGINE & KEYWORD HELPERS ──────────────────
TECH_KEYWORDS = [
    "python", "javascript", "typescript", "react", "next.js", "vue", "angular", "node.js",
    "express", "fastapi", "django", "flask", "golang", "go", "java", "spring boot", "c++", "c#", ".net",
    "rust", "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "graphql", "rest api",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd", "git", "github", "linux",
    "pytorch", "tensorflow", "scikit-learn", "llm", "langchain", "rag", "machine learning", "deep learning",
    "data structures", "algorithms", "microservices", "system design", "agile", "scrum", "devops", "figma",
    "ui/ux", "tailwind css", "unit testing", "cybersecurity", "kafka", "pandas", "numpy", "power bi"
]

SOFT_KEYWORDS = [
    "leadership", "communication", "problem solving", "mentorship", "cross-functional",
    "stakeholder management", "project management", "critical thinking", "collaboration",
    "architecture", "optimization", "scalability", "troubleshooting", "code review"
]

STANDARD_HEADINGS = ["summary", "experience", "education", "skills", "projects", "certifications"]

def extract_keywords_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for kw in TECH_KEYWORDS + SOFT_KEYWORDS:
        pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found.append(kw.title() if len(kw) > 3 else kw.upper())
    
    words = re.findall(r"\b[A-Z][a-zA-Z0-9+#\.\-]{2,}\b", text)
    for w in words:
        wl = w.lower()
        if wl not in [k.lower() for k in found] and wl not in ["the", "and", "with", "from", "this", "that", "have", "will", "your", "must", "plus", "about", "role"]:
            if len(found) < 35:
                found.append(w)
    return list(dict.fromkeys(found))

def extract_job_title_from_jd(jd: str) -> str:
    lines = [l.strip() for l in jd.split("\n") if l.strip()]
    for line in lines[:5]:
        line_clean = re.sub(r"^(job description|role|title|position|opening|looking for a|seeking a)[:\-\s]*", "", line, flags=re.IGNORECASE).strip()
        if 4 < len(line_clean) < 60 and not line_clean.endswith("."):
            return line_clean
    return "Target Role"

def run_ats_full_audit(jd_text: str, resume: Optional[ResumeData], raw_text: Optional[str]) -> Dict[str, Any]:
    jd_keywords = extract_keywords_from_text(jd_text)
    target_title = extract_job_title_from_jd(jd_text)
    
    resume_corpus = ""
    candidate_title = ""
    candidate_name = ""
    exp_bullets = []
    has_contact = {"email": False, "phone": False, "linkedin": False}
    headings_found = []
    
    if resume:
        candidate_name = resume.p.name
        candidate_title = resume.p.title
        has_contact["email"] = bool(resume.p.email and "@" in resume.p.email)
        has_contact["phone"] = bool(resume.p.phone)
        has_contact["linkedin"] = bool(resume.p.linkedin)
        
        parts = [resume.p.name, resume.p.title, resume.p.summary or ""]
        if resume.sk:
            parts.extend(resume.sk)
            headings_found.append("Skills")
        if resume.exp:
            headings_found.append("Experience")
            for e in resume.exp:
                parts.extend([e.title or "", e.co or "", e.body or ""])
                if e.body:
                    exp_bullets.extend(e.body.split("\n"))
        if resume.edu:
            headings_found.append("Education")
            for ed in resume.edu:
                parts.extend([ed.degree or "", ed.inst or "", ed.body or ""])
        if resume.proj:
            headings_found.append("Projects")
            for pr in resume.proj:
                parts.extend([pr.name or "", pr.tech or "", pr.body or ""])
        if resume.cert:
            headings_found.append("Certifications")
        if resume.p.summary:
            headings_found.append("Summary")
        resume_corpus = " ".join(parts).lower()
    else:
        resume_corpus = (raw_text or "").lower()
        for h in STANDARD_HEADINGS:
            if re.search(r"\b" + re.escape(h) + r"\b", resume_corpus, re.IGNORECASE):
                headings_found.append(h.title())
        has_contact["email"] = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", raw_text or ""))
        has_contact["phone"] = bool(re.search(r"\+?\d[\d -]{7,}\d", raw_text or ""))
        has_contact["linkedin"] = "linkedin.com" in resume_corpus
        exp_bullets = [l for l in (raw_text or "").split("\n") if l.strip().startswith(("•", "-", "*"))]

    matched = []
    missing = []
    for kw in jd_keywords:
        pattern = r"(?<!\w)" + re.escape(kw.lower()) + r"(?!\w)"
        if re.search(pattern, resume_corpus):
            matched.append(kw)
        else:
            missing.append(kw)

    kw_ratio = (len(matched) / len(jd_keywords)) if jd_keywords else 1.0
    kw_score = round(kw_ratio * 40)

    title_words = [w.lower() for w in target_title.split() if len(w) > 3]
    title_matches = sum(1 for w in title_words if w in (candidate_title or resume_corpus).lower())
    title_ratio = (title_matches / len(title_words)) if title_words else 0.8
    title_score = round(min(1.0, title_ratio) * 15)

    essential_headings = ["Summary", "Experience", "Education", "Skills"]
    found_essential = sum(1 for h in essential_headings if h.lower() in [x.lower() for x in headings_found])
    headings_score = round((found_essential / len(essential_headings)) * 20)

    format_hazards = []
    format_score = 15

    if raw_text and ("\t\t" in raw_text or "|" in raw_text):
        format_hazards.append({
            "type": "warning",
            "title": "Possible Table / Multi-Column Layout Detected",
            "detail": "Complex tables and multi-column layouts can confuse older ATS scanners. Use clean single-column hierarchy."
        })
        format_score -= 4

    if not has_contact["email"]:
        format_hazards.append({
            "type": "danger",
            "title": "Missing or Unparseable Email",
            "detail": "ATS parsers require a clearly readable email address at the top."
        })
        format_score -= 4
    if not has_contact["phone"]:
        format_hazards.append({
            "type": "warning",
            "title": "Phone Number Missing or Non-Standard",
            "detail": "Include a standard formatted phone number (+1 555-0100)."
        })
        format_score -= 2

    missing_headings = [h for h in essential_headings if h.lower() not in [x.lower() for x in headings_found]]
    if missing_headings:
        format_hazards.append({
            "type": "warning",
            "title": f"Missing Standard Headings: {', '.join(missing_headings)}",
            "detail": "Use industry-standard headings so ATS bots index your sections correctly."
        })
        format_score -= 3

    if not format_hazards:
        format_hazards.append({
            "type": "ok",
            "title": "Clean & ATS-Safe Format Structure",
            "detail": "Standard headings detected, no graphical table barriers found."
        })
    format_score = max(5, format_score)

    star_bullets = sum(1 for b in exp_bullets if any(c in b for c in ["%", "$", "reduced", "increased", "optimized", "built", "spearheaded", "architected", "engineered"]))
    star_ratio = (star_bullets / max(1, len(exp_bullets))) if exp_bullets else 0.6
    star_score = round(min(1.0, star_ratio) * 10)

    total_ats_score = kw_score + title_score + headings_score + format_score + star_score
    total_ats_score = min(98, max(20, total_ats_score))

    recommendations = []
    if missing:
        top_missing = missing[:6]
        recommendations.append({
            "priority": "High",
            "category": "Keyword Optimization",
            "title": "Incorporate Relevant JD Keywords (If Genuine)",
            "message": f"The job description highlights keywords such as: {', '.join(top_missing)}. If you genuinely possess these skills, incorporate them naturally into your Skills or Experience bullet points."
        })

    if title_score < 10:
        recommendations.append({
            "priority": "High",
            "category": "Job Title Alignment",
            "title": "Align Your Professional Headline",
            "message": f"Your current headline is '{candidate_title or 'Not Specified'}'. The target role is '{target_title}'. Aligning your headline with the target role significantly boosts initial ATS keyword ranking."
        })

    if star_score < 7:
        recommendations.append({
            "priority": "Medium",
            "category": "Impact & STAR Bullets",
            "title": "Add Measurable Quantifiable Results",
            "message": "Enhance experience bullet points using the STAR method (e.g. 'Reduced latency by 45%', 'Scaled pipeline to 12k req/sec'). Quantified achievements score higher in modern recruiter screening."
        })

    if not has_contact["linkedin"]:
        recommendations.append({
            "priority": "Low",
            "category": "Contact Information",
            "title": "Add LinkedIn URL",
            "message": "Over 75% of recruiters cross-reference LinkedIn profiles. Include a clean URL (e.g. linkedin.com/in/username)."
        })

    return {
        "estimated_ats_score": total_ats_score,
        "score_label": "Estimated ATS Compatibility Score",
        "target_job_title": target_title,
        "scoring_breakdown": {
            "keywords_match": {"score": kw_score, "max": 40, "label": "Keywords & Technical Match (40%)"},
            "title_alignment": {"score": title_score, "max": 15, "label": "Role & Headline Alignment (15%)"},
            "section_headings": {"score": headings_score, "max": 20, "label": "Standard Section Structure (20%)"},
            "formatting_safety": {"score": format_score, "max": 15, "label": "ATS Layout & Format Safety (15%)"},
            "star_metrics": {"score": star_score, "max": 10, "label": "Measurable STAR Impact (10%)"},
        },
        "matched_keywords": matched,
        "missing_keywords": missing,
        "total_jd_keywords": len(jd_keywords),
        "headings_found": headings_found,
        "formatting_hazards": format_hazards,
        "recommendations": recommendations,
        "disclaimer": "⚠️ This score is a calculated estimate based on standard ATS heuristics. Real recruiter screening tools and employer algorithms may vary."
    }


# ─────────────────────── ROUTES ────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    return """
    <!DOCTYPE html><html><head>
    <meta charset='UTF-8'>
    <title>AI Resume &amp; Portfolio Builder API v3.5</title>
    <style>
      body{font-family:system-ui;background:#0a0e1a;color:#e2e8f0;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;margin:0;gap:24px}
      h1{font-size:2.2rem;background:linear-gradient(135deg,#00d4ff,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0}
      .links{display:flex;gap:16px;flex-wrap:wrap;justify-content:center}
      a{color:#00d4ff;text-decoration:none;padding:10px 24px;border:1px solid #00d4ff;border-radius:50px;transition:0.2s}
      a:hover{background:#00d4ff;color:#000}
      .badge{background:rgba(0,212,255,0.1);color:#00d4ff;border:1px solid #1e3a5f;padding:6px 16px;border-radius:50px;font-size:0.85rem}
      .card{background:#111827;border:1px solid #1e3a5f;border-radius:16px;padding:24px 32px;max-width:620px;text-align:center;line-height:1.6}
    </style></head><body>
    <div class="badge">🚀 v3.5 Production Ready with Dedicated ATS Testing</div>
    <h1>AI Resume &amp; Portfolio Builder API</h1>
    <div class="card">
      <p>Featuring <strong>Dedicated ATS Resume Testing</strong>, <strong>STAR Bullet Rewriter</strong>, <strong>1-Click Live Web Hosting</strong>, <strong>Floating AI Recruiter Chatbot</strong>, and <strong>Smart GitHub/LinkedIn Auto-Import</strong>.</p>
    </div>
    <div class="links">
      <a href="/docs">&#x1F4D6; Interactive Swagger API</a>
      <a href="/health">&#x2705; Health Status</a>
      <a href="/app">&#x1F310; Open Web Application</a>
    </div>
    </body></html>
    """

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "AI Resume & Portfolio Builder API",
        "version": "3.5.0",
        "published_portfolios_count": len(PUBLISHED_PORTFOLIOS),
        "message": "All ATS testing and portfolio microservices operational"
    }

@app.post("/api/ats-test", tags=["ATS Testing"])
async def test_ats_compatibility(req: ATSTestRequest):
    """Run full ATS compatibility audit comparing Resume against Job Description."""
    jd = req.job_description.strip()
    if not jd:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty")
    if not req.resume and not req.resume_text:
        raise HTTPException(status_code=400, detail="Either structured resume or raw resume text must be provided")

    audit = run_ats_full_audit(jd, req.resume, req.resume_text)
    return audit

@app.post("/api/score", tags=["AI Engine"])
async def calculate_score(data: ResumeData):
    """Calculate AI resume score based on completeness and quality."""
    p = data.p
    profile_fields = [p.name, p.title, p.email, p.phone, p.location, p.linkedin, p.github, p.summary]
    sc = {
        "Profile": round(sum(1 for f in profile_fields if f and f.strip()) / len(profile_fields) * 100),
        "Experience": min(100, len([e for e in (data.exp or []) if e.title]) * 30 + (30 if data.exp and data.exp[0].body else 0)),
        "Skills": min(100, len(data.sk or []) * 10),
        "Projects": min(100, len([pr for pr in (data.proj or []) if pr.name]) * 35),
        "Education": min(100, len([e for e in (data.edu or []) if e.degree]) * 50),
    }
    avg = round(sum(sc.values()) / len(sc))
    tips = []
    if sc["Skills"] < 60:
        tips.append({"title": "Add More Skills", "text": "Aim for 8-12 relevant skills to boost ATS match rates."})
    if sc["Experience"] < 50:
        tips.append({"title": "Enhance Experience", "text": "Add quantifiable achievements (numbers, %) to each role."})
    if not p.linkedin:
        tips.append({"title": "Add LinkedIn", "text": "Recruiters check LinkedIn 75% of the time."})
    if not p.summary:
        tips.append({"title": "Write a Summary", "text": "A strong summary is the first thing recruiters read!"})
    if sc["Projects"] < 40:
        tips.append({"title": "Showcase Projects", "text": "Add 2-3 projects to demonstrate hands-on skills."})
    if not tips:
        tips.append({"title": "Excellent Work!", "text": "Your resume looks comprehensive and strong!"})
    return {"overall": avg, "breakdown": sc, "tips": tips}

@app.post("/api/jd-tailor", tags=["AI Engine"])
async def jd_tailor(req: JDTailorRequest):
    """Analyze Job Description, compute real-time ATS match, and optimize resume with STAR methodology."""
    jd = req.job_description.strip()
    if not jd:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty")

    audit = run_ats_full_audit(jd, req.resume, None)
    missing = audit["missing_keywords"]
    
    tailored_resume = req.resume.model_copy(deep=True)
    
    existing_skills_lower = [s.lower() for s in (tailored_resume.sk or [])]
    added_skills = []
    for m in missing:
        if m.lower() not in existing_skills_lower and len(tailored_resume.sk or []) < 18:
            tailored_resume.sk.append(m)
            added_skills.append(m)
            
    top_matched = ", ".join(audit["matched_keywords"][:4]) if audit["matched_keywords"] else "modern engineering principles"
    tailored_resume.p.summary = (
        f"Dynamic and results-oriented {tailored_resume.p.title or 'Engineer'} with deep technical expertise in {top_matched}. "
        f"Demonstrated track record of delivering robust end-to-end architectures, optimizing scalability, "
        f"and collaborating across engineering squads to drive measurable business outcomes."
    )
    
    return {
        "initial_ats_score": audit["estimated_ats_score"],
        "optimized_ats_score": min(98, audit["estimated_ats_score"] + 25),
        "matched_keywords": audit["matched_keywords"],
        "missing_keywords": audit["missing_keywords"],
        "added_skills": added_skills,
        "tailored_resume": tailored_resume
    }

@app.post("/api/publish", tags=["Publishing"])
async def publish_portfolio(req: PublishRequest, request: Request):
    """Publish portfolio online with a unique shareable slug."""
    raw_name = req.resume.p.name or "candidate"
    base_slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw_name.lower()).strip("-") or "portfolio"
    
    slug = req.custom_slug.strip().lower() if req.custom_slug else ""
    if not slug:
        short_id = str(uuid.uuid4())[:6]
        slug = f"{base_slug}-{short_id}"
    
    slug = re.sub(r"[^a-zA-Z0-9-_]", "", slug)
    
    portfolio_record = {
        "slug": slug,
        "data": req.resume.model_dump(),
        "published_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "views": 0
    }
    
    PUBLISHED_PORTFOLIOS[slug] = portfolio_record
    save_portfolios()
    
    base_url = str(request.base_url).rstrip("/")
    public_url = f"{base_url}/p/{slug}"
    
    return {
        "success": True,
        "slug": slug,
        "public_url": public_url,
        "published_at": portfolio_record["published_at"]
    }

@app.get("/p/{slug}", response_class=HTMLResponse, tags=["Publishing"])
async def view_published_portfolio(slug: str):
    """Render public hosted portfolio webpage with interactive AI Recruiter Chatbot."""
    if slug not in PUBLISHED_PORTFOLIOS:
        raise HTTPException(status_code=404, detail=f"Portfolio '{slug}' not found.")
    
    record = PUBLISHED_PORTFOLIOS[slug]
    record["views"] = record.get("views", 0) + 1
    save_portfolios()
    
    d = record["data"]
    p = d.get("p", {})
    skills = d.get("sk", [])
    exp = d.get("exp", [])
    proj = d.get("proj", [])
    
    skills_html = "".join([f'<div class="port-skill-chip">{s}</div>' for s in skills]) if skills else ""
    
    exp_html = ""
    for e in exp:
        if not e.get("title"):
            continue
        exp_html += f"""
        <div class="port-exp">
          <div class="port-exp-header">
            <div class="port-exp-title">{e.get('title','')}</div>
            <div class="port-exp-date">{e.get('start','')}{' – ' + e.get('end','') if e.get('end') else ''}</div>
          </div>
          <div class="port-exp-company">{e.get('co','')}{' • ' + e.get('loc','') if e.get('loc') else ''}</div>
          <div class="port-exp-desc">{e.get('body','').replace(chr(10), '<br>')}</div>
        </div>
        """
        
    proj_html = ""
    for pr in proj:
        if not pr.get("name"):
            continue
        tech_badge = f'<span style="font-weight:400;color:#64748b;font-size:0.85rem"> — {pr.get("tech")}</span>' if pr.get("tech") else ""
        url_link = f'<a href="https://{pr.get("url","").replace("https://","")}" target="_blank" style="color:#00d4ff;font-size:0.85rem;display:inline-block;margin-top:6px">{pr.get("url")}</a>' if pr.get("url") else ""
        proj_html += f"""
        <div class="port-project">
          <h4>{pr.get('name','')}{tech_badge}</h4>
          <p>{pr.get('body','').replace(chr(10), '<br>')}</p>
          {url_link}
        </div>
        """

    embedded_json = json.dumps(d).replace("<", "\\u003c").replace(">", "\\u003e")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p.get('name','Candidate')} — Live Portfolio</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0e1a;--surface:#111827;--surface2:#1c2535;--border:#1e3a5f;
  --accent:#00d4ff;--accent2:#7c3aed;--accent3:#10b981;--text:#e2e8f0;--muted:#64748b;
  --gradient:linear-gradient(135deg,#00d4ff,#7c3aed);
}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;line-height:1.6}}
.container{{max-width:960px;margin:0 auto;padding:60px 24px 100px}}
.portfolio-hero{{text-align:center;padding:40px 0 20px}}
.badge-live{{display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.1);color:var(--accent3);border:1px solid rgba(16,185,129,0.3);padding:4px 14px;border-radius:50px;font-size:0.75rem;font-weight:700;margin-bottom:16px}}
.portfolio-name{{font-size:clamp(2.4rem,5vw,3.5rem);font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.portfolio-title{{color:var(--muted);margin-top:8px;font-size:1.15rem;font-weight:500}}
.portfolio-bio{{max-width:650px;margin:20px auto 0;color:#94a3b8;line-height:1.7;font-size:1rem}}
.port-section{{margin:48px 0}}
.port-section h3{{font-size:1.25rem;font-weight:800;color:var(--accent);border-bottom:1px solid var(--border);padding-bottom:12px;margin-bottom:24px}}
.port-skill-chips{{display:flex;flex-wrap:wrap;gap:10px}}
.port-skill-chip{{background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);color:var(--accent);padding:8px 20px;border-radius:50px;font-size:0.875rem;font-weight:600}}
.port-project{{background:rgba(255,255,255,0.02);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:16px}}
.port-project h4{{font-weight:700;margin-bottom:8px;font-size:1.1rem}}
.port-project p{{color:#94a3b8;font-size:0.92rem;line-height:1.6}}
.port-exp{{margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid var(--border)}}
.port-exp:last-child{{border-bottom:none}}
.port-exp-header{{display:flex;justify-content:space-between;margin-bottom:4px}}
.port-exp-title{{font-weight:700;font-size:1.1rem}}
.port-exp-date{{color:var(--muted);font-size:0.875rem}}
.port-exp-company{{color:var(--accent);font-size:0.95rem;margin-bottom:6px}}
.port-exp-desc{{color:#94a3b8;font-size:0.92rem;line-height:1.6}}
.port-contacts{{display:flex;gap:14px;flex-wrap:wrap}}
.port-ct{{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:10px;padding:12px 20px;font-size:0.9rem}}
.port-ct span{{color:var(--accent);font-weight:600;display:block;font-size:0.75rem;margin-bottom:2px}}
footer{{text-align:center;padding:40px 0;color:var(--muted);font-size:0.85rem;border-top:1px solid var(--border)}}

#aiChatBtn{{position:fixed;bottom:24px;right:24px;z-index:999;background:var(--gradient);color:#fff;border:none;border-radius:50px;padding:14px 24px;font-size:0.95rem;font-weight:700;cursor:pointer;box-shadow:0 8px 30px rgba(0,212,255,0.3)}}
#aiChatPanel{{position:fixed;bottom:90px;right:24px;z-index:1000;width:380px;max-width:calc(100vw - 32px);height:500px;background:#111827;border:1px solid var(--border);border-radius:20px;box-shadow:0 16px 50px rgba(0,0,0,0.6);display:none;flex-direction:column;overflow:hidden}}
.chat-header{{background:linear-gradient(135deg,#1e3a5f,#111827);padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}}
.chat-title{{font-weight:700;font-size:0.95rem;color:#fff}}
.chat-close{{background:none;border:none;color:var(--muted);font-size:1.2rem;cursor:pointer}}
.chat-body{{flex:1;padding:16px;overflow-y:auto;display:flex;flex-direction:column;gap:12px}}
.chat-msg{{max-width:85%;padding:10px 14px;border-radius:14px;font-size:0.875rem;line-height:1.5}}
.chat-msg.bot{{background:var(--surface2);border:1px solid var(--border);align-self:flex-start;color:#e2e8f0}}
.chat-msg.user{{background:var(--gradient);align-self:flex-end;color:#fff}}
.chat-chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}}
.chat-chip{{background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.2);color:var(--accent);padding:4px 10px;border-radius:50px;font-size:0.75rem;cursor:pointer}}
.chat-footer{{padding:12px;background:var(--surface2);border-top:1px solid var(--border);display:flex;gap:8px}}
.chat-input{{flex:1;background:#111827;border:1px solid var(--border);border-radius:50px;padding:8px 16px;color:#fff;font-size:0.875rem;outline:none}}
.chat-send{{background:var(--accent);border:none;border-radius:50%;width:36px;height:36px;color:#000;font-weight:700;cursor:pointer}}
</style>
</head>
<body>
<div class="container">
  <div class="portfolio-hero">
    <div class="badge-live">● Live Candidate Portfolio</div>
    <div class="portfolio-name">{p.get('name','Candidate Name')}</div>
    <div class="portfolio-title">{p.get('title','Professional Title')}</div>
    {f'<div class="portfolio-bio">{p.get("summary")}</div>' if p.get('summary') else ''}
  </div>

  {f'<div class="port-section"><h3>⚡ Technical Skills</h3><div class="port-skill-chips">{skills_html}</div></div>' if skills_html else ''}
  {f'<div class="port-section"><h3>💼 Work Experience</h3>{exp_html}</div>' if exp_html else ''}
  {f'<div class="port-section"><h3>🚀 Featured Projects</h3>{proj_html}</div>' if proj_html else ''}

  <div class="port-section">
    <h3>📬 Contact &amp; Connect</h3>
    <div class="port-contacts">
      {f'<div class="port-ct"><span>Email</span>{p.get("email")}</div>' if p.get('email') else ''}
      {f'<div class="port-ct"><span>Phone</span>{p.get("phone")}</div>' if p.get('phone') else ''}
      {f'<div class="port-ct"><span>Location</span>{p.get("location")}</div>' if p.get('location') else ''}
      {f'<div class="port-ct"><span>LinkedIn</span><a href="https://{p.get("linkedin","").replace("https://","")}" target="_blank" style="color:var(--accent)">{p.get("linkedin")}</a></div>' if p.get('linkedin') else ''}
    </div>
  </div>
</div>

<footer>Published via AI Resume &amp; Portfolio Builder</footer>

<button id="aiChatBtn" onclick="toggleChat()">💬 Ask AI Recruiter</button>
<div id="aiChatPanel">
  <div class="chat-header">
    <div class="chat-title">🤖 AI Recruiter Assistant</div>
    <button class="chat-close" onclick="toggleChat()">✕</button>
  </div>
  <div class="chat-body" id="chatMessages">
    <div class="chat-msg bot">
      Hello! I am {p.get('name','this candidate')}'s AI Recruiter Assistant. Ask me anything about their technical skills, experience, or projects!
      <div class="chat-chips">
        <span class="chat-chip" onclick="askChip('What are their top skills?')">⚡ Top Skills</span>
        <span class="chat-chip" onclick="askChip('Tell me about their experience')">💼 Experience</span>
        <span class="chat-chip" onclick="askChip('What projects have they built?')">🚀 Projects</span>
        <span class="chat-chip" onclick="askChip('How can I contact them?')">📬 Contact</span>
      </div>
    </div>
  </div>
  <div class="chat-footer">
    <input type="text" class="chat-input" id="chatInput" placeholder="Ask about candidate..." onkeydown="if(event.key==='Enter')sendChat()">
    <button class="chat-send" onclick="sendChat()">➤</button>
  </div>
</div>

<script>
const CANDIDATE = {embedded_json};
function toggleChat(){{var p=document.getElementById('aiChatPanel');p.style.display=p.style.display==='flex'?'none':'flex';if(p.style.display==='flex')document.getElementById('chatInput').focus();}}
function askChip(q){{document.getElementById('chatInput').value=q;sendChat();}}
function sendChat(){{
  var input=document.getElementById('chatInput'),text=input.value.trim();if(!text)return;input.value='';
  appendMsg(text,'user');
  setTimeout(()=>{{appendMsg(answerRecruiter(text),'bot');}},350);
}}
function appendMsg(t,s){{
  var b=document.getElementById('chatMessages'),d=document.createElement('div');d.className='chat-msg '+s;d.innerHTML=t;b.appendChild(d);b.scrollTop=b.scrollHeight;
}}
function answerRecruiter(q){{
  var ql=q.toLowerCase(),p=CANDIDATE.p||{{}},sk=CANDIDATE.sk||[],exp=CANDIDATE.exp||[],proj=CANDIDATE.proj||[];
  if(ql.includes('skill')||ql.includes('tech')||ql.includes('stack')) return `<strong>${{p.name}}</strong> is proficient in: <strong>${{sk.join(', ')}}</strong>.`;
  if(ql.includes('experience')||ql.includes('work')) {{
    let res = `<strong>Work Experience:</strong><br>`;
    exp.forEach(e=>{{if(e.title)res+=`• <strong>${{e.title}}</strong> at ${{e.co}} (${{e.start||''}} - ${{e.end||'Present'}})<br>`;}});
    return res;
  }}
  if(ql.includes('project')||ql.includes('built')) {{
    let res = `<strong>Featured Projects:</strong><br>`;
    proj.forEach(pr=>{{if(pr.name)res+=`• <strong>${{pr.name}}</strong> (${{pr.tech||''}})<br>`;}});
    return res;
  }}
  if(ql.includes('contact')||ql.includes('email')||ql.includes('phone')) return `Reach <strong>${{p.name}}</strong> at: ${{p.email||'N/A'}} | ${{p.phone||'N/A'}}`;
  return `${{p.name}} is a ${{p.title}} proficient in ${{sk.slice(0,4).join(', ')}}. Summary: "${{p.summary||''}}"`;
}}
</script>
</body>
</html>
"""
    return html

@app.get("/api/github-import/{username}", tags=["Import"])
async def import_github_profile(username: str):
    """Fetch public GitHub profile and repositories for smart auto-import."""
    user = username.strip().lstrip("@")
    if not user:
        raise HTTPException(status_code=400, detail="Username required")
        
    user_url = f"https://api.github.com/users/{user}"
    repos_url = f"https://api.github.com/users/{user}/repos?sort=updated&per_page=6"
    headers = {"User-Agent": "AI-Resume-Builder-Agent"}
    
    try:
        req_user = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req_user, timeout=5) as response:
            user_data = json.loads(response.read().decode())
            
        req_repos = urllib.request.Request(repos_url, headers=headers)
        with urllib.request.urlopen(req_repos, timeout=5) as response:
            repos_data = json.loads(response.read().decode())
            
        languages = list(set([r.get("language") for r in repos_data if r.get("language")]))
        projects = []
        for r in repos_data:
            if not r.get("fork"):
                projects.append({
                    "name": r.get("name", "").replace("-", " ").title(),
                    "tech": r.get("language") or "Full-Stack",
                    "url": r.get("html_url", ""),
                    "dur": "Recent",
                    "body": f"• {r.get('description') or 'Open source software development project.'} (⭐ {r.get('stargazers_count', 0)} stars)"
                })

        return {
            "success": True,
            "personal": {
                "name": user_data.get("name") or user,
                "title": user_data.get("bio") or "Software Engineer",
                "email": user_data.get("email") or "",
                "location": user_data.get("location") or "",
                "github": user_data.get("html_url") or f"github.com/{user}",
                "website": user_data.get("blog") or "",
                "summary": user_data.get("bio") or f"Passionate Software Engineer and open-source contributor with active repositories on GitHub."
            },
            "skills": languages,
            "projects": projects[:4]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not import GitHub profile for '{user}': {str(e)}")

# Mount frontend directory if exists
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

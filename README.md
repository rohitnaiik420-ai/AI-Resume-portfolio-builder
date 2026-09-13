<div align="center">

# 🚀 AI Resume & Portfolio Builder v3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-222?logo=github)](https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder)

**Build, Tailor against Job Descriptions with STAR methodology, Publish Live Portfolios & Interact with an Embedded AI Recruiter Chatbot.**

[🌐 Live Demo (GitHub Pages)](https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder) &nbsp;|&nbsp;
[📖 API Docs (FastAPI)](http://localhost:8000/docs) &nbsp;|&nbsp;
[⚡ Offline Mode](#-offline-mode-no-server-needed)

</div>

---

## 🌟 What's New in v3.0

| Feature | Description |
|---|---|
| 🎯 **Job Description (JD) Tailoring** | Paste any target JD to compute real-time ATS match percentage (0–100%) and see matched vs missing keywords. |
| ✨ **STAR-Methodology AI Rewriter** | 1-Click optimization that rewrites experience bullet points into high-impact Situation-Task-Action-Result statements. |
| 🚀 **1-Click Live Web Hosting** | Generate instant shareable live portfolio links (`#p=...` portable state or `/p/{slug}` backend URL) with QR code generator. |
| 🤖 **Floating AI Recruiter Chatbot** | Context-aware AI chatbot widget embedded on your live portfolio to answer recruiter questions about skills, experience, and contact. |
| ⚡ **Smart Auto-Import** | Enter your GitHub username to auto-import bio, repositories, stars, and languages into your portfolio in seconds. |
| 📄 **LinkedIn / PDF Resume Parser** | Paste raw text or LinkedIn export to auto-populate all form fields. |

---

## 🗂️ Project Structure

```
AI-Resume-portfolio-builder/
├── frontend/                  # 🌐 Frontend (runs standalone or via backend)
│   ├── index.html             # Main app (self-contained, with AI chatbot & JD optimizer)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js             # API helper client for FastAPI backend
│
├── backend/                   # 🐍 FastAPI backend v3.0
│   ├── server.py              # Main API server with JD tailoring & live hosting
│   ├── requirements.txt       # Python dependencies
│   └── __init__.py
│
├── index.html                 # Root entry (synchronized with frontend/index.html)
├── package.json               # npm helper scripts
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Quick Start (No Server Needed - 100% Offline)

Just double-click `index.html` or `LAUNCH_APP.bat` to launch in your browser:

```bash
# Windows
start index.html

# Mac / Linux
open index.html
```

---

## 🐍 Full-Stack Mode (With FastAPI Backend)

### 1. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Start the backend server
```bash
uvicorn backend.server:app --reload --port 8000
```

### 3. Open in browser
- **Web App**: [http://localhost:8000/app](http://localhost:8000/app)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health check |
| `POST` | `/api/score` | Compute AI Resume Score (0-100%) |
| `POST` | `/api/jd-tailor` | ATS Job Description match & STAR bullet rewriter |
| `POST` | `/api/publish` | Publish portfolio and get permanent `/p/{slug}` URL |
| `GET` | `/p/{slug}` | Render live public candidate portfolio with AI Chatbot |
| `GET` | `/api/github-import/{user}` | Smart auto-import candidate info & repos from GitHub |
| `GET` | `/api/sample/{1,2,3}` | Pre-built test profiles (AI Engineer, Designer, Cloud Architect) |
| `GET` | `/docs` | Interactive Swagger UI |

---

## 🌐 Deploy to GitHub Pages

1. Go to repository **Settings → Pages**
2. Source: `main` branch → `/frontend` folder (or root `/`)
3. Your app is live at:  
   `https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder`

---

## 📄 License

MIT © [rohitnaiik420-ai](https://github.com/rohitnaiik420-ai)

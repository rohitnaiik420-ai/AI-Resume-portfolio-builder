<div align="center">

# 🚀 AI Resume & Portfolio Builder

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-222?logo=github)](https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder)

**Build a professional resume + portfolio website in minutes with AI — zero server errors, works offline too.**

[🌐 Live Demo](https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder) &nbsp;|&nbsp;
[📖 API Docs](https://github.com/rohitnaiik420-ai/AI-Resume-portfolio-builder) &nbsp;|&nbsp;
[⚡ Offline Mode](#-offline-mode-no-server-needed)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **7-Step Guided Form** | Personal info, education, experience, skills, projects, extras & template |
| 🤖 **AI Resume Score** | Intelligent scoring (0–100) with actionable improvement tips |
| 🎨 **4 Templates** | Modern Blue, Dark Minimal, Green Tech, Classic B&W |
| 📄 **PDF Export** | Download print-ready PDF resume instantly |
| 🌐 **Portfolio Generator** | Auto-generate a personal portfolio HTML page |
| 💾 **Auto-Save** | Browser localStorage saves your progress automatically |
| ⚡ **Sample Profiles** | 3 pre-built test profiles (AI Engineer, Designer, Cloud Architect) |
| 🔌 **REST API Backend** | FastAPI backend with Swagger docs, AI scoring endpoints |

---

## 🗂️ Project Structure

```
AI-Resume-portfolio-builder/
├── frontend/                  # 🌐 Frontend (runs standalone or via backend)
│   ├── index.html             # Main app (self-contained, no build step needed)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js             # Optional API helper for backend integration
│
├── backend/                   # 🐍 FastAPI backend
│   ├── server.py              # Main API server
│   ├── requirements.txt       # Python dependencies
│   └── __init__.py
│
├── index.html                 # Root entry (same as frontend/index.html)
├── package.json               # npm scripts for convenience
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚡ Offline Mode (No Server Needed)

Just open `index.html` in your browser — everything works 100% offline:

```bash
# Windows
start frontend/index.html

# Mac / Linux
open frontend/index.html
```

---

## 🐍 Full-Stack Mode (With FastAPI Backend)

### 1. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Start the backend server

```bash
uvicorn backend.server:app --reload --port 8000
```

### 3. Open the frontend

```
http://localhost:8000/app    ← Frontend served by backend
http://localhost:8000/docs   ← Swagger API documentation
http://localhost:8000/health ← Health check
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Server health check |
| `POST` | `/api/score` | Calculate AI resume score |
| `POST` | `/api/validate` | Validate resume fields |
| `POST` | `/api/ai-suggestions` | Get AI improvement suggestions |
| `GET`  | `/api/sample/{1,2,3}` | Load sample profiles for testing |
| `GET`  | `/api/templates` | List available resume templates |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## 🧪 Test with Sample Data

Use the built-in sample loader buttons in the app, or call the API directly:

```bash
# Load sample profile via API
curl http://localhost:8000/api/sample/1

# Score a resume via API  
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"p":{"name":"Alex Rivera","title":"Engineer","email":"alex@example.com"},"sk":["Python","React","AWS"]}'
```

---

## 🌐 Deploy to GitHub Pages (Frontend Only)

The `frontend/index.html` is fully self-contained and deploys directly to GitHub Pages:

1. Go to **Settings → Pages**
2. Source: `main` branch → `/frontend` folder
3. Your app is live at:  
   `https://rohitnaiik420-ai.github.io/AI-Resume-portfolio-builder`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| PDF Export | jsPDF + html2canvas (CDN) |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Data Validation | Pydantic v2 |
| Deployment | GitHub Pages (frontend) + any Python host (backend) |

---

## 📄 License

MIT © [rohitnaiik420-ai](https://github.com/rohitnaiik420-ai)

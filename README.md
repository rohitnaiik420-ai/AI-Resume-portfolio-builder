# 🚀 AI Resume & Portfolio Builder

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![HTML5](https://img.shields.io/badge/HTML5-Frontend-orange?logo=html5)](frontend/index.html)

> Build a **professional resume** and **personal portfolio** in minutes using AI — zero server errors, works offline, no signup required.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎨 **4 Resume Templates** | Modern Blue, Dark Minimal, Green Tech, Classic B&W |
| 🤖 **AI Resume Score** | Real-time scoring with breakdown and smart tips |
| 📄 **PDF Download** | One-click print-ready PDF (jsPDF + html2canvas) |
| 🌐 **Portfolio Export** | Auto-generate standalone portfolio HTML file |
| 💾 **Auto-Save** | localStorage persistence, resumes survive page refresh |
| ⚡ **Sample Profiles** | 3 built-in demo profiles to test instantly |
| 📱 **Mobile Friendly** | Fully responsive layout |
| 🔒 **100% Offline** | Works without any server — open index.html directly |

---

## 📁 Project Structure

```
AI-Resume-portfolio-builder/
├── frontend/
│   ├── index.html          ← Main app (self-contained, works offline)
│   ├── css/
│   │   └── style.css       ← External CSS utilities & print styles
│   └── js/
│       └── app.js          ← Optional API integration layer
├── backend/
│   ├── server.py           ← FastAPI backend (score, suggestions, samples)
│   ├── requirements.txt    ← Python dependencies
│   └── __init__.py
├── index.html              ← Root shortcut (same as frontend/index.html)
├── launch.py               ← Smart Python launcher (auto port detection)
├── LAUNCH_AGENT.bat        ← Windows interactive launcher menu
├── Quick_Launch.vbs        ← Silent instant launcher (no console window)
├── package.json            ← npm scripts for easy startup
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Option 1: Pure Offline (Zero Setup, Zero Server)
Just open the file directly — no installation needed:
```bash
# Windows
start frontend/index.html

# Or double-click LAUNCH_AGENT.bat
```

### Option 2: With FastAPI Backend (AI Score API + Suggestions)
```bash
# 1. Clone the repo
git clone https://github.com/rohitnaiik420-ai/AI-Resume-portfolio-builder.git
cd AI-Resume-portfolio-builder

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Start the backend
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000

# 4. Open the frontend
start frontend/index.html
# OR visit http://localhost:8000/static/index.html
```

### Option 3: npm Scripts
```bash
npm run setup         # Install all backend dependencies
npm start             # Start FastAPI backend server
npm run frontend      # Open frontend in browser
```

---

## 🌐 API Endpoints

Once backend is running at `http://localhost:8000`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API home page |
| `GET` | `/health` | Health check |
| `POST` | `/api/score` | Calculate AI resume score |
| `POST` | `/api/validate` | Validate resume fields |
| `POST` | `/api/ai-suggestions` | Get AI improvement suggestions |
| `GET` | `/api/sample/{1\|2}` | Load demo profile data |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

---

## 📊 Resume Templates

| Template | Best For |
|---|---|
| **Modern Blue** | Tech companies, Startups |
| **Dark Minimal** | Creative & Design roles |
| **Green Tech** | Sustainability, Environment |
| **Classic B&W** | Finance, Law, Corporate |

---

## 🛠️ Tech Stack

**Frontend**
- Pure HTML5 + CSS3 + Vanilla JavaScript
- [jsPDF](https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js) for PDF generation
- [html2canvas](https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js) for canvas capture
- localStorage for client-side data persistence

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async Python web framework
- [Pydantic v2](https://docs.pydantic.dev/) — data validation
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for full details.

---

## 🙌 Contributing

Pull requests are welcome! Open an issue first for major changes.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

Built with ❤️ by [rohitnaiik420-ai](https://github.com/rohitnaiik420-ai)

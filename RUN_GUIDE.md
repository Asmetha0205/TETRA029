# How to Run CurricuAlign AI — Complete Step-by-Step Guide

> **CurricuAlign AI**: Autonomous AI SaaS Platform aligning University Computer Science Curricula with Modern Industry Job Requirements using Gemini 1.5 Pro, Neo4j, Pinecone, FastAPI, and React 19.

---

## 📋 Table of Contents
1. [System Prerequisites](#1-system-prerequisites)
2. [Project Structure Overview](#2-project-structure-overview)
3. [Environment Configuration (`.env`)](#3-environment-configuration-env)
4. [Step-by-Step Backend Setup (FastAPI)](#4-step-by-step-backend-setup-fastapi)
5. [Step-by-Step Frontend Setup (React 19 + Vite)](#5-step-by-step-frontend-setup-react-19--vite)
6. [Running the Full Application](#6-running-the-full-application)
7. [Testing the End-to-End Workflow](#7-testing-the-end-to-end-workflow)
8. [Running Automated Test Suites](#8-running-automated-test-suites)
9. [Troubleshooting & Common Issues](#9-troubleshooting--common-issues)

---

## 1. System Prerequisites

Before running CurricuAlign AI, ensure your local development environment meets the following requirement specs:

| Requirement | Minimum Version | Recommended | Notes |
|---|---|---|---|
| **Python** | `3.11.0` | `3.11.x` | Backend runtime environment |
| **Node.js** | `v18.0.0` | `v20.19.0+` | Frontend JavaScript runtime |
| **npm** | `9.0.0` | `10.8.2+` | Frontend package manager |
| **OS** | Windows 10/11 / macOS / Linux | Windows 11 / macOS | Cross-platform supported |
| **Git** | `2.30+` | Latest | Source control |

---

## 2. Project Structure Overview

```
CurriculAlign AI/
├── backend/                        # Python FastAPI Backend Architecture
│   ├── academic_engine/            # Engine 1: PDF Syllabus Ingestion & Parsing
│   ├── industry_engine/            # Engine 2: Tech Job Scraping & Demand Index
│   ├── semantic_engine/            # Engine 3: Vector Embeddings & Similarity Matcher
│   ├── recommendation_engine/      # Engine 4: Neo4j Graph & Gemini LLM RAG
│   ├── orchestrator/               # Master Pipeline Executor
│   ├── gateway/                    # Unified API Gateways
│   ├── cache/                      # Redis Caching Service
│   ├── events/                     # Async Event Bus
│   ├── health/                     # Multi-Engine Health Checker
│   ├── monitoring/                 # Telemetry & Performance Monitor
│   ├── api/                        # FastAPI Controllers, Schemas & Routes
│   └── tests/                      # Pytest Automated Test Suites
├── frontend/                       # React 19 + Vite Frontend Application
│   ├── src/
│   │   ├── app/                    # Zustand Global App Store
│   │   ├── components/             # Reusable UI & Chart Widgets
│   │   ├── pages/                  # 12 Interactive Platform Views
│   │   ├── services/               # Axios API Client & Fallback Generators
│   │   ├── layouts/                # Platform Shell Layouts
│   │   └── routes/                 # React Router v6 Configuration
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── package.json
├── data/                           # Data storage & SQLite cache
├── RUN_GUIDE.md                    # Step-by-Step Setup & Execution Manual
└── README.md                       # Comprehensive Platform Architecture Documentation
```

---

## 3. Environment Configuration (`.env`)

CurricuAlign AI is built with **resilient fallback policies**. The application can run in **Full Live Production Mode** (with API keys) or **Demo/Hackathon Fallback Mode** (offline mode with mock data generators).

Create a `.env` file in the root directory `CurriculAlign AI/.env` (Optional for API keys):

```env
# =========================================================
# CurricuAlign AI System Configuration
# =========================================================

# Server Settings
PORT=8000
HOST=0.0.0.0
DEBUG=True
ENVIRONMENT=development

# Gemini LLM Configuration (Optional - Fallback data used if absent)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro

# Pinecone Vector Database (Optional - In-Memory vector store used if absent)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=curricualign-taxonomy

# Neo4j Knowledge Graph (Optional - In-Memory Graph Store used if absent)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Redis Caching (Optional - In-Memory LRU cache used if absent)
REDIS_URL=redis://localhost:6379/0

# Maximum Upload File Size
MAX_UPLOAD_SIZE_MB=15
```

---

## 4. Step-by-Step Backend Setup (FastAPI)

### Step 4.1: Open Terminal & Navigate to Project Root
```bash
cd "d:\CurriculAlign AI"
```

### Step 4.2: Create & Activate Python Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS / Linux (Bash/Zsh):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4.3: Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is not present, install core dependencies directly):*
```bash
pip install fastapi uvicorn pydantic pymupdf pdfplumber pytest pytest-asyncio httpx requests
```

### Step 4.4: Verify Backend Installation
Run a quick test import to verify Python environment integrity:
```bash
python -c "import fastapi, pydantic; print('FastAPI & Pydantic successfully loaded!')"
```

---

## 5. Step-by-Step Frontend Setup (React 19 + Vite)

### Step 5.1: Navigate to Frontend Directory
Open a **new terminal tab/window** and run:
```bash
cd "d:\CurriculAlign AI\frontend"
```

### Step 5.2: Install Node Dependencies
```bash
npm install
```

### Step 5.3: Verify Frontend Build Setup
Run TypeScript compiler check:
```bash
npm run build
```
*(Output should confirm 0 errors and production static files generated in `dist/`)*.

---

## 6. Running the Full Application

To run the complete platform, you will start the **Backend Server** in Terminal 1 and the **Frontend Dev Server** in Terminal 2.

### 🚀 Terminal 1: Launch Backend FastAPI Server
```bash
cd "d:\CurriculAlign AI"
.\.venv\Scripts\activate
python -m uvicorn backend.api.routes:app --reload --host 0.0.0.0 --port 8000
```
- **Backend API URL**: `http://localhost:8000`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`
- **Health Check Endpoint**: `http://localhost:8000/health`

---

### 🚀 Terminal 2: Launch Frontend Vite Dev Server
```bash
cd "d:\CurriculAlign AI\frontend"
npm run dev
```
- **Frontend App URL**: `http://localhost:3000`

---

## 7. Testing the End-to-End Workflow

Open your browser and navigate to `http://localhost:3000`.

### Step 7.1: Landing Page (`/`)
1. View the professional landing page with animated mesh gradients and 4-engine feature grid.
2. Click **"Analyze Curriculum PDF"** or **"Explore Live Dashboard Demo"**.

### Step 7.2: PDF Upload Portal (`/upload`)
1. Drag and drop any Computer Science course syllabus PDF file (e.g. `CS_Syllabus.pdf`) into the drop zone.
2. Enter university metadata:
   - **University Name**: `Stanford University School of Engineering`
   - **Academic Year**: `2025-2026`
   - **Department**: `Department of Computer Science`
3. Click **"Run Autonomous Analysis"**.

### Step 7.3: Live Pipeline Tracker (`/analysis/:id/progress`)
1. Watch the live 8-stage progress timeline (*Uploading → Parsing → Skill Extraction → Normalization → Semantic Matching → Gap Analysis → Recommendations → Completed*).
2. Inspect real-time console execution logs in the terminal log window.

### Step 7.4: Main Analytics Dashboard (`/dashboard`)
1. View overall alignment score (e.g., `72.8%`) on the semi-circle gauge widget.
2. Inspect the **Coverage Pie Chart**, **Domain Competency Radar Chart**, **Top Industry Gaps Bar Chart**, **Skill Growth Line Chart**, and **Demand Expansion Area Chart**.

### Step 7.5: Skill Gap Delta Matrix (`/gap-analysis`)
1. Search and filter curriculum skills by category (*AI/ML, DevOps, Web, Systems*) or priority (*CRITICAL, HIGH, MEDIUM*).
2. Click on any row to open the slide-over **Evidence Drawer** showing syllabus quotes vs real job market citations.

### Step 7.6: Course Insertion Recommendations (`/recommendations`)
1. Explore tailored course module recommendations (e.g. *Docker, Kubernetes, Vector DBs, Terraform*).
2. Inspect suggested insertion sites, hands-on lab prompts, capstone project deliverables, study hours, and reference links.

### Step 7.7: Learning Roadmap (`/learning-path`)
1. View the semester-by-semester milestone roadmap with dependency arrows (*Docker → Kubernetes → Redis*).

### Step 7.8: Neo4j Knowledge Graph (`/knowledge-graph`)
1. Pan, zoom, and search nodes on the **React Flow** interactive graph.
2. Click any node to open the right-side **Node Inspector** panel.

### Step 7.9: Executive Report Export (`/report`)
1. View the complete printable executive summary.
2. Click **"Export PDF / Print"** to print or save as PDF.
3. Click **"Export Markdown"** to download `report.md`.
4. Click **"Download JSON"** to download raw data `report.json`.

---

## 8. Running Automated Test Suites

### Backend Unit & Integration Tests (Pytest)
```bash
cd "d:\CurriculAlign AI"
.\.venv\Scripts\python.exe -m pytest backend/tests
```
> **Expected Output**: `27 passed in 3.80s` (100% test pass rate).

### Frontend Production Build Test
```bash
cd "d:\CurriculAlign AI\frontend"
npm run build
```
> **Expected Output**: `built in XXs` with optimized vendor chunks (`vendor-recharts`, `vendor-reactflow`, `vendor-motion`).

---

## 9. Troubleshooting & Common Issues

### Issue 1: `Port 8000 is already in use`
**Cause**: Another process or background instance of FastAPI is running on port 8000.
**Solution**:
```powershell
# Stop process on port 8000 (Windows PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### Issue 2: `Port 3000 is already in use`
**Solution**: Vite will automatically prompt to switch to port `3001` or set `PORT=3005 npm run dev`.

### Issue 3: `ModuleNotFoundError: No module named 'backend'`
**Cause**: Running python commands outside the root directory `CurriculAlign AI`.
**Solution**: Always run python commands from the root directory `d:\CurriculAlign AI` using `python -m ...`.

### Issue 4: `No GEMINI_API_KEY set` Warning
**Cause**: `.env` file does not contain a Gemini API Key.
**Solution**: This is a harmless warning. CurricuAlign AI automatically activates its dynamic mock fallback generator to deliver complete recommendations without crashing!

---

## 🏆 Project Completion Status

- **Phase 3 – Industry Intelligence Engine**: Complete
- **Phase 4 – Academic Intelligence Engine**: Complete
- **Phase 5 – Semantic Intelligence Engine**: Complete
- **Phase 6 – Recommendation Intelligence Layer**: Complete
- **Phase 7 – System Integration Orchestration**: Complete
- **Phase 8 – Frontend Dashboard & Design System**: Complete
- **Phase 9 – Testing, Optimization & Quality Assurance**: Complete
- **Phase 10 – Deployment & Hackathon Presentation Ready**: **100% READY**

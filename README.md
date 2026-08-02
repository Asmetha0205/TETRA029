# CurricuAlign AI: Autonomous Curriculum Alignment & Intelligence Platform

> **AI-Powered SaaS Platform aligning University Computer Science Curricula with Modern Industry Job Market Requirements.**

---

## 🌟 Executive Overview

**CurricuAlign AI** addresses the multi-billion dollar skill gap in higher education. By extracting course syllabi from PDF documents, computing vector embedding similarities against 1,200+ live tech job postings, and querying Neo4j Knowledge Graphs, the platform automatically detects curriculum deltas and generates semester-by-semester course insertion roadmaps.

---

## 🏛 System Architecture

CurricuAlign AI is built on 4 core Intelligence Engines coordinated by a unified FastAPI Orchestration Layer:

```
+-----------------------------------------------------------------------------------+
|                            CurricuAlign AI SaaS Platform                          |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +-----------------------+     +-----------------------+                          |
|  | Academic Engine       |     | Industry Engine       |                          |
|  | - PDF Extractor       |     | - Job Description     |                          |
|  | - Syllabus Parser     |     |   Parser              |                          |
|  | - Bloom Classifier    |     | - Market Demand Index |                          |
|  +-----------+-----------+     +-----------+-----------+                          |
|              |                             |                                      |
|              +--------------+--------------+                                      |
|                             |                                                     |
|              +--------------v--------------+                                      |
|              | Semantic Engine             |                                      |
|              | - Cosine Vector Similarity  |                                      |
|              | - ChromaDB Store            |                                      |
|              | - Coverage Classifier       |                                      |
|              +--------------+--------------+                                      |
|                             |                                                     |
|              +--------------v--------------+                                      |
|              | Recommendation Engine       |                                      |
|              | - Neo4j Knowledge Graph     |                                      |
|              | - Gemini 1.5 Pro LLM RAG    |                                      |
|              | - Learning Path Generator   |                                      |
|              +--------------+--------------+                                      |
|                             |                                                     |
|              +--------------v--------------+                                      |
|              | Unified FastAPI Backend     |                                      |
|              | - Caching & Event Bus       |                                      |
|              | - Health Monitoring         |                                      |
|              +--------------+--------------+                                      |
|                             |                                                     |
|              +--------------v--------------+                                      |
|              | React 19 Frontend Dashboard |                                      |
|              | - Dynamic Recharts Widgets  |                                      |
|              | - React Flow Knowledge Graph|                                      |
|              | - Evidence Drawer & Report  |                                      |
|              +-----------------------------+                                      |
+-----------------------------------------------------------------------------------+
```

---

## 🚀 Key Features

1. **Multimodal PDF Ingestion**: PyMuPDF & pdfplumber multi-engine text extraction with duplicate checksum detection.
2. **Real-time Semantic Vector Matching**: High-dimensional vector search computing cosine similarity scores between academic topics and industry skill registries.
3. **Neo4j Prerequisite Graph Traversal**: Maps dependency sequences for missing technologies (e.g. *Docker → Kubernetes → Redis*).
4. **Actionable Course Modules**: Gemini-backed recommendation generator producing hands-on lab exercises, mini-project prompts, estimated study hours, and documentation references.
5. **Interactive Frontend Analytics**: Built with **React 19**, **TypeScript**, **Tailwind CSS**, **Recharts**, **React Flow**, and **Framer Motion**.
6. **Executive Export Suite**: One-click export to printable PDF, Markdown summary, or raw JSON dataset.

---

## 🛠 Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, TanStack Query v5, Zustand, Framer Motion, Recharts, React Flow, Sonner.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, PyMuPDF, ChromaDB, Neo4j, Gemini 1.5 Pro API, Pytest.
- **Infrastructure**: Redis caching, async event bus, performance telemetry monitor, health check services.

---

## ⚙️ Getting Started

### Prerequisites
- Node.js `v20.19.0+` & npm `10.8.2+`
- Python `3.11+`

### 1. Backend Setup & Local Server
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI Unified Server
python -m uvicorn backend.api.routes:app --reload --port 8000
```

### 2. Frontend Setup & Dev Server
```bash
cd frontend

# Install dependencies
npm install

# Launch Vite Dev Server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Testing & Verification

### Run Backend Unit & Integration Tests
```bash
.\.venv\Scripts\python.exe -m pytest backend/tests
```
> Result: `27 passed in 3.80s` (100% pass rate).

### Run Frontend Production Build
```bash
cd frontend
npm run build
```
> Result: Code-split production bundle generated cleanly under `dist/`.

---

## 📄 API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/analyze-curriculum` | `POST` | Upload PDF & execute end-to-end multi-engine analysis |
| `/analysis/{id}` | `GET` | Retrieve full analysis results |
| `/report/{id}` | `GET` | Retrieve executive report summary |
| `/dashboard` | `GET` | Retrieve aggregate system analytics |
| `/status` | `GET` | Retrieve operational status & active job count |
| `/health` | `GET` | Run multi-engine health checks |
| `/system/statistics` | `GET` | Retrieve telemetry metrics & cache statistics |

---

## 🔒 Security & Reliability

- **Strict PDF Signature Check**: Verifies `%PDF` header magic bytes before parsing.
- **Input Sanitization**: Path traversal prevention and text bounds checking on metadata fields.
- **Fault-Tolerant Fallbacks**: In-memory graph fallback if Neo4j is offline; dynamic mock responses if Gemini API keys are absent.

---

## 📜 License & Copyright

© 2026 CurricuAlign AI. Built for Hackathon Final Presentation.

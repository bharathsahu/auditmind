# AuditMind — AI Compliance & Audit Memory Agent

> **An AI agent that acts as long-term organizational memory for internal audit and compliance teams powered by Hindsight by Vectorize.**

---

## Overview

Internal audit and compliance teams manage massive volumes of historical documentation across audit years—previous audits, finding reports, control failures, evidence, remediation actions, policies, and auditor questions.

Standard document chatbots only answer questions about currently uploaded files. **AuditMind** provides **persistent organizational memory** across audit cycles (e.g. 2024, 2025, and 2026). 

When an auditor asks:
> *"Have we had this problem before?"*

AuditMind queries **Hindsight memory**, retrieves past occurrences from previous audit cycles, explains root causes, recalls earlier remediation outcomes, and alerts the team to recurring control weaknesses.

---

## Key Features

1. **Enterprise Compliance Dashboard**: Metrics for Total Audits, Open Findings, Resolved, Overdue Remediation, High-Risk Findings, and Recurring Control Failures.
2. **Audit Management**: Create, edit, filter, and track audit scopes across departments (Finance Controls, Global Markets, IT Risk, Compliance).
3. **Findings Management & Hindsight Recall**:
   - Log findings with severity, root cause, business impact, and remediation owner.
   - **"Find Similar Historical Findings"** button triggers Hindsight memory recall to surface past identical findings.
4. **Remediation Action Tracking**: Track owner, due dates, completion dates, evidence documents, and resolution statuses.
5. **AI Audit Assistant**: Chat interface combining live database records, **Hindsight Recall & Reflect**, and LLM reasoning.
6. **Hindsight Memory Explorer**: Inspect stored Hindsight memory nodes, category breakdowns, and recurring finding lineage graphs (`FND-2024-012 -> FND-2025-024 -> FND-2026-031`).
7. **Document Ingestion**: Upload PDF, DOCX, TXT, or CSV files to extract facts into persistent Hindsight memory banks.
8. **Hybrid & Semantic Search**: Search structured database records and execute semantic Hindsight memory queries.
9. **Pre-Populated 2024–2026 Demo Data**: Pre-loaded with realistic fictional audit cycles demonstrating transaction approval control failures over 3 consecutive years.

---

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Axios, React Router v6
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2
- **Memory Engine**: **Hindsight by Vectorize** (`hindsight-client` + embedded memory bank fallback)
- **Database**: SQLite / PostgreSQL

---

## Installation & Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (runs at http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (runs at http://localhost:5173)
npm run dev
```

---

## Demo Flow

1. Open `http://localhost:5173` (Log in with default demo user `auditor` / `audit123`).
2. Explore **Dashboard** metrics showing 2024, 2025, and 2026 audit stats and the **Recurring Control Issue Alert**.
3. Navigate to **Findings**, find **`FND-2026-031`**, and click **"Find Similar Historical Findings (Hindsight)"**. Observe how Hindsight recalls findings `FND-2024-012` and `FND-2025-024`!
4. Navigate to **AI Assistant** and ask: *"Have we had this problem before?"* or *"Which findings are high risk?"*.
5. Open **Memory Explorer** to view the Hindsight memory graph, categories, and test raw memory recall queries.
6. Upload a report in **Documents** to extract memory nodes into Hindsight.

---

## Project Structure

```text
auditmind/
├── frontend/
│   ├── src/
│   │   ├── components/       # Sidebar, Navbar, MetricsCard, Modals
│   │   ├── pages/            # Dashboard, Audits, Findings, Remediation, AI Assistant, Documents, MemoryExplorer, Search, Login
│   │   ├── services/         # API integration client
│   │   ├── App.jsx           # Main routing & layout
│   │   └── index.css         # Tailwind & custom styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route controllers
│   │   ├── models/           # SQLAlchemy DB models & Pydantic schemas
│   │   ├── hindsight/        # Hindsight client & fallback memory service
│   │   ├── agents/           # AI Audit Assistant logic
│   │   ├── services/         # Document processor (PDF, DOCX, TXT, CSV)
│   │   ├── demo_data.py      # Seed data generator for 2024-2026
│   │   └── main.py           # FastAPI application entry
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── .env.example
```

# Research Intelligence & Publication Analytics Portal
### Project 14 — Agentic AI Worklets Compendium

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

The **Research Intelligence & Publication Analytics Portal (RIPAP)** is a full-stack, agentic AI platform that automates the **harvesting, verification, deduplication, and citation analytics** of academic publications for university faculty. Built as a showcase of agentic AI worklets, it orchestrates seven specialised LangGraph agents that crawl, validate, and enrich research data from multiple academic APIs—delivering accurate metrics for NIRF and NAAC compliance reporting.

---

## Purpose

| Goal | Description |
|------|-------------|
| **Automated Harvesting** | Continuously pull publications from Google Scholar, Crossref, OpenAlex, Semantic Scholar, Scopus, and Web of Science |
| **Verification & Deduplication** | Cross-reference records across sources; detect and merge duplicates using semantic vector similarity |
| **Citation Analytics** | Compute h-index, i10-index, citation counts, and trend charts per faculty and department |
| **Compliance Reporting** | Generate NIRF and NAAC report bundles (PDF + Excel) with a single click |
| **Human-in-the-Loop** | Surface uncertain duplicate pairs and unverified records to admins for review |

---

## Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI 0.111+ (async, OpenAPI auto-docs) |
| Agent Orchestration | LangGraph 0.2+ with LangChain |
| LLM | Google Gemini 1.5 Pro / OpenAI GPT-4o (configurable) |
| Database ORM | SQLAlchemy 2.0 (async) + Alembic migrations |
| Database | PostgreSQL 16 + pgvector extension |
| Cache / Queue | Redis 7 (task queuing via Celery + result caching) |
| Auth | JWT (python-jose) + bcrypt, RBAC |
| HTTP Client | httpx (async) |
| PDF Export | WeasyPrint |
| Excel Export | openpyxl |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 18 + Vite 5 |
| Styling | Tailwind CSS 3 + shadcn/ui |
| Charts | Recharts 2 |
| State | Zustand + React Query (TanStack) |
| Forms | React Hook Form + Zod |
| Routing | React Router 6 |
| Real-time | WebSocket (native browser API) |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Containerisation | Docker + Docker Compose |
| Reverse Proxy | Nginx (production) |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana (optional) |

---

## Repository Structure

```
agentic-last/
├── README.md                   ← You are here
├── ARCHITECTURE.md             ← System design & diagrams
├── DATABASE_SCHEMA.md          ← Full DB schema reference
├── API_DESIGN.md               ← REST API spec & schemas
├── AGENT_WORKFLOW.md           ← LangGraph workflow detail
├── IMPLEMENTATION_PLAN.md      ← Phased build plan
├── .env.example                ← Environment variable template
│
├── backend/
│   ├── app/
│   │   ├── main.py             ← FastAPI application entry-point
│   │   ├── config.py           ← Settings (pydantic-settings)
│   │   ├── database.py         ← Async SQLAlchemy engine/session
│   │   ├── models/             ← SQLAlchemy ORM models
│   │   ├── schemas/            ← Pydantic request/response schemas
│   │   ├── routers/            ← FastAPI route handlers
│   │   ├── agents/             ← LangGraph agent modules
│   │   │   ├── coordinator.py  ← Graph builder & entry-point
│   │   │   ├── faculty_profile_agent.py
│   │   │   ├── scholar_harvest_agent.py
│   │   │   ├── scopus_wos_agent.py
│   │   │   ├── duplicate_detection_agent.py
│   │   │   ├── citation_analytics_agent.py
│   │   │   ├── validation_agent.py
│   │   │   └── dashboard_agent.py
│   │   ├── services/           ← Business logic layer
│   │   ├── integrations/       ← External API clients
│   │   │   ├── crossref.py
│   │   │   ├── openalex.py
│   │   │   ├── semantic_scholar.py
│   │   │   ├── scopus.py
│   │   │   └── web_of_science.py
│   │   ├── auth/               ← JWT auth utilities
│   │   └── utils/              ← Shared helpers
│   ├── migrations/             ← Alembic migration scripts
│   ├── tests/                  ← Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/              ← Route-level page components
│   │   ├── components/         ← Reusable UI components
│   │   ├── hooks/              ← Custom React hooks
│   │   ├── stores/             ← Zustand state stores
│   │   ├── api/                ← API client (axios/fetch wrappers)
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── nginx/
    └── default.conf
```

---

## Quick Start

### Prerequisites
- Docker Desktop 4.x+
- Git

### 1. Clone & configure

```bash
git clone <repository-url> agentic-last
cd agentic-last
cp .env.example .env
# Edit .env — fill in your API keys
```

### 2. Launch all services

```bash
docker compose up --build -d
```

This starts:
- **db** — PostgreSQL 16 + pgvector on port `5432`
- **redis** — Redis 7 on port `6379`
- **backend** — FastAPI on port `8000`
- **worker** — Celery worker for async agent tasks
- **frontend** — React/Vite dev server on port `5173`

### 3. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Seed initial admin user

```bash
docker compose exec backend python -m app.scripts.seed_admin
```

### 5. Open the app

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:5173 |
| API docs (Swagger) | http://localhost:8000/docs |
| API docs (ReDoc) | http://localhost:8000/redoc |

---

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Super Admin** | System administrator | Full access; manage users, trigger agents, generate all reports |
| **Admin** | Department / research office admin | Manage faculty in their scope, approve duplicates, generate reports |
| **Faculty** | Individual researcher | View & edit own profile and publications; view own analytics |
| **Viewer** | Read-only stakeholder (e.g., NIRF committee) | View dashboards and reports; no write access |

---

## AI Agents

| # | Agent | Trigger | Responsibility |
|---|-------|---------|----------------|
| 1 | **Faculty Profile Agent** | On-demand / scheduled | Builds and updates faculty member profiles from institutional data |
| 2 | **Google Scholar Harvest Agent** | Scheduled / manual | Scrapes/fetches publications from Google Scholar via SerpAPI or scholar.py |
| 3 | **Scopus / WoS Verification Agent** | Post-harvest | Cross-verifies harvested records with Scopus and Web of Science APIs |
| 4 | **Duplicate Detection Agent** | Post-verification | Uses pgvector cosine similarity + LLM reasoning to detect duplicate publications |
| 5 | **Citation Analytics Agent** | Scheduled daily | Computes h-index, i10-index, citation counts; snapshots over time |
| 6 | **Validation Agent** | Pre-report | Validates data completeness and flags anomalies before report generation |
| 7 | **Dashboard Agent** | On-demand | Aggregates metrics and prepares dashboard dataset payloads |

---

## External API Integrations

| API | Purpose | Auth |
|-----|---------|------|
| [Crossref](https://api.crossref.org) | DOI metadata, citation counts | None (polite pool: email header) |
| [OpenAlex](https://openalex.org) | Open bibliographic graph | None (email header) |
| [Semantic Scholar](https://api.semanticscholar.org) | Semantic embeddings, citations | API key (optional) |
| [Scopus](https://dev.elsevier.com) | Verified journal metrics, EID | Institutional API key |
| [Web of Science](https://developer.clarivate.com) | WoS-indexed publication data | Institutional API key |

---

## Environment Configuration

Copy `.env.example` to `.env` and populate the values. See [`.env.example`](.env.example) for all variables.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit with conventional commits: `git commit -m "feat: add citation export"`
4. Open a pull request against `main`

---

## License

MIT © 2024 — Research Intelligence & Publication Analytics Portal

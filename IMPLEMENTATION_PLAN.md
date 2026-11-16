# Phased Implementation Plan

## Project: Research Intelligence & Publication Analytics Portal (Project 14)

---

## Phase 1: Foundation Architecture (Current Phase)
**Objective**: Establish complete repository scaffolding, database schema, containerization, core documentation, authentication foundation, and initial frontend shell.

- [x] Architecture, Database Schema, API Design, and Agent Workflow documentation
- [x] Docker & Docker Compose setup (`db`, `redis`, `backend`, `frontend`, `pgadmin`)
- [x] SQLAlchemy 2.0 ORM models for all 13 core entities
- [x] Alembic migration environment and PostgreSQL connection
- [x] JWT authentication and Role-Based Access Control (Admin, Research Coordinator, Faculty Member)
- [x] Initial FastAPI application with health checks and structured logging
- [x] Initial React 18 + Vite + Tailwind CSS frontend shell with routing and empty states
- [x] Base 7-agent modules and LangGraph coordinator skeleton
- [x] Unit test setup with in-memory isolation for auth and agents

**Acceptance Criteria**:
1. All configuration, models, routers, and schemas compile without syntax errors.
2. Production data starts strictly empty (zero hardcoded publications or faculty).
3. Docker Compose builds and exposes backend on `:8000` and frontend on `:3000`.

---

## Phase 2: LangGraph Multi-Agent Engine
**Objective**: Finalize autonomous agent execution logic, state transitions, and background Celery/Redis task workers.

- [ ] Connect agent triggers to Celery task queue with Redis broker
- [ ] Implement live logging emission to `agent_logs` and WebSocket status streaming
- [ ] Enable state checkpoints in LangGraph for long-running workflows
- [ ] Add Human-in-the-Loop pause and resume nodes for uncertain duplicates
- [ ] Connect pgvector embedding generation for semantic title similarity

**Files to modify/create**:
- `backend/app/agents/coordinator.py`
- `backend/app/tasks/agent_tasks.py`
- `backend/app/routers/agents.py` (WebSocket logs endpoint)

**Acceptance Criteria**:
- End-to-end multi-agent pipeline completes in background and updates `agent_executions` table.
- Logs stream to frontend in real time.

---

## Phase 3: External Scholarly API Integrations
**Objective**: Connect live, rate-limited adapters for official academic indexes.

- [ ] Crossref REST API client with polite-pool headers
- [ ] OpenAlex API client with email identification
- [ ] Semantic Scholar Academic Graph API integration
- [ ] Elsevier Scopus Abstract Retrieval API client
- [ ] Clarivate Web of Science (WoS) Starter / Expanded API client
- [ ] Resilient retry policy with exponential backoff and circuit breaking

**Files to create**:
- `backend/app/integrations/crossref.py`
- `backend/app/integrations/openalex.py`
- `backend/app/integrations/semanticscholar.py`
- `backend/app/integrations/scopus.py`
- `backend/app/integrations/wos.py`

**Acceptance Criteria**:
- Valid DOIs automatically resolve to verified metadata from Crossref / OpenAlex.
- Scopus / WoS keys securely fetched from environment; fallback cleanly to manual review when keys are omitted.

---

## Phase 4: Frontend Portal & Analytics Dashboard
**Objective**: Build out the user interface with React 18, Tailwind CSS, and Recharts.

- [ ] Complete faculty directory, search, and profile management
- [ ] Interactive publication explorer with faceted filters (year, type, status)
- [ ] Drag-and-drop Google Scholar CSV upload interface
- [ ] Interactive Recharts visualizations:
  - Year-wise publication & citation trends
  - Departmental comparative radar charts
  - $h$-index and $i10$-index metric meters
- [ ] Agent execution monitor with live progress visualizer
- [ ] Duplicate resolution queue interface for Research Coordinators

**Acceptance Criteria**:
- No mock data: displays informative empty states until user imports real records.
- Responsive design supporting mobile, tablet, and desktop viewports.

---

## Phase 5: NIRF & NAAC Accreditation Report Generation
**Objective**: Implement automated computation and document compilation for university ranking submissions.

- [ ] NIRF Research and Professional Practice (RPC) metric calculation
- [ ] NAAC Criterion 3.4 (Research Publications and Awards) compiler
- [ ] PDF generation using ReportLab / WeasyPrint
- [ ] Excel / CSV tabular export formatted to national ranking templates
- [ ] Immutable audit log record for each generated report

**Files to create**:
- `backend/app/reports/nirf_generator.py`
- `backend/app/reports/naac_generator.py`
- `backend/app/reports/pdf_exporter.py`

**Acceptance Criteria**:
- Generated reports pull directly from verified database records with verifiable calculation breakdown.

---

## Phase 6: Production Hardening, Security & CI/CD
**Objective**: Prepare platform for enterprise university deployment.

- [ ] Automated migration pipelines and database backup routines
- [ ] Rate limiting on authentication and external harvest endpoints
- [ ] Comprehensive unit and integration test suite (>80% coverage)
- [ ] OWASP security audit (CSRF, XSS, SQL injection verification)
- [ ] GitHub Actions CI workflow for linting, testing, and Docker image builds

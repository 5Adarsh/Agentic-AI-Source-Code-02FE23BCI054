# REST API Design
## Research Intelligence & Publication Analytics Portal (RIPAP)

> **Base URL:** `http://localhost:8000/api/v1`  
> **Auth:** Bearer JWT (access token) in `Authorization` header  
> **Content-Type:** `application/json` (unless noted)  
> **API Docs:** `/docs` (Swagger UI) · `/redoc` (ReDoc)

---

## Table of Contents
1. [Global Conventions](#1-global-conventions)
2. [Error Codes & Status Codes](#2-error-codes--status-codes)
3. [Role-Based Permission Matrix](#3-role-based-permission-matrix)
4. [Auth Endpoints](#4-auth-endpoints)
5. [Faculty Endpoints](#5-faculty-endpoints)
6. [Publication Endpoints](#6-publication-endpoints)
7. [Agent Endpoints](#7-agent-endpoints)
8. [Analytics Endpoints](#8-analytics-endpoints)
9. [Report Endpoints](#9-report-endpoints)
10. [WebSocket](#10-websocket)

---

## 1. Global Conventions

### Pagination
All list endpoints support cursor-based or offset-based pagination:

```
GET /publications?page=1&page_size=20&sort=year&order=desc
```

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number (1-based) |
| `page_size` | 20 | Items per page (max 100) |
| `sort` | `created_at` | Field to sort by |
| `order` | `desc` | `asc` or `desc` |

**Paginated Response Envelope:**
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 450,
    "total_pages": 23,
    "has_next": true,
    "has_prev": false
  }
}
```

### Standard Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Request IDs
Every response carries `X-Request-ID` header for tracing.

---

## 2. Error Codes & Status Codes

### HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| `200` | OK |
| `201` | Created |
| `204` | No Content (DELETE success) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorised (missing/invalid token) |
| `403` | Forbidden (role insufficient) |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `422` | Unprocessable Entity (Pydantic validation) |
| `429` | Too Many Requests (rate limit) |
| `500` | Internal Server Error |
| `503` | Service Unavailable (external API down) |

### Error Response Schema
```json
{
  "success": false,
  "error": {
    "code": "PUBLICATION_NOT_FOUND",
    "message": "Publication with id '...' was not found.",
    "details": null,
    "request_id": "req_01HXY..."
  }
}
```

### Application Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `AUTH_TOKEN_EXPIRED` | 401 | Access token expired |
| `AUTH_TOKEN_INVALID` | 401 | Malformed or tampered token |
| `AUTH_REFRESH_TOKEN_REVOKED` | 401 | Refresh token blacklisted |
| `FORBIDDEN_ROLE` | 403 | Caller lacks required role |
| `FORBIDDEN_SCOPE` | 403 | Resource outside caller's dept scope |
| `USER_NOT_FOUND` | 404 | |
| `FACULTY_NOT_FOUND` | 404 | |
| `PUBLICATION_NOT_FOUND` | 404 | |
| `AGENT_EXECUTION_NOT_FOUND` | 404 | |
| `REPORT_NOT_FOUND` | 404 | |
| `DUPLICATE_EMAIL` | 409 | Email already registered |
| `DUPLICATE_DOI` | 409 | Publication with same DOI exists |
| `AGENT_ALREADY_RUNNING` | 409 | An agent run is active for this faculty |
| `VALIDATION_ERROR` | 422 | Request body validation failed |
| `EXTERNAL_API_ERROR` | 503 | Upstream API failure |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## 3. Role-Based Permission Matrix

| Endpoint | Super Admin | Admin | Faculty | Viewer |
|----------|:-----------:|:-----:|:-------:|:------:|
| `POST /auth/login` | ✅ | ✅ | ✅ | ✅ |
| `POST /auth/refresh` | ✅ | ✅ | ✅ | ✅ |
| `POST /auth/logout` | ✅ | ✅ | ✅ | ✅ |
| `GET /users` | ✅ | ❌ | ❌ | ❌ |
| `POST /users` | ✅ | ❌ | ❌ | ❌ |
| `GET /faculty` | ✅ | ✅ | ✅ | ✅ |
| `POST /faculty` | ✅ | ✅ | ❌ | ❌ |
| `PUT /faculty/{id}` | ✅ | ✅(dept) | ✅(own) | ❌ |
| `DELETE /faculty/{id}` | ✅ | ❌ | ❌ | ❌ |
| `GET /publications` | ✅ | ✅ | ✅ | ✅ |
| `POST /publications` | ✅ | ✅ | ✅(own) | ❌ |
| `PUT /publications/{id}` | ✅ | ✅ | ✅(own) | ❌ |
| `DELETE /publications/{id}` | ✅ | ✅ | ❌ | ❌ |
| `POST /publications/import` | ✅ | ✅ | ❌ | ❌ |
| `POST /agents/trigger` | ✅ | ✅ | ❌ | ❌ |
| `GET /agents/executions` | ✅ | ✅ | ❌ | ❌ |
| `GET /agents/{id}/logs` | ✅ | ✅ | ❌ | ❌ |
| `POST /agents/{id}/resume` | ✅ | ✅ | ❌ | ❌ |
| `GET /analytics/faculty/{id}` | ✅ | ✅ | ✅(own) | ✅ |
| `GET /analytics/department/{id}` | ✅ | ✅(own) | ❌ | ✅ |
| `GET /analytics/institution` | ✅ | ✅ | ❌ | ✅ |
| `POST /reports/generate` | ✅ | ✅ | ❌ | ❌ |
| `GET /reports` | ✅ | ✅ | ❌ | ✅ |
| `GET /reports/{id}/download` | ✅ | ✅ | ❌ | ✅ |

---

## 4. Auth Endpoints

### `POST /auth/login`
Authenticate user and receive JWT tokens.

**Request:**
```json
{
  "email": "admin@university.edu",
  "password": "SecurePass123!"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "admin@university.edu",
      "role": "admin",
      "department_id": "dept-uuid",
      "full_name": "Dr. Admin User"
    }
  }
}
```

**Errors:** `AUTH_INVALID_CREDENTIALS` (401), `VALIDATION_ERROR` (422)

---

### `POST /auth/refresh`
Exchange a valid refresh token for a new access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "expires_in": 900
  }
}
```

**Errors:** `AUTH_TOKEN_INVALID` (401), `AUTH_REFRESH_TOKEN_REVOKED` (401)

---

### `POST /auth/logout`
Revoke the current refresh token (blacklist in Redis).

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

**Response `200`:**
```json
{ "success": true, "message": "Logged out successfully." }
```

---

### `GET /auth/me`
Return the currently authenticated user's profile.

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@university.edu",
    "role": "faculty",
    "department_id": "uuid",
    "faculty_profile": { "id": "uuid", "full_name": "Dr. Jane Smith" }
  }
}
```

---

## 5. Faculty Endpoints

### `GET /faculty`
List all faculty members with optional filters.

**Query Params:**
| Param | Type | Description |
|-------|------|-------------|
| `department_id` | UUID | Filter by department |
| `search` | string | Name search (trigram) |
| `is_active` | bool | Default: `true` |
| `page`, `page_size`, `sort`, `order` | — | Pagination |

**Response `200`:** Paginated list of `FacultyListItem`

```json
{
  "data": [
    {
      "id": "uuid",
      "full_name": "Dr. Ravi Kumar",
      "designation": "Professor",
      "department": { "id": "uuid", "name": "Computer Science", "code": "CSE" },
      "scholar_id": "abc123",
      "orcid": "0000-0001-2345-6789",
      "total_publications": 42,
      "h_index": 15,
      "total_citations": 890
    }
  ],
  "pagination": { ... }
}
```

---

### `POST /faculty`
Create a new faculty record. **Roles:** super_admin, admin

**Request:**
```json
{
  "full_name": "Dr. Priya Sharma",
  "first_name": "Priya",
  "last_name": "Sharma",
  "email": "priya.sharma@university.edu",
  "designation": "Associate Professor",
  "department_id": "uuid",
  "employee_id": "EMP2024001",
  "scholar_id": "xyz789",
  "scopus_author_id": "12345678900",
  "orcid": "0000-0002-3456-7890",
  "research_interests": ["Machine Learning", "NLP", "Computer Vision"]
}
```

**Response `201`:** Full `FacultyDetail` object

---

### `GET /faculty/{faculty_id}`
Get detailed faculty profile including latest citation metrics.

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "full_name": "Dr. Priya Sharma",
    "designation": "Associate Professor",
    "department": { "id": "uuid", "name": "Computer Science", "code": "CSE" },
    "employee_id": "EMP2024001",
    "email": "priya.sharma@university.edu",
    "scholar_id": "xyz789",
    "scopus_author_id": "12345678900",
    "orcid": "0000-0002-3456-7890",
    "research_interests": ["Machine Learning", "NLP"],
    "latest_metrics": {
      "h_index": 12,
      "i10_index": 8,
      "total_citations": 540,
      "total_publications": 35,
      "snapshot_date": "2024-11-15"
    },
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### `PUT /faculty/{faculty_id}`
Update faculty record. **Roles:** super_admin, admin (dept scope), faculty (own only)

**Request:** Any subset of `POST /faculty` fields.

**Response `200`:** Updated `FacultyDetail`

---

### `DELETE /faculty/{faculty_id}`
Soft-delete faculty (sets `is_active=false`). **Roles:** super_admin only

**Response `204`:** No content

---

### `GET /faculty/{faculty_id}/publications`
List all publications for a faculty member.

**Query Params:** `year`, `publication_type`, `status`, `page`, `page_size`

**Response `200`:** Paginated `PublicationListItem` list

---

## 6. Publication Endpoints

### `GET /publications`
Search and filter publications across all faculty.

**Query Params:**
| Param | Type | Description |
|-------|------|-------------|
| `faculty_id` | UUID | Filter by author |
| `department_id` | UUID | Filter by department |
| `year_from` | int | Start year |
| `year_to` | int | End year |
| `publication_type` | string | Type filter |
| `status` | string | Verification status |
| `search` | string | Title full-text search |
| `doi` | string | Exact DOI lookup |

**Response `200`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "doi": "10.1109/ACCESS.2024.12345",
      "title": "Deep Learning for Medical Image Segmentation",
      "year": 2024,
      "publication_type": "journal_article",
      "journal_name": "IEEE Access",
      "total_citations": 23,
      "status": "verified",
      "authors": [
        { "faculty_id": "uuid", "full_name": "Dr. Priya Sharma", "author_order": 1, "is_corresponding": true }
      ]
    }
  ],
  "pagination": { ... }
}
```

---

### `POST /publications`
Manually add a publication record.

**Request:**
```json
{
  "doi": "10.1109/ACCESS.2024.12345",
  "title": "Deep Learning for Medical Image Segmentation",
  "abstract": "In this paper we propose...",
  "year": 2024,
  "publication_type": "journal_article",
  "journal_name": "IEEE Access",
  "volume": "12",
  "pages": "12345-12360",
  "authors": [
    { "faculty_id": "uuid", "author_order": 1, "is_corresponding": true },
    { "external_author_name": "Dr. John Smith", "external_author_affiliation": "MIT", "author_order": 2 }
  ]
}
```

**Response `201`:** Full `PublicationDetail` object

---

### `GET /publications/{publication_id}`
Get full publication detail including all source data and verification.

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "doi": "10.1109/ACCESS.2024.12345",
    "title": "Deep Learning for Medical Image Segmentation",
    "abstract": "...",
    "year": 2024,
    "publication_type": "journal_article",
    "journal_name": "IEEE Access",
    "total_citations": 23,
    "crossref_citations": 20,
    "scopus_citations": 23,
    "status": "verified",
    "open_access": true,
    "authors": [ ... ],
    "verification": {
      "crossref_status": "found",
      "scopus_status": "found",
      "wos_status": "not_found",
      "openalex_status": "found",
      "overall_status": "verified",
      "confidence_score": 0.95
    },
    "sources": [
      { "source_name": "crossref", "source_id": "10.1109/ACCESS.2024.12345", "fetched_at": "2024-11-10T..." }
    ]
  }
}
```

---

### `PUT /publications/{publication_id}`
Update publication metadata. **Roles:** super_admin, admin, faculty (own publications)

**Request:** Partial update of publication fields.

**Response `200`:** Updated `PublicationDetail`

---

### `DELETE /publications/{publication_id}`
Delete publication record. **Roles:** super_admin, admin

**Response `204`:** No content

---

### `POST /publications/import`
Bulk import publications from a JSON/CSV payload or trigger re-harvest. **Roles:** super_admin, admin

**Request:**
```json
{
  "faculty_id": "uuid",
  "import_source": "crossref",
  "publications": [
    {
      "doi": "10.1000/xyz123",
      "title": "...",
      "year": 2023
    }
  ]
}
```

**Response `202`:**
```json
{
  "success": true,
  "data": {
    "import_job_id": "uuid",
    "status": "queued",
    "total_submitted": 15
  }
}
```

---

### `GET /publications/search`
Semantic search across publication titles and abstracts.

**Query Params:** `q` (required), `top_k` (default 10), `faculty_id`, `year_from`, `year_to`

**Response `200`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "...",
      "similarity_score": 0.94,
      "year": 2023
    }
  ]
}
```

---

### `GET /publications/duplicates`
List unresolved duplicate candidate pairs. **Roles:** super_admin, admin

**Query Params:** `resolution_status` (default: `pending`), `min_similarity` (default: 0.85)

**Response `200`:** Paginated list of `DuplicateCandidate` with both publication details

---

### `POST /publications/duplicates/{candidate_id}/resolve`
Resolve a duplicate pair. **Roles:** super_admin, admin

**Request:**
```json
{
  "resolution": "confirmed_duplicate",
  "canonical_publication_id": "uuid-of-publication-to-keep",
  "note": "Same paper submitted to two conferences."
}
```

**Response `200`:**
```json
{ "success": true, "message": "Duplicate resolved. Publication marked as duplicate." }
```

---

## 7. Agent Endpoints

### `POST /agents/trigger`
Trigger a new agent execution run. **Roles:** super_admin, admin

**Request:**
```json
{
  "agent_type": "full_harvest",
  "faculty_id": "uuid",
  "options": {
    "include_scopus": true,
    "include_wos": true,
    "force_refresh": false
  }
}
```

**Agent types:**

| `agent_type` | Description |
|-------------|-------------|
| `full_harvest` | Complete pipeline: harvest → verify → dedup → analytics |
| `scholar_only` | Google Scholar harvest only |
| `verify_only` | Re-verify already-harvested publications |
| `citation_update` | Refresh citation counts only |
| `dedup_scan` | Run duplicate detection on existing records |
| `validation` | Run validation agent only |
| `dashboard_refresh` | Refresh dashboard cache |

**Response `202`:**
```json
{
  "success": true,
  "data": {
    "execution_id": "uuid",
    "status": "pending",
    "agent_type": "full_harvest",
    "faculty_id": "uuid",
    "created_at": "2024-11-15T12:00:00Z"
  }
}
```

---

### `GET /agents/executions`
List agent execution runs with filters. **Roles:** super_admin, admin

**Query Params:** `faculty_id`, `status`, `agent_type`, `page`, `page_size`

**Response `200`:** Paginated `AgentExecutionSummary` list

---

### `GET /agents/executions/{execution_id}`
Get full detail of an agent execution. **Roles:** super_admin, admin

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "agent_type": "full_harvest",
    "status": "completed",
    "faculty": { "id": "uuid", "full_name": "Dr. Priya Sharma" },
    "triggered_by": { "id": "uuid", "email": "admin@university.edu" },
    "publications_found": 42,
    "publications_verified": 38,
    "duplicates_flagged": 2,
    "result_summary": { ... },
    "started_at": "2024-11-15T12:00:00Z",
    "completed_at": "2024-11-15T12:04:30Z",
    "duration_seconds": 270
  }
}
```

---

### `GET /agents/executions/{execution_id}/logs`
Stream or paginate agent execution logs. **Roles:** super_admin, admin

**Query Params:** `level` (filter by log level), `node` (filter by agent node), `page`, `page_size`

**Response `200`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "agent_node": "scholar_harvest",
      "log_level": "INFO",
      "message": "Fetched 42 raw publications for Dr. Priya Sharma",
      "metadata": { "scholar_id": "xyz789", "fetch_duration_ms": 1230 },
      "logged_at": "2024-11-15T12:01:15Z"
    }
  ],
  "pagination": { ... }
}
```

---

### `POST /agents/executions/{execution_id}/cancel`
Cancel a running or pending execution. **Roles:** super_admin, admin

**Response `200`:**
```json
{ "success": true, "message": "Execution cancelled." }
```

---

### `POST /agents/executions/{execution_id}/resume`
Resume a paused execution (after human-in-the-loop review). **Roles:** super_admin, admin

**Request:**
```json
{
  "resolution_data": {
    "duplicate_resolutions": [
      {
        "candidate_id": "uuid",
        "resolution": "confirmed_duplicate",
        "canonical_id": "uuid"
      }
    ]
  }
}
```

**Response `200`:**
```json
{ "success": true, "message": "Execution resumed.", "execution_id": "uuid" }
```

---

## 8. Analytics Endpoints

### `GET /analytics/faculty/{faculty_id}`
Get citation metrics for a faculty member over time.

**Query Params:** `from_date` (ISO date), `to_date` (ISO date)

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "faculty": { "id": "uuid", "full_name": "Dr. Priya Sharma" },
    "current_metrics": {
      "h_index": 14,
      "i10_index": 10,
      "total_citations": 680,
      "total_publications": 38,
      "snapshot_date": "2024-11-15"
    },
    "trend": [
      { "date": "2024-01-01", "h_index": 11, "i10_index": 7, "total_citations": 450 },
      { "date": "2024-04-01", "h_index": 12, "i10_index": 8, "total_citations": 520 },
      { "date": "2024-11-15", "h_index": 14, "i10_index": 10, "total_citations": 680 }
    ],
    "per_year_citations": {
      "2020": 45, "2021": 78, "2022": 112, "2023": 189, "2024": 256
    },
    "top_publications": [
      { "id": "uuid", "title": "...", "year": 2022, "citations": 145 }
    ]
  }
}
```

---

### `GET /analytics/department/{department_id}`
Aggregate analytics for a department. **Roles:** super_admin, admin, viewer

**Response `200`:**
```json
{
  "data": {
    "department": { "id": "uuid", "name": "Computer Science", "code": "CSE" },
    "summary": {
      "total_faculty": 28,
      "total_publications": 540,
      "total_citations": 12400,
      "avg_h_index": 9.4,
      "top_h_index": 22
    },
    "publication_types": {
      "journal_article": 320,
      "conference_paper": 180,
      "book_chapter": 40
    },
    "per_year_publications": { "2020": 65, "2021": 80, "2022": 95, "2023": 150, "2024": 150 },
    "faculty_rankings": [
      { "faculty_id": "uuid", "full_name": "Dr. ...", "h_index": 22, "total_citations": 1800 }
    ]
  }
}
```

---

### `GET /analytics/institution`
Institution-wide aggregated metrics. **Roles:** super_admin, admin, viewer

**Response `200`:** Similar structure to department analytics, scoped to all departments.

---

### `GET /analytics/h-index/{faculty_id}`
Compute and return current h-index with breakdown.

**Response `200`:**
```json
{
  "data": {
    "faculty_id": "uuid",
    "h_index": 14,
    "h_core_publications": [
      { "id": "uuid", "title": "...", "citations": 89, "rank": 1 }
    ],
    "computed_at": "2024-11-15T12:00:00Z"
  }
}
```

---

### `GET /analytics/citations/trends`
Citation trend data for charting. Supports faculty, department, or institution scope.

**Query Params:** `scope` (`faculty`|`department`|`institution`), `scope_id`, `granularity` (`month`|`quarter`|`year`), `from_date`, `to_date`

**Response `200`:**
```json
{
  "data": {
    "labels": ["2020", "2021", "2022", "2023", "2024"],
    "datasets": [
      { "name": "Total Citations", "values": [120, 230, 410, 580, 760] },
      { "name": "New Publications", "values": [8, 12, 15, 18, 20] }
    ]
  }
}
```

---

## 9. Report Endpoints

### `POST /reports/generate`
Queue a new report generation. **Roles:** super_admin, admin

**Request:**
```json
{
  "report_type": "nirf",
  "academic_year": "2024-25",
  "department_id": null,
  "file_format": "pdf",
  "report_config": {
    "include_all_departments": true,
    "include_citation_charts": true
  }
}
```

**Report types:**

| `report_type` | Description |
|-------------|-------------|
| `nirf` | NIRF Research & Publications data format |
| `naac` | NAAC criterion 3 (Research, Innovations and Extension) |
| `faculty_profile` | Individual faculty CV-style report |
| `department_summary` | Department-level publication summary |
| `custom` | Custom analytics export |

**Response `202`:**
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "status": "pending",
    "report_type": "nirf",
    "academic_year": "2024-25"
  }
}
```

---

### `GET /reports`
List generated reports. **Roles:** super_admin, admin, viewer

**Query Params:** `report_type`, `academic_year`, `department_id`, `status`

**Response `200`:** Paginated `ReportSummary` list

---

### `GET /reports/{report_id}`
Get report metadata and status.

**Response `200`:**
```json
{
  "data": {
    "id": "uuid",
    "report_type": "nirf",
    "academic_year": "2024-25",
    "status": "completed",
    "file_format": "pdf",
    "file_size_bytes": 245760,
    "generated_by": { "id": "uuid", "email": "admin@university.edu" },
    "generated_at": "2024-11-15T13:30:00Z"
  }
}
```

---

### `GET /reports/{report_id}/download`
Download the generated report file. **Roles:** super_admin, admin, viewer

**Response `200`:**
- `Content-Type: application/pdf` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="NIRF_2024-25.pdf"`

---

### `DELETE /reports/{report_id}`
Delete a report file and record. **Roles:** super_admin, admin

**Response `204`:** No content

---

## 10. WebSocket

### `WS /ws/agents/{execution_id}`
Real-time log streaming for an agent execution run.

**Connection:** Requires `token` query param: `ws://localhost:8000/ws/agents/{id}?token=<access_token>`

**Server → Client Messages:**

```json
{ "type": "log", "data": {
    "agent_node": "scholar_harvest",
    "log_level": "INFO",
    "message": "Found 42 publications",
    "logged_at": "2024-11-15T12:01:00Z"
}}
```

```json
{ "type": "status_update", "data": {
    "execution_id": "uuid",
    "status": "awaiting_review",
    "message": "2 duplicate pairs require human review"
}}
```

```json
{ "type": "run_complete", "data": {
    "execution_id": "uuid",
    "status": "completed",
    "result_summary": { "publications_found": 42, "h_index": 14 }
}}
```

```json
{ "type": "error", "data": {
    "message": "Scopus API returned 429 — rate limit exceeded",
    "agent_node": "scopus_wos_verify"
}}
```

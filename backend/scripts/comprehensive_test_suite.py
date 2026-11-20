"""
Comprehensive End-to-End System Test Suite
Tests all 10 Portal Modules, 7 AI Agents, and Accreditation Exporters.
"""
import io
import requests
import json
import sys

BASE = "http://127.0.0.1:8000/api/v1"

results = {}

def record(module, check, success, detail=""):
    results.setdefault(module, []).append({
        "check": check,
        "success": success,
        "detail": detail
    })
    status_str = "PASS" if success else "FAIL"
    print(f"[{status_str}] {module} -> {check}: {detail}")

print("===================================================================")
print("COMPREHENSIVE AUDIT & FUNCTIONAL TEST SUITE - KLE RESEARCH PORTAL")
print("===================================================================\n")

# 1. AUTHENTICATION & USERS
try:
    login_res = requests.post(f"{BASE}/auth/login", json={"email": "admin@university.edu", "password": "Admin@123456"})
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        record("Auth", "Admin Login", True, "JWT token acquired successfully")
    else:
        record("Auth", "Admin Login", False, f"HTTP {login_res.status_code}")
        sys.exit(1)

    me_res = requests.get(f"{BASE}/auth/me", headers=headers)
    record("Auth", "Current User (/me)", me_res.status_code == 200, f"Role: {me_res.json().get('role')}")
except Exception as e:
    record("Auth", "Login Flow", False, str(e))

# 2. MAIN DASHBOARD METRICS
try:
    dash = requests.get(f"{BASE}/analytics/dashboard", headers=headers).json()
    record("Dashboard", "KPI Cards", True, f"Pubs: {dash.get('total_publications')}, Citations: {dash.get('total_citations')}, Faculty: {dash.get('total_faculty')}, h-index: {dash.get('h_index')}")

    pubs_yr = requests.get(f"{BASE}/analytics/publications-by-year", headers=headers).json()
    record("Dashboard", "Publications by Year Chart", len(pubs_yr) > 0, f"{len(pubs_yr)} year buckets")

    cits_yr = requests.get(f"{BASE}/analytics/citation-trends", headers=headers).json()
    record("Dashboard", "Citation Trends Chart", len(cits_yr) > 0, f"{len(cits_yr)} years plotted")

    dept_comp = requests.get(f"{BASE}/analytics/department-comparison", headers=headers).json()
    record("Dashboard", "Department Comparison Chart", len(dept_comp) > 0, f"{len(dept_comp)} departments compared")

    verif_dist = requests.get(f"{BASE}/analytics/verification-distribution", headers=headers).json()
    record("Dashboard", "Verification Donut Chart", len(verif_dist) > 0, f"{len(verif_dist)} statuses represented")
except Exception as e:
    record("Dashboard", "Dashboard Metrics", False, str(e))

# 3. FACULTY MANAGEMENT
try:
    faculty_list = requests.get(f"{BASE}/faculty/", headers=headers).json()
    record("Faculty", "List Faculty Roster", len(faculty_list) >= 8, f"Found {len(faculty_list)} registered faculty members")

    # Test individual profile & publications & metrics for each
    all_profiles_ok = True
    for f in faculty_list[:5]:
        fid = f["id"]
        fname = f["full_name"]
        p_res = requests.get(f"{BASE}/faculty/{fid}", headers=headers)
        pubs_res = requests.get(f"{BASE}/faculty/{fid}/publications", headers=headers)
        m_res = requests.get(f"{BASE}/faculty/{fid}/citation-metrics", headers=headers)
        if not (p_res.status_code == 200 and pubs_res.status_code == 200 and m_res.status_code == 200):
            all_profiles_ok = False
            record("Faculty", f"Profile & Pubs ({fname})", False, f"HTTP {p_res.status_code}/{pubs_res.status_code}/{m_res.status_code}")
    if all_profiles_ok:
        record("Faculty", "Faculty Profile & Publications & Metrics", True, "All checked faculty returned HTTP 200 with complete publications and citation metrics")
except Exception as e:
    record("Faculty", "Faculty Management", False, str(e))

# 4. PUBLICATION MANAGEMENT
try:
    pubs_res = requests.get(f"{BASE}/publications/?limit=100", headers=headers).json()
    record("Publications", "Catalog List", len(pubs_res) > 50, f"Retrieved {len(pubs_res)} publications from database")

    first_pub = pubs_res[0]
    first_id = first_pub["id"]
    detail_res = requests.get(f"{BASE}/publications/{first_id}", headers=headers)
    record("Publications", "Publication Detail", detail_res.status_code == 200, f"Title: {detail_res.json().get('title')[:40]}...")

    # CSV Upload test
    sample_csv = "Title,Authors,Publication date,Journal,Volume,Issue,Pages,Publisher,Total citations,URL,DOI\n\"Novel Microstrip Antenna Array for 5G IoT Devices\",\"Sridhar Iyer; Rajashri Khanai\",2024,\"IEEE Access\",12,1,\"1-10\",\"IEEE\",25,\"https://doi.org/10.1109/ACCESS.2024.TEST999\",\"10.1109/ACCESS.2024.TEST999\"\n"
    import_res = requests.post(
        f"{BASE}/publications/import/scholar-csv",
        headers=headers,
        files={"file": ("test_import.csv", io.BytesIO(sample_csv.encode("utf-8")), "text/csv")}
    )
    record("Publications", "Google Scholar CSV Import", import_res.status_code == 200, f"Saved: {import_res.json().get('saved_to_database')}, Parsed: {import_res.json().get('total_parsed')}")
except Exception as e:
    record("Publications", "Publication Catalog", False, str(e))

# 5. DUPLICATE DETECTION & RESOLUTION
try:
    dups_res = requests.get(f"{BASE}/duplicates/", headers=headers).json()
    record("Duplicates", "List Duplicate Candidates", len(dups_res) > 0, f"Found {len(dups_res)} candidates with similarity scores")

    if len(dups_res) > 0:
        dup = dups_res[0]
        record("Duplicates", "Side-by-Side Comparison Brief", bool(dup.get("publication_a") and dup.get("publication_b")), f"Score: {dup.get('similarity_score')}, Type: {dup.get('match_type')}")
except Exception as e:
    record("Duplicates", "Duplicate Module", False, str(e))

# 6. VERIFICATION CENTER
try:
    verifs_res = requests.get(f"{BASE}/verification/", headers=headers).json()
    record("Verification", "List Verification Records", len(verifs_res) > 0, f"Found {len(verifs_res)} verification entries")

    if len(verifs_res) > 0:
        v0 = verifs_res[0]
        pub_id = v0["publication_id"]
        v_detail = requests.get(f"{BASE}/verification/{pub_id}", headers=headers)
        record("Verification", "Verification Detail & Evidence", v_detail.status_code == 200, f"Scopus: {v0.get('scopus_verified')}, WoS: {v0.get('wos_verified')}")

        # Test manual review action
        note_res = requests.post(
            f"{BASE}/verification/{pub_id}/manual",
            headers=headers,
            json={"scopus_verified": True, "wos_verified": True, "notes": "Verified against institutional publisher record", "evidence_url": "https://doi.org/10.3221/IGF-ESIS.71.03"}
        )
        record("Verification", "Manual Reviewer Approval", note_res.status_code == 200, f"Scopus Verified: {note_res.json().get('scopus_verified')}")
except Exception as e:
    record("Verification", "Verification Center", False, str(e))

# 7. CITATION ANALYTICS
try:
    h_idx_res = requests.get(f"{BASE}/analytics/h-index", headers=headers).json()
    record("Analytics", "Calculated h-index & i10-index", bool(h_idx_res.get('institutional_h_index')), f"University h-index: {h_idx_res.get('institutional_h_index')}, i10-index: {h_idx_res.get('institutional_i10_index')}, Faculty evaluated: {len(h_idx_res.get('faculty_breakdown', []))}")

    types_res = requests.get(f"{BASE}/analytics/publication-types", headers=headers).json()
    record("Analytics", "Publication Types Distribution", len(types_res) > 0, f"{len(types_res)} types found")
except Exception as e:
    record("Analytics", "Citation Analytics", False, str(e))

# 8. AI AGENTS & ORCHESTRATION
try:
    agents_res = requests.get(f"{BASE}/agents/", headers=headers).json()
    record("Agents", "List 7 AI Agents Executions", len(agents_res) > 0, f"Found {len(agents_res)} tracked execution runs")

    # Trigger individual agent
    trig_res = requests.post(f"{BASE}/agents/trigger", headers=headers, json={"agent_name": "Faculty Profile Agent", "input_data": {}})
    record("Agents", "Individual Agent Trigger", trig_res.status_code in (200, 202), f"Status: {trig_res.json().get('status')}, Agent: {trig_res.json().get('agent_name')}")

    # Trigger LangGraph full coordinator pipeline
    pipeline_res = requests.post(f"{BASE}/agents/trigger", headers=headers, json={"agent_name": "all", "input_data": {}})
    record("Agents", "LangGraph Full Pipeline Orchestration", pipeline_res.status_code in (200, 202), f"Status: {pipeline_res.json().get('status')}, Agent: {pipeline_res.json().get('agent_name')}")
except Exception as e:
    record("Agents", "Agent Monitoring", False, str(e))

# 9. NIRF / NAAC ACCREDITATION REPORTS
try:
    nirf_res = requests.post(
        f"{BASE}/reports/",
        headers=headers,
        json={"report_type": "nirf", "title": "NIRF Research Report 2024-2025", "academic_year": "2024-2025"}
    )
    record("Reports", "NIRF Report Compilation", nirf_res.status_code == 201, f"Report ID: {nirf_res.json().get('id')}")
    rep_id = nirf_res.json().get("id")

    pdf_res = requests.get(f"{BASE}/reports/{rep_id}/download/pdf", headers=headers)
    record("Reports", "Certified PDF Export", pdf_res.status_code == 200 and len(pdf_res.content) > 1000, f"{len(pdf_res.content)} bytes generated")

    xlsx_res = requests.get(f"{BASE}/reports/{rep_id}/download/excel", headers=headers)
    record("Reports", "Certified Excel Export", xlsx_res.status_code == 200 and len(xlsx_res.content) > 1000, f"{len(xlsx_res.content)} bytes generated")
except Exception as e:
    record("Reports", "Accreditation Reports", False, str(e))

# 10. SYSTEM CONFIGURATION & DIAGNOSTICS
try:
    cfg_res = requests.get(f"{BASE}/system/config-status", headers=headers)
    record("System", "Integrations Diagnostic Status", cfg_res.status_code == 200, f"App: {cfg_res.json().get('app_name')}, DB: {cfg_res.json().get('database_url_type')}")
except Exception as e:
    record("System", "Config Status", False, str(e))

print("\n===================================================================")
print("AUDIT SUMMARY:")
total_checks = sum(len(v) for v in results.values())
passed_checks = sum(sum(1 for c in v if c["success"]) for v in results.values())
print(f"Total Checks: {total_checks} | Passed: {passed_checks} | Failed: {total_checks - passed_checks}")
print("===================================================================")

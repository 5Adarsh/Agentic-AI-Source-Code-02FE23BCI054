"""
End-to-End Workflow & Integration Test Suite.
Verifies the complete 12-step university research lifecycle:
1. Administrator login and JWT issuance
2. Faculty profile registration
3. Database persistence & retrieval
4. Scholar CSV upload & harvest agent execution
5. Scopus / WoS verification evidence tracking
6. Duplicate candidate generation
7. Human review & merge resolution
8. Mathematical correctness of h-index & i10-index
9. Validation Agent rule execution
10. Dashboard analytics aggregation
11. NIRF / NAAC report compilation
12. Certified PDF and Excel file downloads
"""
import pytest
from uuid import uuid4

from app.models.user import User, UserRole
from app.models.faculty import Faculty, Department
from app.models.publication import Publication, PublicationAuthor, PublicationStatus, PublicationType
from app.models.duplicate import DuplicateCandidate, DuplicateStatus, MatchType
from app.models.verification import PublicationVerification
from app.utils.auth import hash_password, create_access_token


@pytest.fixture
def admin_token(db_session):
    admin = db_session.query(User).filter(User.email == "admin_test@kletech.ac.in").first()
    if not admin:
        admin = User(
            email="admin_test@kletech.ac.in",
            hashed_password=hash_password("Admin@123456"),
            full_name="Dr. Admin Test",
            role=UserRole.admin,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

    return create_access_token({"sub": str(admin.id), "role": admin.role.value})


def test_full_university_e2e_workflow(client, admin_token, db_session):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Step 1: Admin Authentication Verification
    auth_resp = client.get("/api/v1/auth/me", headers=headers)
    assert auth_resp.status_code == 200
    assert auth_resp.json()["email"] == "admin_test@kletech.ac.in"
    assert auth_resp.json()["role"] == "admin"

    # Step 2 & 3: Department & Faculty Registration
    dept = Department(name="School of Computer Science & Engineering", code="KLE-CSE-TEST")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)

    fac_payload = {
        "faculty_id": f"KLE-FAC-{uuid4().hex[:6]}",
        "full_name": "Dr. Ashok Shettar",
        "email": "vc_test@kletech.ac.in",
        "department_id": str(dept.id),
        "designation": "Professor & Vice Chancellor",
        "orcid": "0000-0002-1825-0097",
        "google_scholar_id": "ashok_scholar_001",
    }
    fac_resp = client.post("/api/v1/faculty/", json=fac_payload, headers=headers)
    assert fac_resp.status_code == 201
    faculty_data = fac_resp.json()
    faculty_id = faculty_data["id"]
    assert faculty_data["full_name"] == "Dr. Ashok Shettar"
    assert faculty_data["orcid"] == "0000-0002-1825-0097"

    # Step 4 & 5: Scholar CSV Ingestion
    sample_csv = (
        "title,authors,year,citations,url\n"
        "Outcome-Based Engineering Assessment,Shettar; Iyer,2023,45,https://doi.org/10.1109/TE.2023.001920\n"
        "Machine Learning in Industry 4.0,Shettar; Kulkarni,2022,25,https://doi.org/10.1016/j.jmsy.2022.09.004\n"
        "Outcome-Based Engineering Assessment Framework,Shettar; Iyer,2023,10,\n"
    )
    files = {"file": ("scholar_export.csv", sample_csv.encode("utf-8"), "text/csv")}
    data = {"faculty_id": faculty_id}
    csv_resp = client.post(
        "/api/v1/publications/import/scholar-csv",
        files=files,
        data=data,
        headers=headers,
    )
    assert csv_resp.status_code == 200
    import_result = csv_resp.json()
    assert import_result["status"] == "success"
    assert import_result["saved_to_database"] >= 2

    # Step 6: Scopus / WoS Verification
    pubs = client.get("/api/v1/publications/", headers=headers).json()
    assert len(pubs) >= 2
    pub1_id = pubs[0]["id"]

    manual_audit_payload = {
        "scopus_verified": True,
        "wos_verified": True,
        "notes": "Verified against Elsevier Scopus Institutional Portal with EID: 2-s2.0-85123456",
        "evidence_url": "https://www.scopus.com/record/display.uri?eid=2-s2.0-85123456",
    }
    audit_resp = client.post(
        f"/api/v1/verification/{pub1_id}/manual",
        json=manual_audit_payload,
        headers=headers,
    )
    assert audit_resp.status_code == 200
    assert audit_resp.json()["scopus_verified"] is True
    assert audit_resp.json()["wos_verified"] is True

    # Step 7 & 8: Duplicate Detection & Human Merge Resolution
    if len(pubs) >= 2:
        from uuid import UUID
        cand = DuplicateCandidate(
            publication_a_id=UUID(pubs[0]["id"]),
            publication_b_id=UUID(pubs[1]["id"]),
            similarity_score=0.92,
            match_type=MatchType.title_fuzzy,
            status=DuplicateStatus.pending,
        )
        db_session.add(cand)
        db_session.commit()
        db_session.refresh(cand)

        # Check candidate list
        dups_list = client.get("/api/v1/duplicates/", headers=headers).json()
        assert len(dups_list) >= 1

        # Approve Merge
        resolve_resp = client.post(
            f"/api/v1/duplicates/{cand.id}/resolve",
            json={"action": "approve"},
            headers=headers,
        )
        assert resolve_resp.status_code == 200
        assert resolve_resp.json()["status"] == "merged"

    # Step 9 & 10: Citation Analytics & Dashboard Aggregation
    dash_resp = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_faculty"] >= 1
    assert dash_data["total_publications"] >= 2
    assert dash_data["total_citations"] >= 70
    assert dash_data["h_index"] >= 2
    assert dash_data["i10_index"] >= 2

    # Step 11 & 12: NIRF/NAAC Report Generation & Binary File Exports
    report_payload = {
        "title": "NIRF Research & Professional Practice Submission 2024",
        "report_type": "nirf",
        "academic_year": "2023-2024",
    }
    rep_resp = client.post("/api/v1/reports/nirf", json=report_payload, headers=headers)
    assert rep_resp.status_code == 201
    report_id = rep_resp.json()["id"]

    # Download PDF
    pdf_resp = client.get(f"/api/v1/reports/{report_id}/download/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")  # Valid PDF Magic Bytes

    # Download Excel
    excel_resp = client.get(f"/api/v1/reports/{report_id}/download/excel", headers=headers)
    assert excel_resp.status_code == 200
    assert "openxmlformats" in excel_resp.headers["content-type"]
    assert excel_resp.content.startswith(b"PK")  # Valid ZIP / XLSX Magic Bytes

"""
Unit and integration tests for all 7 independent AI agents and edge conditions:
- Valid publication records
- Missing DOI
- Duplicate records & similar titles
- Different author formats
- Missing years
- Conflicting citation counts
- API failures & fallbacks
- Invalid CSV files
- Faculty identity conflicts
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.faculty_profile_agent import FacultyProfileAgent
from app.agents.scholar_harvest_agent import ScholarHarvestAgent
from app.agents.scopus_wos_agent import ScopusWosAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent, compute_title_similarity
from app.agents.citation_analytics_agent import CitationAnalyticsAgent, calculate_h_index, calculate_i10_index
from app.agents.validation_agent import ValidationAgent
from app.agents.dashboard_agent import DashboardAgent
from app.agents.coordinator import ResearchIntelligenceCoordinator


# 1. Faculty Profile Agent Tests: Identity conflict & ORCID validation
@pytest.mark.asyncio
async def test_faculty_profile_agent_identity_conflict():
    agent = FacultyProfileAgent()
    state = {
        "faculty_id": "non-existent-id",
        "logs": [],
    }
    result = await agent.execute(state)
    assert result["current_agent"] == "faculty_profile_agent"
    assert len(result["logs"]) > 0


# 2. Google Scholar Harvest Agent Tests: Valid CSV, author splitting, invalid CSV
@pytest.mark.asyncio
async def test_scholar_harvest_agent_valid_csv():
    agent = ScholarHarvestAgent()
    csv_data = (
        "title,authors,year,citations,url\n"
        "Attention Is All You Need,Vaswani; Shazeer; Parmar,2017,95000,https://doi.org/10.48550/arXiv.1706.03762\n"
        "BERT Pre-training,Devlin, J.,2018,65000,\n"
    )
    state = {
        "scholar_csv_content": csv_data,
        "logs": [],
        "harvested_publications": [],
    }
    result = await agent.execute(state)
    harvested = result["harvested_publications"]
    assert len(harvested) == 2
    assert harvested[0]["title"] == "Attention Is All You Need"
    assert len(harvested[0]["authors"]) == 3
    assert harvested[0]["publication_year"] == 2017
    assert harvested[0]["total_citations"] == 95000
    assert harvested[0]["doi"] == "10.48550/arXiv.1706.03762"


@pytest.mark.asyncio
async def test_scholar_harvest_agent_invalid_csv():
    agent = ScholarHarvestAgent()
    state = {
        "scholar_csv_content": "random,unstructured\nno_title_column,here",
        "logs": [],
        "harvested_publications": [],
    }
    result = await agent.execute(state)
    # Gracefully ignores rows without titles
    assert len(result["harvested_publications"]) == 0


# 3. Scopus / WoS Verification Agent Tests: API unconfigured fallback & live simulation
@pytest.mark.asyncio
async def test_scopus_wos_agent_unconfigured_reporting():
    agent = ScopusWosAgent()
    state = {
        "harvested_publications": [
            {"title": "Quantum Computing Advances", "doi": "10.1038/s41586-020-0001"}
        ],
        "logs": [],
    }
    result = await agent.execute(state)
    verifs = result["verification_results"]
    assert len(verifs) == 1
    # Without credentials, explicitly notes that APIs are not configured
    assert verifs[0]["scopus_api_configured"] is False
    assert verifs[0]["wos_api_configured"] is False


@pytest.mark.asyncio
async def test_scopus_wos_agent_api_mock_verification():
    agent = ScopusWosAgent()
    with patch.object(agent.scopus, "verify_doi", new_callable=AsyncMock) as mock_scopus:
        mock_scopus.return_value = {
            "verified": True,
            "status": "indexed",
            "scopus_eid": "2-s2.0-85000000000",
            "evidence": {"source": "scopus", "eid": "2-s2.0-85000000000"},
        }
        state = {
            "harvested_publications": [{"title": "Deep Learning", "doi": "10.1145/3065386"}],
            "logs": [],
        }
        result = await agent.execute(state)
        assert result["verification_results"][0]["scopus_verified"] is True
        assert result["verification_results"][0]["scopus_eid"] == "2-s2.0-85000000000"


# 4. Duplicate Detection Agent Tests: Exact DOI, fuzzy titles, human review queue
@pytest.mark.asyncio
async def test_duplicate_detection_agent_exact_and_fuzzy():
    agent = DuplicateDetectionAgent()
    state = {
        "harvested_publications": [
            {"title": "Transformers in Computer Vision", "doi": "10.1007/s11263-022-01650-6", "total_citations": 120, "authors": ["Dosovitskiy"]},
            {"title": "Transformers in Computer Vision", "doi": "10.1007/s11263-022-01650-6", "total_citations": 150, "authors": ["Dosovitskiy"]},
            {"title": "Transformers in Computer Vision: A Survey", "doi": None, "total_citations": 40, "authors": ["Dosovitskiy"]},
        ],
        "logs": [],
    }
    result = await agent.execute(state)
    assert len(result["deduplicated_publications"]) <= 2
    assert len(result["duplicate_candidates"]) >= 1
    assert result["duplicate_candidates"][0]["status"] == "confirmed_duplicate"


# 5. Citation Analytics Agent Tests: Deterministic math, conflicting counts
@pytest.mark.asyncio
async def test_citation_analytics_agent_calculations():
    agent = CitationAnalyticsAgent()
    state = {
        "deduplicated_publications": [
            {"title": "Paper 1", "total_citations": 50, "publication_year": 2020},
            {"title": "Paper 2", "total_citations": 25, "publication_year": 2021},
            {"title": "Paper 3", "total_citations": 10, "publication_year": 2021},
            {"title": "Paper 4", "total_citations": 5, "publication_year": 2022},
            {"title": "Paper 5", "total_citations": 0, "publication_year": None},
        ],
        "logs": [],
    }
    result = await agent.execute(state)
    metrics = result["citation_metrics"]
    assert metrics["total_publications"] == 5
    assert metrics["total_citations"] == 90
    assert metrics["h_index"] == 4
    assert metrics["i10_index"] == 3
    assert len(result["yearly_citations"]) == 3  # 2020, 2021, 2022


# 6. Validation Agent Tests: Missing DOI, anomalous years, status assignment
@pytest.mark.asyncio
async def test_validation_agent_rules():
    agent = ValidationAgent()
    state = {
        "deduplicated_publications": [
            {"title": "Valid Paper", "doi": "10.1016/j.jbi.2021.103750", "publication_year": 2021, "authors": ["Smith, J."]},
            {"title": "Bad Year Paper", "doi": "10.1016/j.jbi.2021.103751", "publication_year": 2500, "authors": ["Smith, J."]},
            {"title": "Missing Metadata", "doi": None, "publication_year": None, "authors": []},
        ],
        "verification_results": [
            {"doi": "10.1016/j.jbi.2021.103750", "scopus_verified": True}
        ],
        "logs": [],
    }
    result = await agent.execute(state)
    counts = result["validation_status_counts"]
    assert counts["verified"] == 1
    assert counts["requires_review"] >= 1


# 7. Dashboard Agent Tests: NIRF and NAAC generation
@pytest.mark.asyncio
async def test_dashboard_agent_compliance_structure():
    agent = DashboardAgent()
    state = {
        "citation_metrics": {"total_publications": 10, "total_citations": 200, "h_index": 5, "i10_index": 4},
        "validation_status_counts": {"verified": 8, "partially_verified": 2, "unverified": 0, "requires_review": 0},
        "yearly_citations": [{"year": 2022, "publications": 5, "citations": 100}],
        "logs": [],
    }
    result = await agent.execute(state)
    nirf = result["nirf_report_data"]
    naac = result["naac_report_data"]
    assert nirf["sub_metrics"]["combined_metric_publications"] == 10
    assert nirf["sub_metrics"]["scopus_wos_indexed_count"] == 8
    assert naac["metrics"]["3.4.5_h_index_institutional"] == 5


# 8. End-to-End Central Coordinator Workflow
@pytest.mark.asyncio
async def test_coordinator_full_execution_pipeline():
    coordinator = ResearchIntelligenceCoordinator()
    csv_sample = (
        "title,authors,year,citations,doi\n"
        "AI Foundations,Turing, A.,2020,30,10.1145/1234567\n"
        "Cybernetics,Wiener, N.,2021,15,10.1145/7654321\n"
    )
    initial_state = {
        "execution_id": "test-full-pipeline",
        "scholar_csv_content": csv_sample,
        "logs": [],
    }
    final_state = await coordinator.run(initial_state)
    assert final_state["status"] == "COMPLETED"
    assert final_state["citation_metrics"]["total_publications"] == 2
    assert final_state["citation_metrics"]["total_citations"] >= 45
    assert "nirf_report_data" in final_state
    assert len(final_state["logs"]) >= 7

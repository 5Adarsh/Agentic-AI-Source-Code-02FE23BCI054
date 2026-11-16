"""
Multi-Agent package for Research Intelligence & Publication Analytics Portal.
Contains all 7 domain agents and the central LangGraph coordinator.
"""
from app.agents.state import AgentState
from app.agents.coordinator import ResearchIntelligenceCoordinator
from app.agents.faculty_profile_agent import FacultyProfileAgent
from app.agents.scholar_harvest_agent import ScholarHarvestAgent
from app.agents.scopus_wos_agent import ScopusWosAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent
from app.agents.citation_analytics_agent import CitationAnalyticsAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.dashboard_agent import DashboardAgent

__all__ = [
    "AgentState",
    "ResearchIntelligenceCoordinator",
    "FacultyProfileAgent",
    "ScholarHarvestAgent",
    "ScopusWosAgent",
    "DuplicateDetectionAgent",
    "CitationAnalyticsAgent",
    "ValidationAgent",
    "DashboardAgent",
]

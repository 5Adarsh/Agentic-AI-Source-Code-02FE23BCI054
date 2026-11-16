"""
Central Coordinator: LangGraph Multi-Agent Orchestration
Module: app.agents.coordinator

Implements the non-negotiable workflow:
START
↓
Faculty Profile Agent
↓
Google Scholar Harvest Agent
↓
Scopus / WoS Verification Agent
↓
Duplicate Detection Agent
↓
Citation Analytics Agent
↓
Validation Agent
↓
Human Review if necessary
↓
Dashboard Agent
↓
END
"""
from typing import Any, Dict, Optional
from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.faculty_profile_agent import FacultyProfileAgent
from app.agents.scholar_harvest_agent import ScholarHarvestAgent
from app.agents.scopus_wos_agent import ScopusWosAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent
from app.agents.citation_analytics_agent import CitationAnalyticsAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.dashboard_agent import DashboardAgent
from app.utils.logger import get_logger

logger = get_logger("agents.coordinator")


class ResearchIntelligenceCoordinator:
    """
    Central LangGraph coordinator orchestrating all seven research intelligence agents.
    Provides conditional routing, human review gating, execution tracking, and resumable state.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings

        # Instantiate all seven domain agents
        self.faculty_profile_agent = FacultyProfileAgent(db_session, llm_client, settings)
        self.scholar_harvest_agent = ScholarHarvestAgent(db_session, llm_client, settings)
        self.scopus_wos_agent = ScopusWosAgent(db_session, llm_client, settings)
        self.duplicate_detection_agent = DuplicateDetectionAgent(db_session, llm_client, settings)
        self.citation_analytics_agent = CitationAnalyticsAgent(db_session, llm_client, settings)
        self.validation_agent = ValidationAgent(db_session, llm_client, settings)
        self.dashboard_agent = DashboardAgent(db_session, llm_client, settings)

        # Build workflow state graph
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        # 1. Register all 7 agent nodes + human review checkpoint node
        builder.add_node("faculty_profile_node", self.faculty_profile_agent.execute)
        builder.add_node("scholar_harvest_node", self.scholar_harvest_agent.execute)
        builder.add_node("scopus_wos_node", self.scopus_wos_agent.execute)
        builder.add_node("duplicate_detection_node", self.duplicate_detection_agent.execute)
        builder.add_node("citation_analytics_node", self.citation_analytics_agent.execute)
        builder.add_node("validation_node", self.validation_agent.execute)
        
        async def human_review_node(state: AgentState) -> AgentState:
            logger.info("[Coordinator] Human Review checkpoint: %d items in review queue.", len(state.get("review_queue", [])))
            updated = state.copy()
            updated["current_agent"] = "human_review"
            return updated

        builder.add_node("human_review_node", human_review_node)
        builder.add_node("dashboard_node", self.dashboard_agent.execute)

        # 2. Set Entry Point
        builder.set_entry_point("faculty_profile_node")

        # 3. Sequential Transitions
        builder.add_edge("faculty_profile_node", "scholar_harvest_node")
        builder.add_edge("scholar_harvest_node", "scopus_wos_node")
        builder.add_edge("scopus_wos_node", "duplicate_detection_node")
        builder.add_edge("duplicate_detection_node", "citation_analytics_node")
        builder.add_edge("citation_analytics_node", "validation_node")

        # 4. Conditional Edge after Validation: Human Review if flagged items require review
        def route_after_validation(state: AgentState) -> str:
            needs_review = (
                state.get("human_review_required", False)
                or (state.get("validation_status_counts", {}).get("requires_review", 0) > 0)
            )
            if needs_review:
                logger.info("[Coordinator] Discrepancies detected. Routing through Human Review node.")
                return "human_review_node"
            return "dashboard_node"

        builder.add_conditional_edges(
            "validation_node",
            route_after_validation,
            {
                "human_review_node": "human_review_node",
                "dashboard_node": "dashboard_node",
            }
        )

        builder.add_edge("human_review_node", "dashboard_node")
        builder.add_edge("dashboard_node", END)

        return builder.compile()

    async def run(self, initial_state: AgentState) -> AgentState:
        """Execute the complete 7-agent workflow."""
        logger.info("[Coordinator] Starting 7-agent workflow execution.")
        result = await self.graph.ainvoke(initial_state)
        logger.info("[Coordinator] Workflow completed. Status: %s", result.get("status"))
        return result

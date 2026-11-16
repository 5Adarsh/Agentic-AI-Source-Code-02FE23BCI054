"""
Elsevier Scopus Official Abstract Retrieval API Connector.
Uses official Scopus API credentials (API Key and optional Institutional Token).
Reports Not Configured when credentials are missing.
"""
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("integrations.scopus")


class ScopusClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, inst_token: Optional[str] = None):
        self.api_url = (api_url or settings.SCOPUS_API_URL or "https://api.elsevier.com/content").rstrip("/")
        self.api_key = api_key or settings.SCOPUS_API_KEY
        self.inst_token = inst_token or settings.SCOPUS_INST_TOKEN

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self.api_key or "",
        }
        if self.inst_token:
            headers["X-ELS-Insttoken"] = self.inst_token
        return headers

    async def verify_doi(self, doi: str) -> Dict[str, Any]:
        """
        Verify indexing in Scopus via official Abstract Retrieval API.
        Returns verification payload or status report.
        """
        if not self.is_configured:
            return {
                "verified": False,
                "status": "not_configured",
                "message": "Scopus API credentials not configured in environment.",
                "evidence": None,
            }

        clean_doi = doi.strip()
        url = f"{self.api_url}/abstract/doi/{urllib.parse.quote(clean_doi, safe='')}"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    data = response.json()
                    abstract_resp = data.get("abstracts-retrieval-response", {})
                    coredata = abstract_resp.get("coredata", {})
                    scopus_eid = coredata.get("eid")
                    citations = int(coredata.get("citedby-count", 0)) if coredata.get("citedby-count") else 0

                    return {
                        "verified": True,
                        "status": "indexed",
                        "scopus_eid": scopus_eid,
                        "citations": citations,
                        "evidence": {
                            "source": "scopus",
                            "eid": scopus_eid,
                            "cited_by_count": citations,
                            "publication_name": coredata.get("prism:publicationName"),
                            "cover_date": coredata.get("prism:coverDate"),
                            "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        },
                    }
                elif response.status_code == 404:
                    return {
                        "verified": False,
                        "status": "not_indexed",
                        "message": "Article not indexed in Scopus.",
                        "evidence": None,
                    }
                else:
                    return {
                        "verified": False,
                        "status": "api_error",
                        "message": f"Scopus API returned HTTP {response.status_code}",
                        "evidence": None,
                    }
            except Exception as e:
                logger.error("Scopus verification error: %s", str(e))
                return {
                    "verified": False,
                    "status": "network_error",
                    "message": str(e),
                    "evidence": None,
                }

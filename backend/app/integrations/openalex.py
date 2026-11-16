"""
OpenAlex REST API Connector.
Free and open scholarly index connector with mailto identification.
"""
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("integrations.openalex")


class OpenAlexClient:
    def __init__(self, api_url: Optional[str] = None, email: Optional[str] = None):
        self.api_url = (api_url or settings.OPENALEX_API_URL or "https://api.openalex.org").rstrip("/")
        self.email = email or settings.OPENALEX_EMAIL or "research-portal@university.edu"

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": f"ResearchIntelligencePortal/1.0 (mailto:{self.email})",
            "Accept": "application/json",
        }

    async def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        clean_doi = doi.strip()
        url = f"{self.api_url}/works/https://doi.org/{clean_doi}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    return self._normalize_work(response.json())
                return None
            except Exception as e:
                logger.error("OpenAlex error for DOI %s: %s", doi, str(e))
                return None

    async def get_works_by_author_orcid(self, orcid: str, limit: int = 25) -> List[Dict[str, Any]]:
        clean_orcid = orcid.strip().replace("https://orcid.org/", "")
        url = f"{self.api_url}/works?filter=author.orcid:https://orcid.org/{clean_orcid}&per-page={limit}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    return [self._normalize_work(w) for w in results]
                return []
            except Exception as e:
                logger.error("OpenAlex ORCID works error: %s", str(e))
                return []

    def _normalize_work(self, item: Dict[str, Any]) -> Dict[str, Any]:
        title = item.get("title") or item.get("display_name") or ""
        doi_raw = item.get("doi") or ""
        doi = doi_raw.replace("https://doi.org/", "") if doi_raw else None
        
        authors = []
        for authorship in item.get("authorships", []):
            author_obj = authorship.get("author", {})
            name = author_obj.get("display_name")
            if name:
                authors.append(name)
        
        year = item.get("publication_year")
        citations = item.get("cited_by_count", 0)

        return {
            "title": title,
            "doi": doi,
            "authors": authors,
            "publication_year": year,
            "total_citations": citations,
            "source": "openalex",
            "source_id": item.get("id"),
            "source_url": item.get("id"),
            "raw_data": item,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

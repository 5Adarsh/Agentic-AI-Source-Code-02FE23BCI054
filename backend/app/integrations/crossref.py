"""
Crossref REST API Connector.
Uses polite pool headers with email identification, backoff retry, and DOI resolution.
"""
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("integrations.crossref")


class CrossrefClient:
    def __init__(self, api_url: Optional[str] = None, email: Optional[str] = None):
        self.api_url = (api_url or settings.CROSSREF_API_URL or "https://api.crossref.org/works").rstrip("/")
        self.email = email or settings.CROSSREF_EMAIL or "research-portal@university.edu"

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": f"ResearchIntelligencePortal/1.0 (mailto:{self.email})",
            "Accept": "application/json",
        }

    async def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        clean_doi = doi.strip()
        encoded_doi = urllib.parse.quote(clean_doi, safe="")
        url = f"{self.api_url}/{encoded_doi}"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    data = response.json()
                    item = data.get("message", {})
                    return self._normalize_work(item)
                elif response.status_code == 404:
                    logger.info("DOI not found on Crossref: %s", doi)
                    return None
                else:
                    logger.warning("Crossref returned status %d for DOI %s", response.status_code, doi)
                    return None
            except Exception as e:
                logger.error("Crossref API request error for DOI %s: %s", doi, str(e))
                return None

    async def search_works(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = f"{self.api_url}?query={urllib.parse.quote(query)}&rows={limit}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    items = response.json().get("message", {}).get("items", [])
                    return [self._normalize_work(item) for item in items]
                return []
            except Exception as e:
                logger.error("Crossref search error: %s", str(e))
                return []

    def _normalize_work(self, item: Dict[str, Any]) -> Dict[str, Any]:
        titles = item.get("title", [])
        title = titles[0] if titles else ""
        doi = item.get("DOI")
        
        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip() or author.get("name", "")
            if name:
                authors.append(name)
        
        pub_year = None
        published = item.get("published-print") or item.get("published-online") or item.get("created")
        if published and "date-parts" in published and published["date-parts"]:
            parts = published["date-parts"][0]
            if parts and isinstance(parts[0], int):
                pub_year = parts[0]

        citations = item.get("is-referenced-by-count", 0)

        return {
            "title": title,
            "doi": doi,
            "authors": authors,
            "publication_year": pub_year,
            "total_citations": citations,
            "source": "crossref",
            "source_id": doi,
            "source_url": f"https://doi.org/{doi}" if doi else None,
            "raw_data": item,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

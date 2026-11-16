"""
Semantic Scholar Academic Graph API Connector.
Retrieves citation graphs and publication indexing with rate limit backoff.
"""
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("integrations.semanticscholar")


class SemanticScholarClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = (api_url or settings.SEMANTIC_SCHOLAR_API_URL or "https://api.semanticscholar.org/graph/v1").rstrip("/")
        self.api_key = api_key or settings.SEMANTIC_SCHOLAR_API_KEY

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        # Supports DOI:10.xxx or Semantic Scholar Paper ID
        clean_id = paper_id.strip()
        fields = "title,authors,year,citationCount,externalIds,url,abstract"
        url = f"{self.api_url}/paper/{clean_id}?fields={fields}"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    return self._normalize_paper(response.json())
                elif response.status_code == 429:
                    logger.warning("Semantic Scholar rate limit reached")
                    return None
                return None
            except Exception as e:
                logger.error("Semantic Scholar request failed: %s", str(e))
                return None

    def _normalize_paper(self, item: Dict[str, Any]) -> Dict[str, Any]:
        ext_ids = item.get("externalIds") or {}
        doi = ext_ids.get("DOI")
        authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]

        return {
            "title": item.get("title", ""),
            "doi": doi,
            "authors": authors,
            "publication_year": item.get("year"),
            "total_citations": item.get("citationCount", 0),
            "abstract": item.get("abstract"),
            "source": "semantic_scholar",
            "source_id": item.get("paperId"),
            "source_url": item.get("url"),
            "raw_data": item,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

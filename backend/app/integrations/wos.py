"""
Web of Science (Clarivate) Official API Connector.
Uses official WoS Starter or Expanded API keys.
Accurately reports Not Configured when credentials are missing.
"""
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("integrations.wos")


class WebOfScienceClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = (api_url or settings.WOS_API_URL or "https://wos-api.clarivate.com/api/wos").rstrip("/")
        self.api_key = api_key or settings.WOS_API_KEY

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "X-ApiKey": self.api_key or "",
        }

    async def verify_doi(self, doi: str) -> Dict[str, Any]:
        """
        Verify indexing in Web of Science.
        Returns authentic indexing status and UID or Not Configured.
        """
        if not self.is_configured:
            return {
                "verified": False,
                "status": "not_configured",
                "message": "Web of Science API credentials not configured in environment.",
                "evidence": None,
            }

        clean_doi = doi.strip()
        query = f'DO="{clean_doi}"'
        url = f"{self.api_url}?usrQuery={urllib.parse.quote(query)}&count=1&firstRecord=1"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, headers=self._headers())
                if response.status_code == 200:
                    data = response.json()
                    records_found = data.get("QueryResult", {}).get("RecordsFound", 0)
                    if records_found > 0:
                        records = data.get("Data", {}).get("Records", {}).get("records", {}).get("REC", [])
                        rec = records[0] if isinstance(records, list) and records else records
                        uid = rec.get("UID") if isinstance(rec, dict) else None

                        return {
                            "verified": True,
                            "status": "indexed",
                            "wos_uid": uid,
                            "evidence": {
                                "source": "wos",
                                "uid": uid,
                                "database": "WOS.CORE",
                                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                            },
                        }
                    else:
                        return {
                            "verified": False,
                            "status": "not_indexed",
                            "message": "Article not found in Web of Science Core Collection.",
                            "evidence": None,
                        }
                else:
                    return {
                        "verified": False,
                        "status": "api_error",
                        "message": f"WoS API returned HTTP {response.status_code}",
                        "evidence": None,
                    }
            except Exception as e:
                logger.error("Web of Science verification error: %s", str(e))
                return {
                    "verified": False,
                    "status": "network_error",
                    "message": str(e),
                    "evidence": None,
                }

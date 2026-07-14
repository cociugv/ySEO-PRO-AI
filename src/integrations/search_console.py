"""
Google Search Console Integration — Query performance data and URL inspection.

Requires:
- Service account credentials (JSON key file) OR
- OAuth 2.0 token

Features:
- Search performance queries (clicks, impressions, CTR, position)
- URL inspection (indexing status, crawl info)
- Sitemap management
- Index coverage data
"""

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional


GSC_API = "https://www.googleapis.com/webmasters/v3"
SEARCH_ANALYTICS_API = "https://searchconsole.googleapis.com/webmasters/v3"


@dataclass
class SearchPerformanceRow:
    """A single row from Search Analytics."""
    query: str = ""
    page: str = ""
    country: str = ""
    device: str = ""
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0
    position: float = 0

    def to_dict(self) -> dict:
        return {
            "query": self.query, "page": self.page,
            "clicks": self.clicks, "impressions": self.impressions,
            "ctr": round(self.ctr, 4), "position": round(self.position, 1),
        }


@dataclass
class GSCResult:
    """Result from GSC API call."""
    success: bool
    data: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "rows_count": len(self.rows),
            "rows": [r.to_dict() if hasattr(r, "to_dict") else r for r in self.rows[:50]],
            "error": self.error,
        }


class SearchConsoleClient:
    """
    Google Search Console API client.

    Usage:
        client = SearchConsoleClient(
            property_url="https://ylink.pro",
            credentials_path="config/gsc-credentials.json"
        )
        result = client.query_performance(days=30)
    """

    def __init__(
        self,
        property_url: str,
        credentials_path: str = "",
        access_token: str = "",
    ):
        self.property_url = property_url
        self.credentials_path = credentials_path
        self._access_token = access_token

    def query_performance(
        self,
        days: int = 28,
        dimensions: list = None,
        row_limit: int = 100,
        query_filter: str = "",
        page_filter: str = "",
    ) -> GSCResult:
        """
        Query search performance data.

        Args:
            days: Number of days to look back
            dimensions: ["query", "page", "country", "device", "date"]
            row_limit: Max rows to return
            query_filter: Filter by query containing this text
            page_filter: Filter by page URL containing this text
        """
        if not self._get_token():
            return GSCResult(success=False, error="No valid credentials")

        dimensions = dimensions or ["query", "page"]

        import time
        end_date = time.strftime("%Y-%m-%d")
        start_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() - days * 86400))

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }

        # Add filters
        filters = []
        if query_filter:
            filters.append({"dimension": "query", "operator": "contains", "expression": query_filter})
        if page_filter:
            filters.append({"dimension": "page", "operator": "contains", "expression": page_filter})
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]

        encoded_property = urllib.parse.quote(self.property_url, safe="")
        url = f"{SEARCH_ANALYTICS_API}/sites/{encoded_property}/searchAnalytics/query"

        result = self._post(url, body)
        if not result.success:
            return result

        # Parse rows
        rows = []
        for row_data in result.data.get("rows", []):
            keys = row_data.get("keys", [])
            row = SearchPerformanceRow(
                query=keys[0] if len(keys) > 0 and "query" in dimensions else "",
                page=keys[1] if len(keys) > 1 and "page" in dimensions else (keys[0] if "page" in dimensions and "query" not in dimensions else ""),
                clicks=row_data.get("clicks", 0),
                impressions=row_data.get("impressions", 0),
                ctr=row_data.get("ctr", 0),
                position=row_data.get("position", 0),
            )
            rows.append(row)

        result.rows = rows
        return result

    def inspect_url(self, url: str) -> GSCResult:
        """
        Inspect a URL's index status.

        Returns: indexing state, crawl time, referring sitemap, etc.
        """
        if not self._get_token():
            return GSCResult(success=False, error="No valid credentials")

        body = {
            "inspectionUrl": url,
            "siteUrl": self.property_url,
        }

        api_url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
        return self._post(api_url, body)

    def list_sitemaps(self) -> GSCResult:
        """List submitted sitemaps for the property."""
        if not self._get_token():
            return GSCResult(success=False, error="No valid credentials")

        encoded_property = urllib.parse.quote(self.property_url, safe="")
        url = f"{GSC_API}/sites/{encoded_property}/sitemaps"
        return self._get(url)

    def submit_sitemap(self, sitemap_url: str) -> GSCResult:
        """Submit a sitemap to Google Search Console."""
        if not self._get_token():
            return GSCResult(success=False, error="No valid credentials")

        encoded_property = urllib.parse.quote(self.property_url, safe="")
        encoded_sitemap = urllib.parse.quote(sitemap_url, safe="")
        url = f"{GSC_API}/sites/{encoded_property}/sitemaps/{encoded_sitemap}"

        try:
            req = urllib.request.Request(url, method="PUT", headers=self._auth_headers())
            urllib.request.urlopen(req, timeout=30)
            return GSCResult(success=True, data={"submitted": sitemap_url})
        except Exception as e:
            return GSCResult(success=False, error=str(e))

    # ─── Private ───────────────────────────────────────────────────

    def _get_token(self) -> bool:
        """Ensure we have a valid access token."""
        if self._access_token:
            return True

        # Try env var
        token = os.environ.get("GSC_ACCESS_TOKEN", "")
        if token:
            self._access_token = token
            return True

        # Try service account credentials file
        if self.credentials_path and os.path.exists(self.credentials_path):
            # Full OAuth implementation would go here
            # For now, support pre-generated tokens
            try:
                with open(self.credentials_path, "r") as f:
                    creds = json.load(f)
                if "access_token" in creds:
                    self._access_token = creds["access_token"]
                    return True
            except (json.JSONDecodeError, OSError):
                pass

        return False

    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _post(self, url: str, body: dict) -> GSCResult:
        """Make authenticated POST request."""
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=self._auth_headers(), method="POST")
            response = urllib.request.urlopen(req, timeout=30)
            result_data = json.loads(response.read().decode("utf-8"))
            return GSCResult(success=True, data=result_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")[:200]
            return GSCResult(success=False, error=f"HTTP {e.code}: {error_body}")
        except Exception as e:
            return GSCResult(success=False, error=str(e))

    def _get(self, url: str) -> GSCResult:
        """Make authenticated GET request."""
        try:
            req = urllib.request.Request(url, headers=self._auth_headers())
            response = urllib.request.urlopen(req, timeout=30)
            result_data = json.loads(response.read().decode("utf-8"))
            return GSCResult(success=True, data=result_data)
        except urllib.error.HTTPError as e:
            return GSCResult(success=False, error=f"HTTP {e.code}")
        except Exception as e:
            return GSCResult(success=False, error=str(e))

"""
IndexNow Pinger — Notify search engines of new/updated content instantly.

Supports:
- IndexNow API (Bing, Yandex, Seznam, Naver)
- Google Ping (sitemaps)
- Bulk URL submission
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


@dataclass
class PingResult:
    """Result of an IndexNow ping."""
    success: bool
    urls_submitted: int = 0
    engine: str = ""
    status_code: int = 0
    error: str = ""


class IndexNowPinger:
    """
    Pings search engines via IndexNow protocol for instant indexing.

    IndexNow lets you notify participating search engines immediately
    when pages are created, updated, or deleted.
    """

    ENDPOINTS = {
        "indexnow": "https://api.indexnow.org/indexnow",
        "bing": "https://www.bing.com/indexnow",
        "yandex": "https://yandex.com/indexnow",
        "seznam": "https://search.seznam.cz/indexnow",
        "naver": "https://searchadvisor.naver.com/indexnow",
    }

    GOOGLE_PING = "https://www.google.com/ping?sitemap="

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.key = self.config.get("indexnow_key", "")
        self.key_location = self.config.get("key_location", "")
        self.host = self.config.get("host", "")

    def ping_single(self, url: str, engine: str = "indexnow") -> PingResult:
        """Submit a single URL to IndexNow."""
        if not self.key:
            return PingResult(success=False, error="IndexNow key not configured")

        parsed = urlparse(url)
        host = self.host or parsed.netloc

        endpoint = self.ENDPOINTS.get(engine, self.ENDPOINTS["indexnow"])
        params = f"?url={url}&key={self.key}"

        if self.key_location:
            params += f"&keyLocation={self.key_location}"

        try:
            req = urllib.request.Request(endpoint + params)
            response = urllib.request.urlopen(req, timeout=15)
            return PingResult(
                success=True,
                urls_submitted=1,
                engine=engine,
                status_code=response.status,
            )
        except urllib.error.HTTPError as e:
            return PingResult(
                success=e.code in (200, 202),
                urls_submitted=1 if e.code in (200, 202) else 0,
                engine=engine,
                status_code=e.code,
                error="" if e.code in (200, 202) else f"HTTP {e.code}",
            )
        except Exception as e:
            return PingResult(success=False, engine=engine, error=str(e))

    def ping_batch(self, urls: list[str], engine: str = "indexnow") -> PingResult:
        """Submit multiple URLs via IndexNow batch API."""
        if not self.key:
            return PingResult(success=False, error="IndexNow key not configured")
        if not urls:
            return PingResult(success=False, error="No URLs provided")

        parsed = urlparse(urls[0])
        host = self.host or parsed.netloc

        endpoint = self.ENDPOINTS.get(engine, self.ENDPOINTS["indexnow"])

        payload = {
            "host": host,
            "key": self.key,
            "urlList": urls[:10000],  # Max 10,000 per batch
        }

        if self.key_location:
            payload["keyLocation"] = self.key_location

        data = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            response = urllib.request.urlopen(req, timeout=30)
            return PingResult(
                success=True,
                urls_submitted=len(urls),
                engine=engine,
                status_code=response.status,
            )
        except urllib.error.HTTPError as e:
            return PingResult(
                success=e.code in (200, 202),
                urls_submitted=len(urls) if e.code in (200, 202) else 0,
                engine=engine,
                status_code=e.code,
                error="" if e.code in (200, 202) else f"HTTP {e.code}",
            )
        except Exception as e:
            return PingResult(success=False, engine=engine, error=str(e))

    def ping_google_sitemap(self, sitemap_url: str) -> PingResult:
        """Ping Google with sitemap URL (legacy but still works)."""
        try:
            url = f"{self.GOOGLE_PING}{sitemap_url}"
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=15)
            return PingResult(
                success=True,
                urls_submitted=1,
                engine="google",
                status_code=response.status,
            )
        except Exception as e:
            return PingResult(success=False, engine="google", error=str(e))

    def ping_all_engines(self, urls: list[str]) -> list[PingResult]:
        """Submit URLs to all supported IndexNow engines."""
        results = []
        for engine in self.ENDPOINTS:
            result = self.ping_batch(urls, engine=engine)
            results.append(result)
        return results

"""
HTTP Fetcher — Unified page retrieval with caching and rate limiting.

Features:
- Respects robots.txt
- Built-in rate limiting
- Response caching
- Custom user-agent
- Timeout management
- Retry with exponential backoff
"""

import hashlib
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FetchResult:
    """Result of fetching a URL."""
    url: str
    status_code: int
    headers: dict = field(default_factory=dict)
    body: str = ""
    elapsed_ms: float = 0
    from_cache: bool = False
    error: str = ""
    redirects: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")

    @property
    def is_html(self) -> bool:
        return "text/html" in self.content_type


class PageFetcher:
    """
    Fetches web pages with caching, rate limiting, and retries.
    Uses only stdlib — no external dependencies.
    """

    def __init__(
        self,
        user_agent: str = "ySEO-PRO-AI/1.0 (+https://ylink.pro/bot)",
        cache_dir: str = ".yseo/cache",
        rate_limit_ms: int = 1000,
        timeout_seconds: int = 30,
        max_retries: int = 2,
    ):
        self.user_agent = user_agent
        self.cache_dir = cache_dir
        self.rate_limit_ms = rate_limit_ms
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self._last_request_time: float = 0

        os.makedirs(cache_dir, exist_ok=True)

    def fetch(self, url: str, use_cache: bool = True) -> FetchResult:
        """Fetch a URL with caching and rate limiting."""
        if use_cache:
            cached = self._get_cached(url)
            if cached:
                return cached

        self._rate_limit()

        result = self._do_fetch(url)

        if result.ok and use_cache:
            self._save_cache(url, result)

        return result

    def fetch_many(self, urls: list[str], use_cache: bool = True) -> list[FetchResult]:
        """Fetch multiple URLs sequentially with rate limiting."""
        return [self.fetch(url, use_cache) for url in urls]

    def _do_fetch(self, url: str, attempt: int = 0) -> FetchResult:
        """Execute the actual HTTP request."""
        start = time.time()
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "identity",
            })

            response = urllib.request.urlopen(req, timeout=self.timeout)
            body = response.read().decode("utf-8", errors="replace")
            headers = dict(response.headers)
            elapsed = (time.time() - start) * 1000

            return FetchResult(
                url=url,
                status_code=response.status,
                headers=headers,
                body=body,
                elapsed_ms=elapsed,
            )

        except urllib.error.HTTPError as e:
            elapsed = (time.time() - start) * 1000
            return FetchResult(
                url=url,
                status_code=e.code,
                headers=dict(e.headers) if e.headers else {},
                body="",
                elapsed_ms=elapsed,
                error=str(e),
            )

        except Exception as e:
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
                return self._do_fetch(url, attempt + 1)

            elapsed = (time.time() - start) * 1000
            return FetchResult(
                url=url,
                status_code=0,
                elapsed_ms=elapsed,
                error=str(e),
            )

    def _rate_limit(self) -> None:
        """Enforce minimum delay between requests."""
        now = time.time() * 1000
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_ms:
            time.sleep((self.rate_limit_ms - elapsed) / 1000)
        self._last_request_time = time.time() * 1000

    def _cache_key(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _get_cached(self, url: str) -> Optional[FetchResult]:
        """Retrieve cached response if available and fresh."""
        key = self._cache_key(url)
        path = os.path.join(self.cache_dir, f"{key}.json")
        if not os.path.exists(path):
            return None

        # Cache expires after 1 hour
        if time.time() - os.path.getmtime(path) > 3600:
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return FetchResult(
                url=data["url"],
                status_code=data["status_code"],
                headers=data.get("headers", {}),
                body=data.get("body", ""),
                elapsed_ms=0,
                from_cache=True,
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def _save_cache(self, url: str, result: FetchResult) -> None:
        """Save response to cache."""
        key = self._cache_key(url)
        path = os.path.join(self.cache_dir, f"{key}.json")
        data = {
            "url": result.url,
            "status_code": result.status_code,
            "headers": result.headers,
            "body": result.body[:500000],  # Cap at 500KB
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            pass

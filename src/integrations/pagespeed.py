"""
Google PageSpeed Insights Integration — Real API calls for Core Web Vitals.

Fetches Lighthouse performance data via Google's public API.
Free tier: 25,000 queries/day (no key required for basic usage).
With API key: higher quotas.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional


API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


@dataclass
class CoreWebVitals:
    """Core Web Vitals metrics."""
    lcp_ms: float = 0       # Largest Contentful Paint
    fid_ms: float = 0       # First Input Delay (legacy)
    inp_ms: float = 0       # Interaction to Next Paint
    cls: float = 0          # Cumulative Layout Shift
    fcp_ms: float = 0       # First Contentful Paint
    ttfb_ms: float = 0      # Time to First Byte
    si_ms: float = 0        # Speed Index
    tbt_ms: float = 0       # Total Blocking Time

    @property
    def lcp_rating(self) -> str:
        if self.lcp_ms <= 2500: return "good"
        if self.lcp_ms <= 4000: return "needs_improvement"
        return "poor"

    @property
    def inp_rating(self) -> str:
        if self.inp_ms <= 200: return "good"
        if self.inp_ms <= 500: return "needs_improvement"
        return "poor"

    @property
    def cls_rating(self) -> str:
        if self.cls <= 0.1: return "good"
        if self.cls <= 0.25: return "needs_improvement"
        return "poor"

    def to_dict(self) -> dict:
        return {
            "lcp_ms": self.lcp_ms, "lcp_rating": self.lcp_rating,
            "inp_ms": self.inp_ms, "inp_rating": self.inp_rating,
            "cls": self.cls, "cls_rating": self.cls_rating,
            "fcp_ms": self.fcp_ms, "ttfb_ms": self.ttfb_ms,
            "si_ms": self.si_ms, "tbt_ms": self.tbt_ms,
        }


@dataclass
class PageSpeedResult:
    """Complete PageSpeed Insights result."""
    url: str
    strategy: str = "mobile"
    performance_score: int = 0
    vitals: CoreWebVitals = field(default_factory=CoreWebVitals)
    opportunities: list = field(default_factory=list)
    diagnostics: list = field(default_factory=list)
    error: str = ""
    success: bool = False

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "strategy": self.strategy,
            "performance_score": self.performance_score,
            "vitals": self.vitals.to_dict(),
            "opportunities": self.opportunities[:10],
            "diagnostics": self.diagnostics[:10],
            "error": self.error,
            "success": self.success,
        }


class PageSpeedClient:
    """
    Client for Google PageSpeed Insights API.

    Usage:
        client = PageSpeedClient(api_key="optional")
        result = client.analyze("https://example.com", strategy="mobile")
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def analyze(self, url: str, strategy: str = "mobile") -> PageSpeedResult:
        """
        Run PageSpeed Insights on a URL.

        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"

        Returns:
            PageSpeedResult with scores, vitals, and opportunities
        """
        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
        }
        if self.api_key:
            params["key"] = self.api_key

        api_url = f"{API_URL}?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(api_url, headers={
                "Accept": "application/json",
                "User-Agent": "ySEO-PRO-AI/1.0",
            })
            response = urllib.request.urlopen(req, timeout=60)
            data = json.loads(response.read().decode("utf-8"))
            return self._parse_response(url, strategy, data)

        except urllib.error.HTTPError as e:
            return PageSpeedResult(
                url=url, strategy=strategy,
                error=f"API error: HTTP {e.code}", success=False,
            )
        except Exception as e:
            return PageSpeedResult(
                url=url, strategy=strategy,
                error=str(e), success=False,
            )

    def _parse_response(self, url: str, strategy: str, data: dict) -> PageSpeedResult:
        """Parse the PageSpeed API JSON response."""
        result = PageSpeedResult(url=url, strategy=strategy, success=True)

        # Lighthouse score
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        perf = categories.get("performance", {})
        result.performance_score = int((perf.get("score", 0) or 0) * 100)

        # Audits for metrics
        audits = lighthouse.get("audits", {})

        # Core Web Vitals from audits
        vitals = CoreWebVitals()

        lcp = audits.get("largest-contentful-paint", {})
        vitals.lcp_ms = lcp.get("numericValue", 0)

        fcp = audits.get("first-contentful-paint", {})
        vitals.fcp_ms = fcp.get("numericValue", 0)

        cls_audit = audits.get("cumulative-layout-shift", {})
        vitals.cls = cls_audit.get("numericValue", 0)

        tbt = audits.get("total-blocking-time", {})
        vitals.tbt_ms = tbt.get("numericValue", 0)

        si = audits.get("speed-index", {})
        vitals.si_ms = si.get("numericValue", 0)

        ttfb = audits.get("server-response-time", {})
        vitals.ttfb_ms = ttfb.get("numericValue", 0)

        # INP from CrUX data if available
        loading_exp = data.get("loadingExperience", {})
        metrics = loading_exp.get("metrics", {})
        inp_data = metrics.get("INTERACTION_TO_NEXT_PAINT", {})
        if inp_data:
            vitals.inp_ms = inp_data.get("percentile", 0)

        result.vitals = vitals

        # Opportunities (potential savings)
        opportunities = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity":
                savings = audit.get("details", {}).get("overallSavingsMs", 0)
                if savings > 0:
                    opportunities.append({
                        "id": key,
                        "title": audit.get("title", ""),
                        "savings_ms": savings,
                        "description": audit.get("description", "")[:200],
                    })
        result.opportunities = sorted(opportunities, key=lambda x: -x["savings_ms"])

        # Diagnostics
        diagnostics = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "table" and audit.get("score") is not None:
                if audit["score"] < 1:
                    diagnostics.append({
                        "id": key,
                        "title": audit.get("title", ""),
                        "score": audit["score"],
                    })
        result.diagnostics = sorted(diagnostics, key=lambda x: x.get("score", 1))

        return result

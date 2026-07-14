"""
Site Crawler — Disk-backed persistent crawl with resume, dedup, and politeness.

Features:
- SQLite-backed URL frontier (survives crashes)
- Content-hash deduplication
- Per-host crawl delay (respects robots.txt Crawl-delay)
- Resume from checkpoint after interruption
- Bounded memory (streams results)
- Configurable depth, max pages, URL filters
- Sitemap-first discovery
"""

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Generator
from urllib.parse import urlparse, urljoin

from .fetcher import PageFetcher, FetchResult
from .parser import parse_html, PageData


class CrawlStatus(Enum):
    PENDING = "pending"
    FETCHED = "fetched"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CrawledPage:
    """Result of crawling a single URL."""
    url: str
    status: CrawlStatus
    depth: int = 0
    http_status: int = 0
    content_hash: str = ""
    title: str = ""
    word_count: int = 0
    internal_links: list = field(default_factory=list)
    elapsed_ms: float = 0
    error: str = ""
    is_duplicate: bool = False

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "status": self.status.value,
            "depth": self.depth,
            "http_status": self.http_status,
            "content_hash": self.content_hash,
            "title": self.title,
            "word_count": self.word_count,
            "internal_links_count": len(self.internal_links),
            "elapsed_ms": self.elapsed_ms,
            "error": self.error,
            "is_duplicate": self.is_duplicate,
        }


class SiteCrawler:
    """
    Persistent site crawler with disk-backed state.

    Usage:
        crawler = SiteCrawler("https://example.com", max_pages=100)
        for page in crawler.crawl():
            process(page)
        crawler.close()

    Resume:
        crawler = SiteCrawler("https://example.com")  # Reopens existing DB
        for page in crawler.crawl():  # Continues from where it left off
            process(page)
    """

    def __init__(
        self,
        start_url: str,
        max_pages: int = 200,
        max_depth: int = 5,
        crawl_delay_ms: int = 1000,
        db_path: str = "",
        allowed_domains: list = None,
        exclude_patterns: list = None,
    ):
        self.start_url = start_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.crawl_delay_ms = crawl_delay_ms
        self.exclude_patterns = [re.compile(p) for p in (exclude_patterns or [])]

        parsed = urlparse(start_url)
        self.start_domain = parsed.netloc
        self.allowed_domains = set(allowed_domains or [self.start_domain])

        # DB path defaults to .yseo/crawls/{domain}.db
        if not db_path:
            db_dir = os.path.join(".yseo", "crawls")
            os.makedirs(db_dir, exist_ok=True)
            safe_domain = self.start_domain.replace(":", "_").replace(".", "_")
            db_path = os.path.join(db_dir, f"{safe_domain}.db")

        self.db_path = db_path
        self._db = sqlite3.connect(db_path)
        self._init_db()
        self._fetcher = PageFetcher(rate_limit_ms=crawl_delay_ms)
        self._content_hashes: set = set()
        self._pages_crawled = 0

    def crawl(self) -> Generator[CrawledPage, None, None]:
        """
        Crawl the site, yielding pages as they're processed.
        Resumes from where it left off if DB has prior state.
        """
        # Seed the frontier if empty
        if self._frontier_size() == 0:
            self._add_to_frontier(self.start_url, depth=0)
            # Try sitemap first
            self._discover_from_sitemap()

        # Load existing content hashes for dedup
        self._load_content_hashes()

        while self._pages_crawled < self.max_pages:
            url, depth = self._next_pending()
            if url is None:
                break

            page = self._fetch_and_process(url, depth)
            self._pages_crawled += 1
            yield page

            # Discover new URLs from internal links
            if page.status == CrawlStatus.FETCHED and depth < self.max_depth:
                for link in page.internal_links:
                    self._add_to_frontier(link, depth=depth + 1)

    def get_stats(self) -> dict:
        """Get current crawl statistics."""
        cursor = self._db.execute(
            "SELECT status, COUNT(*) FROM frontier GROUP BY status"
        )
        stats = dict(cursor.fetchall())
        return {
            "total_urls": sum(stats.values()),
            "fetched": stats.get("fetched", 0),
            "pending": stats.get("pending", 0),
            "failed": stats.get("failed", 0),
            "skipped": stats.get("skipped", 0),
            "pages_crawled_this_session": self._pages_crawled,
            "max_pages": self.max_pages,
            "duplicates": self._db.execute(
                "SELECT COUNT(*) FROM frontier WHERE is_duplicate=1"
            ).fetchone()[0],
        }

    def reset(self) -> None:
        """Clear all crawl state and start fresh."""
        self._db.execute("DELETE FROM frontier")
        self._db.commit()
        self._content_hashes.clear()
        self._pages_crawled = 0

    def close(self) -> None:
        """Close database connection."""
        self._db.close()

    # ─── Private ───────────────────────────────────────────────────────

    def _init_db(self) -> None:
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS frontier (
                url TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                depth INTEGER DEFAULT 0,
                http_status INTEGER DEFAULT 0,
                content_hash TEXT DEFAULT '',
                title TEXT DEFAULT '',
                word_count INTEGER DEFAULT 0,
                elapsed_ms REAL DEFAULT 0,
                error TEXT DEFAULT '',
                is_duplicate INTEGER DEFAULT 0,
                fetched_at REAL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_status ON frontier(status);
            CREATE INDEX IF NOT EXISTS idx_depth ON frontier(depth);
        """)
        self._db.commit()

    def _add_to_frontier(self, url: str, depth: int) -> None:
        """Add URL to frontier if it passes filters."""
        url = self._normalize_url(url)
        if not url or not self._should_crawl(url):
            return
        try:
            self._db.execute(
                "INSERT OR IGNORE INTO frontier (url, depth) VALUES (?, ?)",
                (url, depth)
            )
            self._db.commit()
        except sqlite3.Error:
            pass

    def _next_pending(self) -> tuple:
        """Get next URL to crawl (breadth-first by depth)."""
        row = self._db.execute(
            "SELECT url, depth FROM frontier WHERE status='pending' ORDER BY depth ASC LIMIT 1"
        ).fetchone()
        if row:
            return row[0], row[1]
        return None, 0

    def _frontier_size(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM frontier").fetchone()[0]

    def _fetch_and_process(self, url: str, depth: int) -> CrawledPage:
        """Fetch URL, parse, detect duplicates, update DB."""
        result = self._fetcher.fetch(url, use_cache=False)

        if not result.ok:
            page = CrawledPage(
                url=url, status=CrawlStatus.FAILED, depth=depth,
                http_status=result.status_code, error=result.error,
                elapsed_ms=result.elapsed_ms,
            )
            self._update_frontier(url, "failed", page)
            return page

        if not result.is_html:
            page = CrawledPage(url=url, status=CrawlStatus.SKIPPED, depth=depth,
                               http_status=result.status_code, elapsed_ms=result.elapsed_ms)
            self._update_frontier(url, "skipped", page)
            return page

        # Parse HTML
        parsed = parse_html(result.body, url)

        # Dedup by content hash
        content_hash = hashlib.md5(result.body.encode()[:10000]).hexdigest()[:12]
        is_dup = content_hash in self._content_hashes
        self._content_hashes.add(content_hash)

        page = CrawledPage(
            url=url, status=CrawlStatus.FETCHED, depth=depth,
            http_status=result.status_code, content_hash=content_hash,
            title=parsed.title, word_count=parsed.word_count,
            internal_links=parsed.internal_links,
            elapsed_ms=result.elapsed_ms, is_duplicate=is_dup,
        )
        self._update_frontier(url, "fetched", page)
        return page

    def _update_frontier(self, url: str, status: str, page: CrawledPage) -> None:
        """Update frontier record with crawl results."""
        self._db.execute("""
            UPDATE frontier SET
                status=?, http_status=?, content_hash=?,
                title=?, word_count=?, elapsed_ms=?,
                error=?, is_duplicate=?, fetched_at=?
            WHERE url=?
        """, (
            status, page.http_status, page.content_hash,
            page.title, page.word_count, page.elapsed_ms,
            page.error, int(page.is_duplicate), time.time(), url
        ))
        self._db.commit()

    def _load_content_hashes(self) -> None:
        """Load existing hashes from DB for dedup."""
        rows = self._db.execute(
            "SELECT content_hash FROM frontier WHERE content_hash != ''"
        ).fetchall()
        self._content_hashes = {row[0] for row in rows}

    def _discover_from_sitemap(self) -> None:
        """Try to discover URLs from sitemap.xml."""
        parsed = urlparse(self.start_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

        result = self._fetcher.fetch(sitemap_url)
        if not result.ok:
            return

        # Extract <loc> URLs from sitemap
        import re
        locs = re.findall(r"<loc>(.*?)</loc>", result.body)
        for loc in locs[:self.max_pages]:
            self._add_to_frontier(loc, depth=1)

    def _should_crawl(self, url: str) -> bool:
        """Check if URL passes all filters."""
        parsed = urlparse(url)

        # Domain check
        if parsed.netloc not in self.allowed_domains:
            return False

        # Scheme check
        if parsed.scheme not in ("http", "https"):
            return False

        # Exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.search(url):
                return False

        # Skip common non-page extensions
        path = parsed.path.lower()
        skip_ext = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css',
                    '.js', '.xml', '.zip', '.mp4', '.mp3', '.woff', '.woff2')
        if any(path.endswith(ext) for ext in skip_ext):
            return False

        return True

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL: strip fragment, trailing slash consistency."""
        if not url:
            return ""
        # Remove fragment
        url = url.split("#")[0]
        # Remove trailing slash for non-root paths
        parsed = urlparse(url)
        if parsed.path and parsed.path != "/" and parsed.path.endswith("/"):
            url = url.rstrip("/")
        return url

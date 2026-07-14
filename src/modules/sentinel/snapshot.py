"""
Snapshot Manager — Captures and stores SEO state snapshots.

Snapshots include: title, description, canonical, H1, hreflang,
schema, word count, internal links, robots directives.
"""

import json
import os
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SEOSnapshot:
    """Point-in-time capture of a page's SEO state."""
    url: str
    timestamp: float = field(default_factory=time.time)
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    h1: list = field(default_factory=list)
    meta_robots: str = ""
    hreflang_count: int = 0
    schema_count: int = 0
    word_count: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    status_code: int = 200
    response_time_ms: float = 0
    content_hash: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SEOSnapshot":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SnapshotManager:
    """
    Manages SEO snapshots — save, load, list, compare.

    Storage: .yseo/snapshots/{domain}/{url_hash}/{timestamp}.json
    """

    def __init__(self, storage_dir: str = ".yseo/snapshots"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def capture(self, url: str, page_data: dict, fetch_data: dict) -> SEOSnapshot:
        """Capture current SEO state as a snapshot."""
        content_hash = hashlib.md5(
            json.dumps(page_data, sort_keys=True).encode()
        ).hexdigest()[:12]

        snapshot = SEOSnapshot(
            url=url,
            title=page_data.get("title", ""),
            meta_description=page_data.get("meta_description", ""),
            canonical=page_data.get("canonical", ""),
            h1=page_data.get("h1", []),
            meta_robots=page_data.get("meta_robots", ""),
            hreflang_count=page_data.get("hreflang_count", 0),
            schema_count=page_data.get("json_ld_count", 0),
            word_count=page_data.get("word_count", 0),
            internal_links_count=page_data.get("internal_links_count", 0),
            external_links_count=page_data.get("external_links_count", 0),
            status_code=fetch_data.get("status_code", 0),
            response_time_ms=fetch_data.get("elapsed_ms", 0),
            content_hash=content_hash,
        )

        self._save(snapshot)
        return snapshot

    def get_latest(self, url: str) -> Optional[SEOSnapshot]:
        """Get the most recent snapshot for a URL."""
        snapshots = self._list_snapshots(url)
        if not snapshots:
            return None
        return snapshots[-1]

    def get_baseline(self, url: str) -> Optional[SEOSnapshot]:
        """Get the first (baseline) snapshot for a URL."""
        snapshots = self._list_snapshots(url)
        if not snapshots:
            return None
        return snapshots[0]

    def get_history(self, url: str, limit: int = 30) -> list[SEOSnapshot]:
        """Get snapshot history for a URL."""
        snapshots = self._list_snapshots(url)
        return snapshots[-limit:]

    def _url_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:12]

    def _get_dir(self, url: str) -> str:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace(":", "_")
        url_hash = self._url_hash(url)
        path = os.path.join(self.storage_dir, domain, url_hash)
        os.makedirs(path, exist_ok=True)
        return path

    def _save(self, snapshot: SEOSnapshot) -> None:
        """Save snapshot to disk."""
        directory = self._get_dir(snapshot.url)
        filename = f"{int(snapshot.timestamp)}.json"
        filepath = os.path.join(directory, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

    def _list_snapshots(self, url: str) -> list[SEOSnapshot]:
        """Load all snapshots for a URL, sorted by time."""
        directory = self._get_dir(url)
        snapshots = []

        if not os.path.exists(directory):
            return []

        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    snapshots.append(SEOSnapshot.from_dict(data))
                except (json.JSONDecodeError, OSError):
                    continue

        return snapshots

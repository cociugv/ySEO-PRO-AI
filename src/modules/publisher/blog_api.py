"""
Blog Publisher — Publishes content via API and triggers indexing.

Supports:
- yLink.pro blog API (POST /blog-api.php)
- WordPress REST API
- Custom API endpoints
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PublishResult:
    """Result of publishing content."""
    success: bool
    url: str = ""
    post_id: str = ""
    error: str = ""
    status_code: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "url": self.url,
            "post_id": self.post_id,
            "error": self.error,
        }


@dataclass
class BlogPost:
    """Blog post content ready for publishing."""
    title: str
    content: str
    slug: str = ""
    excerpt: str = ""
    language: str = "en"
    category: str = ""
    tags: list = field(default_factory=list)
    meta_description: str = ""
    featured_image: str = ""
    status: str = "publish"  # publish | draft | scheduled
    author: str = ""


class BlogPublisher:
    """
    Publishes blog posts via API.

    Supports multiple API formats:
    - ylink: yLink.pro custom API
    - wordpress: WordPress REST API
    - custom: Generic JSON API
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.api_url = self.config.get("blog_api", "")
        self.api_token = self.config.get("api_token", "")
        self.api_type = self.config.get("api_type", "ylink")

    def publish(self, post: BlogPost) -> PublishResult:
        """Publish a blog post via configured API."""
        if not self.api_url:
            return PublishResult(success=False, error="No blog API URL configured")

        if self.api_type == "ylink":
            return self._publish_ylink(post)
        elif self.api_type == "wordpress":
            return self._publish_wordpress(post)
        else:
            return self._publish_generic(post)

    def _publish_ylink(self, post: BlogPost) -> PublishResult:
        """Publish to yLink.pro blog API."""
        payload = {
            "action": "create",
            "title": post.title,
            "content": post.content,
            "slug": post.slug or self._slugify(post.title),
            "excerpt": post.excerpt,
            "language": post.language,
            "category": post.category,
            "tags": ",".join(post.tags),
            "meta_description": post.meta_description,
            "status": post.status,
        }

        return self._send_request(payload)

    def _publish_wordpress(self, post: BlogPost) -> PublishResult:
        """Publish to WordPress REST API."""
        payload = {
            "title": post.title,
            "content": post.content,
            "slug": post.slug or self._slugify(post.title),
            "excerpt": post.excerpt,
            "status": post.status,
            "categories": [post.category] if post.category else [],
            "tags": post.tags,
        }

        return self._send_request(payload, endpoint="/wp-json/wp/v2/posts")

    def _publish_generic(self, post: BlogPost) -> PublishResult:
        """Publish to a generic JSON API."""
        payload = {
            "title": post.title,
            "body": post.content,
            "slug": post.slug or self._slugify(post.title),
            "language": post.language,
            "meta": {
                "description": post.meta_description,
                "tags": post.tags,
            },
        }

        return self._send_request(payload)

    def _send_request(self, payload: dict, endpoint: str = "") -> PublishResult:
        """Send HTTP POST request to the API."""
        url = self.api_url + endpoint
        data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            response = urllib.request.urlopen(req, timeout=30)
            body = json.loads(response.read().decode("utf-8"))

            return PublishResult(
                success=True,
                url=body.get("url", body.get("link", "")),
                post_id=str(body.get("id", body.get("post_id", ""))),
                status_code=response.status,
            )

        except urllib.error.HTTPError as e:
            return PublishResult(
                success=False,
                error=f"HTTP {e.code}: {e.reason}",
                status_code=e.code,
            )
        except Exception as e:
            return PublishResult(
                success=False,
                error=str(e),
            )

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert title to URL-friendly slug."""
        import re
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:80].strip('-')

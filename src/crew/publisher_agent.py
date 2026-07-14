"""
Publisher Agent — Content publishing and indexing specialist.

Capabilities:
- Publish blog posts via API
- Ping IndexNow for instant indexing
- Batch URL submission
- Content scheduling
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..modules.publisher.blog_api import BlogPublisher, BlogPost
from ..modules.publisher.indexnow import IndexNowPinger


class PublisherAgent(BaseAgent):
    name = "publisher"
    role = "Content Publisher & Index Notifier"
    capabilities = ["publish", "indexnow", "ping", "submit", "blog"]
    modules_used = ["publisher"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Execute publishing action based on context."""
        start = time.time()
        context = context or {}
        action = context.get("action", "indexnow")  # publish | indexnow | batch

        if action == "publish":
            return self._publish_post(context, start)
        elif action == "batch":
            return self._batch_submit(context, start)
        else:
            return self._ping_indexnow(target_url, start)

    def _ping_indexnow(self, url: str, start: float) -> AgentResult:
        """Ping IndexNow for a single URL."""
        pinger = IndexNowPinger(self.config.get("integrations", {}).get("indexnow", {}))
        result = pinger.ping_single(url)

        return AgentResult(
            agent_name=self.name,
            success=result.success,
            summary=f"IndexNow ping {'succeeded' if result.success else 'failed'} for {url}",
            data={
                "url": url,
                "engine": result.engine,
                "status_code": result.status_code,
                "error": result.error,
            },
            elapsed_seconds=time.time() - start,
        )

    def _publish_post(self, context: dict, start: float) -> AgentResult:
        """Publish a blog post."""
        publisher = BlogPublisher(self.config.get("modules", {}).get("publisher", {}))

        post = BlogPost(
            title=context.get("title", ""),
            content=context.get("content", ""),
            slug=context.get("slug", ""),
            language=context.get("language", "en"),
            meta_description=context.get("meta_description", ""),
            tags=context.get("tags", []),
        )

        result = publisher.publish(post)

        # If published successfully, ping IndexNow
        if result.success and result.url:
            pinger = IndexNowPinger(self.config.get("integrations", {}).get("indexnow", {}))
            pinger.ping_single(result.url)

        return AgentResult(
            agent_name=self.name,
            success=result.success,
            summary=f"Published: {result.url}" if result.success else f"Publish failed: {result.error}",
            data=result.to_dict(),
            elapsed_seconds=time.time() - start,
        )

    def _batch_submit(self, context: dict, start: float) -> AgentResult:
        """Submit multiple URLs to IndexNow."""
        urls = context.get("urls", [])
        if not urls:
            return AgentResult(
                agent_name=self.name,
                success=False,
                summary="No URLs provided for batch submission",
                elapsed_seconds=time.time() - start,
            )

        pinger = IndexNowPinger(self.config.get("integrations", {}).get("indexnow", {}))
        results = pinger.ping_all_engines(urls)

        successful = sum(1 for r in results if r.success)

        return AgentResult(
            agent_name=self.name,
            success=successful > 0,
            summary=f"Batch submitted {len(urls)} URLs to {successful}/{len(results)} engines",
            data={
                "urls_count": len(urls),
                "engines_pinged": len(results),
                "engines_successful": successful,
            },
            elapsed_seconds=time.time() - start,
        )

"""
Strategist Agent — SEO planning, competitor intel, and opportunity discovery.

Capabilities:
- Competitor SEO comparison
- Backlink opportunity finding
- Programmatic page planning
- SEO strategy recommendations
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..modules.radar.tracker import CompetitorTracker
from ..modules.radar.opportunities import BacklinkFinder
from ..modules.architect.generator import ProgrammaticGenerator


class StrategistAgent(BaseAgent):
    name = "strategist"
    role = "SEO Strategist & Competitor Analyst"
    capabilities = ["compete", "strategy", "backlinks", "opportunities", "programmatic"]
    modules_used = ["radar", "architect"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Execute strategy analysis."""
        start = time.time()
        context = context or {}
        action = context.get("action", "full")  # full | compete | opportunities | programmatic

        if action == "compete" and context.get("competitor"):
            return self._compare_competitor(target_url, context["competitor"], start)
        elif action == "opportunities":
            return self._find_opportunities(target_url, context, start)
        elif action == "programmatic":
            return self._plan_programmatic(target_url, context, start)
        else:
            return self._full_strategy(target_url, context, start)

    def _compare_competitor(self, url: str, competitor_url: str, start: float) -> AgentResult:
        """Compare your site against a competitor."""
        tracker = CompetitorTracker(self.config)
        comparison = tracker.compare(url, competitor_url)

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Compared {url} vs {competitor_url}: {len(comparison.advantages)} advantages, {len(comparison.disadvantages)} gaps",
            data={
                "metrics": {k: {"yours": v[0], "theirs": v[1]} for k, v in comparison.metrics.items()},
                "advantages": comparison.advantages,
                "disadvantages": comparison.disadvantages,
            },
            recommendations=comparison.disadvantages[:5],
            elapsed_seconds=time.time() - start,
        )

    def _find_opportunities(self, url: str, context: dict, start: float) -> AgentResult:
        """Find backlink opportunities."""
        finder = BacklinkFinder(self.config)
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        directories = finder.find_directories(domain)
        keywords = context.get("keywords", ["url shortener", "link management", "QR code"])
        guest_posts = finder.find_guest_post_targets(keywords)

        all_opps = directories + guest_posts
        plan = finder.generate_outreach_plan(all_opps)

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Found {len(all_opps)} backlink opportunities ({len(directories)} directories, {len(guest_posts)} guest post queries)",
            data={
                "total_opportunities": len(all_opps),
                "directories": len(directories),
                "guest_post_queries": len(guest_posts),
                "weekly_plan": plan.get("weekly_targets", [])[:4],
            },
            recommendations=[
                f"Submit to {opp.url}" for opp in directories[:5]
            ],
            elapsed_seconds=time.time() - start,
        )

    def _plan_programmatic(self, url: str, context: dict, start: float) -> AgentResult:
        """Plan programmatic SEO pages."""
        gen_config = {
            "brand_name": self.config.get("platform", {}).get("name", "yLink.pro"),
            "base_url": url,
            "languages": self.config.get("targets", {}).get("languages", ["en"]),
        }
        generator = ProgrammaticGenerator(gen_config)

        # Generate sample pages
        sample_cities = [
            {"name": "Berlin", "country": "Germany"},
            {"name": "London", "country": "UK"},
            {"name": "Paris", "country": "France"},
            {"name": "Tokyo", "country": "Japan"},
            {"name": "New York", "country": "USA"},
        ]

        city_pages = generator.generate_city_pages(sample_cities)
        competitors = [{"name": "Bitly"}, {"name": "TinyURL"}, {"name": "Rebrandly"}]
        vs_pages = generator.generate_comparison_pages(competitors)

        total_pages = len(city_pages) + len(vs_pages)

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Generated {total_pages} programmatic page specs ({len(city_pages)} city + {len(vs_pages)} comparison)",
            data={
                "city_pages": [p.to_dict() for p in city_pages[:3]],
                "comparison_pages": [p.to_dict() for p in vs_pages],
                "total_specs": total_pages,
            },
            recommendations=[
                f"Create page: {p.title}" for p in city_pages[:5]
            ],
            elapsed_seconds=time.time() - start,
        )

    def _full_strategy(self, url: str, context: dict, start: float) -> AgentResult:
        """Run full strategic analysis."""
        # Combine opportunities + programmatic planning
        opp_result = self._find_opportunities(url, context, start)
        prog_result = self._plan_programmatic(url, context, start)

        total_recs = opp_result.recommendations + prog_result.recommendations

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Strategy complete: {opp_result.data.get('total_opportunities', 0)} link opportunities + {prog_result.data.get('total_specs', 0)} page specs",
            data={
                "opportunities": opp_result.data,
                "programmatic": prog_result.data,
            },
            recommendations=total_recs[:10],
            elapsed_seconds=time.time() - start,
        )

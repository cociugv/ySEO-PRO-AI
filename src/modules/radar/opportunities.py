"""
Backlink Opportunity Finder — Discovers link building targets.

Strategies:
- Directory submission targets
- Guest post opportunities
- Broken link building targets
- Resource page targets
- Competitor backlink gap analysis
"""

from dataclasses import dataclass, field


@dataclass
class LinkOpportunity:
    """A potential backlink opportunity."""
    url: str
    strategy: str  # directory | guest_post | broken_link | resource | competitor_gap
    domain_authority: int = 0
    relevance_score: float = 0.0
    contact_info: str = ""
    notes: str = ""
    priority: str = "medium"  # high | medium | low

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "strategy": self.strategy,
            "domain_authority": self.domain_authority,
            "relevance_score": self.relevance_score,
            "contact_info": self.contact_info,
            "notes": self.notes,
            "priority": self.priority,
        }


class BacklinkFinder:
    """
    Finds backlink opportunities using multiple strategies.

    Works with free data sources (no paid API required).
    """

    # Common directory categories for SaaS/URL shorteners
    DIRECTORY_TEMPLATES = [
        {"category": "SaaS Directories", "examples": [
            "https://www.producthunt.com",
            "https://alternativeto.net",
            "https://www.saasworthy.com",
            "https://www.g2.com",
            "https://stackshare.io",
        ]},
        {"category": "Startup Directories", "examples": [
            "https://betalist.com",
            "https://www.startupranking.com",
            "https://launching.io",
        ]},
        {"category": "Tool Directories", "examples": [
            "https://toolify.ai",
            "https://www.toolhunt.net",
            "https://www.webdesignerdepot.com/resources",
        ]},
        {"category": "URL Shortener Lists", "examples": [
            "https://zapier.com/blog/best-url-shorteners",
            "https://blog.hubspot.com/marketing/url-shorteners",
        ]},
    ]

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.industry = self.config.get("industry", "saas")

    def find_directories(self, domain: str, industry: str = "") -> list[LinkOpportunity]:
        """Find relevant directory submission opportunities."""
        target_industry = industry or self.industry
        opportunities = []

        for directory in self.DIRECTORY_TEMPLATES:
            for url in directory["examples"]:
                opportunities.append(LinkOpportunity(
                    url=url,
                    strategy="directory",
                    relevance_score=0.8,
                    notes=f"Submit to {directory['category']}",
                    priority="high" if "producthunt" in url or "g2" in url else "medium",
                ))

        return opportunities

    def find_guest_post_targets(self, niche_keywords: list[str]) -> list[LinkOpportunity]:
        """
        Generate search queries to find guest post opportunities.

        Returns queries the user should search manually
        (we don't scrape Google directly).
        """
        opportunities = []

        search_patterns = [
            '"{keyword}" + "write for us"',
            '"{keyword}" + "guest post"',
            '"{keyword}" + "contribute"',
            '"{keyword}" + "submit an article"',
            '"{keyword}" + inurl:guest-post',
        ]

        for keyword in niche_keywords[:5]:
            for pattern in search_patterns:
                query = pattern.replace("{keyword}", keyword)
                opportunities.append(LinkOpportunity(
                    url=f"https://www.google.com/search?q={query}",
                    strategy="guest_post",
                    relevance_score=0.7,
                    notes=f"Search: {query}",
                    priority="medium",
                ))

        return opportunities

    def generate_outreach_plan(self, opportunities: list[LinkOpportunity]) -> dict:
        """Generate a structured outreach plan from opportunities."""
        plan = {
            "total_opportunities": len(opportunities),
            "by_strategy": {},
            "by_priority": {"high": [], "medium": [], "low": []},
            "weekly_targets": [],
        }

        for opp in opportunities:
            # Group by strategy
            if opp.strategy not in plan["by_strategy"]:
                plan["by_strategy"][opp.strategy] = []
            plan["by_strategy"][opp.strategy].append(opp.to_dict())

            # Group by priority
            plan["by_priority"][opp.priority].append(opp.to_dict())

        # Create weekly targets (5 high priority + 10 medium per week)
        high_queue = plan["by_priority"]["high"][:20]
        medium_queue = plan["by_priority"]["medium"][:40]

        week = 1
        while high_queue or medium_queue:
            week_targets = high_queue[:5] + medium_queue[:10]
            high_queue = high_queue[5:]
            medium_queue = medium_queue[10:]
            if week_targets:
                plan["weekly_targets"].append({
                    "week": week,
                    "targets": week_targets,
                    "count": len(week_targets),
                })
            week += 1

        return plan

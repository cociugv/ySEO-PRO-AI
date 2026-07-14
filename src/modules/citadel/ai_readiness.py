"""
AI Search Readiness Scorer — Measures how well a page performs in AI search.

Evaluates:
- Citability (can AI cite specific facts from this page?)
- Entity presence (are key entities clearly defined?)
- Clear answers (does content provide direct answers to questions?)
- Structured information (lists, tables, definitions)
- Authority signals (author info, sources, dates)
- Content freshness
"""

from dataclasses import dataclass, field
from ...core.pipeline import PipelineContext, Issue, Severity, Stage


@dataclass
class AIReadinessReport:
    """AI Search Readiness assessment."""
    url: str
    overall_score: int = 0  # 0-100
    citability_score: int = 0
    entity_score: int = 0
    answer_clarity_score: int = 0
    structure_score: int = 0
    authority_score: int = 0
    freshness_score: int = 0
    recommendations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "overall_score": self.overall_score,
            "breakdown": {
                "citability": self.citability_score,
                "entity_presence": self.entity_score,
                "answer_clarity": self.answer_clarity_score,
                "structure": self.structure_score,
                "authority": self.authority_score,
                "freshness": self.freshness_score,
            },
            "recommendations": self.recommendations,
        }


class AIReadinessScorer:
    """
    Scores a page's readiness for AI search engines
    (Google AI Overviews, ChatGPT, Perplexity, etc.)
    """

    def __init__(self, config: dict = None):
        self.config = config or {}

    def register(self, pipeline) -> None:
        """Register into pipeline."""
        pipeline.register(Stage.DIAGNOSE, self.score_readiness)

    def score_readiness(self, ctx: PipelineContext) -> None:
        """DIAGNOSE: Calculate AI readiness score."""
        page = ctx.scan_data.get("page", {})
        report = self.calculate_score(ctx.target_url, page)

        ctx.scan_data["ai_readiness"] = report.to_dict()

        if report.overall_score < 50:
            ctx.issues.append(Issue(
                code="AI-001",
                title=f"Low AI Search Readiness Score ({report.overall_score}/100)",
                severity=Severity.MEDIUM,
                module="citadel",
                url=ctx.target_url,
                description="Page is not well-optimized for AI search engines",
                evidence=report.to_dict(),
            ))

        for rec in report.recommendations:
            ctx.issues.append(Issue(
                code=f"AI-{rec['code']}",
                title=rec["title"],
                severity=Severity.LOW,
                module="citadel",
                url=ctx.target_url,
                description=rec["description"],
                fix_available=rec.get("fixable", False),
            ))

    def calculate_score(self, url: str, page_data: dict) -> AIReadinessReport:
        """Calculate comprehensive AI readiness score."""
        report = AIReadinessReport(url=url)

        report.citability_score = self._score_citability(page_data)
        report.entity_score = self._score_entities(page_data)
        report.answer_clarity_score = self._score_answers(page_data)
        report.structure_score = self._score_structure(page_data)
        report.authority_score = self._score_authority(page_data)
        report.freshness_score = self._score_freshness(page_data)

        # Weighted average
        weights = {
            "citability": 0.25,
            "entity": 0.20,
            "answer_clarity": 0.20,
            "structure": 0.15,
            "authority": 0.10,
            "freshness": 0.10,
        }

        report.overall_score = int(
            report.citability_score * weights["citability"] +
            report.entity_score * weights["entity"] +
            report.answer_clarity_score * weights["answer_clarity"] +
            report.structure_score * weights["structure"] +
            report.authority_score * weights["authority"] +
            report.freshness_score * weights["freshness"]
        )

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report, page_data)

        return report

    def _score_citability(self, page_data: dict) -> int:
        """Score: Can AI cite specific facts from this page?"""
        score = 0
        word_count = page_data.get("word_count", 0)

        # Sufficient content length
        if word_count >= 500:
            score += 25
        elif word_count >= 300:
            score += 15

        # Has clear title
        if page_data.get("title"):
            score += 15

        # Has meta description (summary)
        if page_data.get("meta_description"):
            score += 15

        # Has structured headings (H2s indicate sections)
        h2_count = len(page_data.get("h2", []))
        if h2_count >= 3:
            score += 25
        elif h2_count >= 1:
            score += 15

        # Has schema (citable structured data)
        if page_data.get("json_ld_count", 0) > 0:
            score += 20

        return min(100, score)

    def _score_entities(self, page_data: dict) -> int:
        """Score: Are key entities clearly defined?"""
        score = 0

        # Title contains a clear entity (not generic)
        title = page_data.get("title", "")
        if title and len(title) > 10:
            score += 25

        # H1 is specific
        h1_list = page_data.get("h1", [])
        if h1_list and len(h1_list[0]) > 5:
            score += 20

        # Has OG metadata (entity signals)
        if page_data.get("og_title"):
            score += 15

        # Has schema (defines entities)
        if page_data.get("json_ld_count", 0) > 0:
            score += 25

        # URL is descriptive (not random IDs)
        url = page_data.get("url", "")
        if url and not any(c.isdigit() for c in url.split("/")[-1][:5]):
            score += 15

        return min(100, score)

    def _score_answers(self, page_data: dict) -> int:
        """Score: Does content provide direct answers?"""
        score = 0

        # Has multiple headings (likely answering questions)
        h2_count = len(page_data.get("h2", []))
        h3_count = len(page_data.get("h3", []))

        if h2_count >= 5:
            score += 30
        elif h2_count >= 3:
            score += 20
        elif h2_count >= 1:
            score += 10

        # Good content length (enough to answer deeply)
        word_count = page_data.get("word_count", 0)
        if word_count >= 1500:
            score += 30
        elif word_count >= 800:
            score += 20
        elif word_count >= 400:
            score += 10

        # Meta description acts as a summary answer
        desc_len = page_data.get("description_length", 0)
        if 100 <= desc_len <= 160:
            score += 20

        # Hierarchy depth (H2 + H3 = well-structured answers)
        if h3_count >= 3:
            score += 20

        return min(100, score)

    def _score_structure(self, page_data: dict) -> int:
        """Score: Is information structured (lists, tables)?"""
        score = 0

        # Heading hierarchy
        h2_count = len(page_data.get("h2", []))
        h3_count = len(page_data.get("h3", []))

        if h2_count >= 3 and h3_count >= 2:
            score += 40
        elif h2_count >= 2:
            score += 25

        # Schema markup
        if page_data.get("json_ld_count", 0) > 0:
            score += 30

        # Internal links (navigation structure)
        internal = page_data.get("internal_links_count", 0)
        if internal >= 5:
            score += 15
        elif internal >= 2:
            score += 10

        # Images (visual structure)
        images = page_data.get("images_count", 0)
        if images >= 2:
            score += 15

        return min(100, score)

    def _score_authority(self, page_data: dict) -> int:
        """Score: Does the page signal authority?"""
        score = 50  # Base score (we can't fully assess authority from on-page alone)

        # Has schema (publisher/author info)
        if page_data.get("json_ld_count", 0) > 0:
            score += 20

        # External links (citing sources)
        external = page_data.get("external_links_count", 0)
        if external >= 3:
            score += 15
        elif external >= 1:
            score += 10

        # HTTPS
        url = page_data.get("url", "")
        if url.startswith("https://"):
            score += 15

        return min(100, score)

    def _score_freshness(self, page_data: dict) -> int:
        """Score: Is the content fresh/updated? (limited from on-page data)"""
        score = 50  # Base — we'd need last-modified headers for full assessment

        # If page has schema with dateModified, that's a positive signal
        if page_data.get("json_ld_count", 0) > 0:
            score += 20

        # Good word count suggests maintained content
        if page_data.get("word_count", 0) >= 500:
            score += 15

        # Internal links suggest integration (maintained)
        if page_data.get("internal_links_count", 0) >= 3:
            score += 15

        return min(100, score)

    def _generate_recommendations(self, report: AIReadinessReport, page_data: dict) -> list[dict]:
        """Generate actionable recommendations based on scores."""
        recs = []

        if report.citability_score < 60:
            recs.append({
                "code": "010",
                "title": "Improve citability — add clear facts and statistics",
                "description": "Include specific numbers, dates, and definitions AI can quote",
                "fixable": False,
            })

        if report.entity_score < 60:
            recs.append({
                "code": "020",
                "title": "Define entities clearly — add schema markup",
                "description": "Use JSON-LD to explicitly define what this page is about",
                "fixable": True,
            })

        if report.answer_clarity_score < 60:
            recs.append({
                "code": "030",
                "title": "Add direct answers in first paragraphs",
                "description": "Start sections with concise answers before elaborating",
                "fixable": False,
            })

        if report.structure_score < 60:
            recs.append({
                "code": "040",
                "title": "Add structured content (lists, headings, tables)",
                "description": "Break content into scannable sections with clear H2/H3 hierarchy",
                "fixable": False,
            })

        if page_data.get("json_ld_count", 0) == 0:
            recs.append({
                "code": "050",
                "title": "Add JSON-LD structured data",
                "description": "Schema markup helps AI understand page content and entities",
                "fixable": True,
            })

        return recs

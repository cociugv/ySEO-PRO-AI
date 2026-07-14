"""
Benchmark Fixtures — HTML samples with expected findings.

Each fixture defines:
- html: the page content
- url: simulated URL
- expected_issues: list of issue codes that MUST be found
- expected_no_issues: list of issue codes that MUST NOT be found
"""


FIXTURES = [
    # ─── Perfect page: no issues ────────────────────────────────────
    {
        "name": "perfect_page",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Perfect Page Title for Testing</title>
<meta name="description" content="This is a well-crafted meta description that explains what the page is about clearly and concisely.">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="https://example.com/perfect">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","name":"Perfect"}</script>
</head>
<body>
<h1>Perfect Page Heading</h1>
<p>This page has substantial content. It contains multiple paragraphs with real text that provides value to readers. The content is well structured with proper headings, internal links, and multimedia elements that enhance the user experience significantly. We cover everything you need to know about this topic in great detail.</p>
<p>Additional content paragraph with more useful information about the topic being discussed. This ensures the word count is above the minimum threshold for content quality. We believe in providing comprehensive coverage of every subject matter we address on this website.</p>
<p>Yet another paragraph explaining things in detail so that search engines and users alike find this page valuable and informative. Quality content is the foundation of good SEO. Our team of experts has carefully crafted this content to provide maximum value to our readers and visitors. We hope you find it useful and informative.</p>
<p>Furthermore, we want to make sure this page demonstrates all the qualities of well-optimized content including proper structure, sufficient length, relevant information, and engaging writing style that keeps readers interested throughout the entire page.</p>
<p>""" + " ".join(["content"] * 200) + """</p>
<a href="/other-page">Related content</a>
<a href="/about">About us</a>
<img src="/hero.jpg" alt="Descriptive alt text" width="800" height="400">
</body></html>""",
        "url": "https://example.com/perfect",
        "expected_issues": [],
        "expected_no_issues": ["TECH-020", "TECH-025", "TECH-030", "TECH-040", "TECH-045", "TECH-050", "TECH-070"],
    },
    # ─── Missing everything ─────────────────────────────────────────
    {
        "name": "empty_head",
        "html": "<html><head></head><body><p>Short.</p></body></html>",
        "url": "https://example.com/empty",
        "expected_issues": ["TECH-020", "TECH-025", "TECH-030", "TECH-040", "TECH-045", "TECH-050", "TECH-070"],
        "expected_no_issues": [],
    },
    # ─── Title too short ────────────────────────────────────────────
    {
        "name": "title_too_short",
        "html": '<html lang="en"><head><title>Hi</title><meta name="description" content="A good description for testing purposes and SEO checks that is long enough."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/p"><script type="application/ld+json">{}</script></head><body><h1>Hello World Page</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/p",
        "expected_issues": ["TECH-021"],
        "expected_no_issues": ["TECH-020", "TECH-025", "TECH-030"],
    },
    # ─── Title too long ─────────────────────────────────────────────
    {
        "name": "title_too_long",
        "html": '<html lang="en"><head><title>' + "A" * 80 + '</title><meta name="description" content="Good description that is the right length for search results."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/p"><script type="application/ld+json">{}</script></head><body><h1>Page</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/p",
        "expected_issues": ["TECH-022"],
        "expected_no_issues": ["TECH-020", "TECH-021"],
    },
    # ─── Multiple H1 ───────────────────────────────────────────────
    {
        "name": "multiple_h1",
        "html": '<html lang="en"><head><title>Good Title For Page</title><meta name="description" content="Good description content here for testing purposes."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/p"><script type="application/ld+json">{}</script></head><body><h1>First</h1><h1>Second</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/p",
        "expected_issues": ["TECH-031"],
        "expected_no_issues": ["TECH-030"],
    },
    # ─── HTTP (not HTTPS) ──────────────────────────────────────────
    {
        "name": "http_no_ssl",
        "html": '<html lang="en"><head><title>Good Title Here Now</title><meta name="description" content="Good meta description for the page."><meta name="viewport" content="width=device-width"><link rel="canonical" href="http://x.com/p"><script type="application/ld+json">{}</script></head><body><h1>Page</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "http://x.com/p",
        "expected_issues": ["TECH-060"],
        "expected_no_issues": [],
    },
    # ─── Thin content ──────────────────────────────────────────────
    {
        "name": "thin_content",
        "html": '<html lang="en"><head><title>Good Title For This Page</title><meta name="description" content="A proper meta description with enough characters."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/thin"><script type="application/ld+json">{}</script></head><body><h1>Hello</h1><p>Very short.</p></body></html>',
        "url": "https://x.com/thin",
        "expected_issues": ["TECH-070"],
        "expected_no_issues": ["TECH-020", "TECH-025"],
    },
    # ─── Meta description too short ────────────────────────────────
    {
        "name": "desc_too_short",
        "html": '<html lang="en"><head><title>Good Title For This Page</title><meta name="description" content="Short."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/d"><script type="application/ld+json">{}</script></head><body><h1>Page</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/d",
        "expected_issues": ["TECH-026"],
        "expected_no_issues": ["TECH-025", "TECH-027"],
    },
    # ─── Meta description too long ─────────────────────────────────
    {
        "name": "desc_too_long",
        "html": '<html lang="en"><head><title>Good Title For This Page</title><meta name="description" content="' + "x" * 200 + '"><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/d"><script type="application/ld+json">{}</script></head><body><h1>Page</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/d",
        "expected_issues": ["TECH-027"],
        "expected_no_issues": ["TECH-025", "TECH-026"],
    },
    # ─── No schema ─────────────────────────────────────────────────
    {
        "name": "no_schema",
        "html": '<html lang="en"><head><title>Good Title For Testing</title><meta name="description" content="Good meta description for this page content."><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://x.com/ns"></head><body><h1>Content</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/ns",
        "expected_issues": ["TECH-050"],
        "expected_no_issues": ["TECH-020", "TECH-025"],
    },
    # ─── Missing viewport ──────────────────────────────────────────
    {
        "name": "no_viewport",
        "html": '<html lang="en"><head><title>Good Title For Testing</title><meta name="description" content="Good meta description for this page content."><link rel="canonical" href="https://x.com/nv"><script type="application/ld+json">{}</script></head><body><h1>Content</h1><p>' + "word " * 100 + '</p></body></html>',
        "url": "https://x.com/nv",
        "expected_issues": ["TECH-045"],
        "expected_no_issues": ["TECH-020", "TECH-025"],
    },
]

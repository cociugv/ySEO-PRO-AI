"""
Template Engine — Simple template processing for programmatic pages.

Uses {variable} syntax for interpolation.
Supports conditional blocks and loops.
"""

import re
from typing import Any


class TemplateEngine:
    """
    Lightweight template engine for generating SEO page content.

    Syntax:
    - {variable} — simple substitution
    - {variable|default_value} — with default
    - {{#if condition}}...{{/if}} — conditional
    - {{#each items}}...{{/each}} — loop
    """

    def render(self, template: str, data: dict) -> str:
        """Render a template with data context."""
        result = template

        # Process conditionals first
        result = self._process_conditionals(result, data)

        # Process loops
        result = self._process_loops(result, data)

        # Process simple variables
        result = self._process_variables(result, data)

        return result

    def _process_variables(self, template: str, data: dict) -> str:
        """Replace {variable} and {variable|default} patterns."""
        def replace_var(match):
            key = match.group(1)
            if "|" in key:
                key, default = key.split("|", 1)
                return str(data.get(key.strip(), default.strip()))
            return str(data.get(key.strip(), match.group(0)))

        return re.sub(r'\{(\w+(?:\|\w+)?)\}', replace_var, template)

    def _process_conditionals(self, template: str, data: dict) -> str:
        """Process {{#if key}}...{{/if}} blocks."""
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'

        def replace_if(match):
            key = match.group(1)
            content = match.group(2)
            if data.get(key):
                return content
            return ""

        return re.sub(pattern, replace_if, template, flags=re.DOTALL)

    def _process_loops(self, template: str, data: dict) -> str:
        """Process {{#each items}}...{{/each}} blocks."""
        pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'

        def replace_each(match):
            key = match.group(1)
            body = match.group(2)
            items = data.get(key, [])
            if not isinstance(items, list):
                return ""
            parts = []
            for item in items:
                if isinstance(item, dict):
                    parts.append(self._process_variables(body, item))
                else:
                    parts.append(body.replace("{item}", str(item)))
            return "".join(parts)

        return re.sub(pattern, replace_each, template, flags=re.DOTALL)

    def render_page_html(self, spec: dict, template_html: str = "") -> str:
        """Render a full HTML page from a PageSpec dict."""
        if not template_html:
            template_html = self._default_page_template()

        return self.render(template_html, spec)

    def _default_page_template(self) -> str:
        return """<!DOCTYPE html>
<html lang="{language|en}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <link rel="canonical" href="{canonical_url}">
</head>
<body>
    <h1>{h1}</h1>
    <div class="content">
        {content}
    </div>
</body>
</html>"""

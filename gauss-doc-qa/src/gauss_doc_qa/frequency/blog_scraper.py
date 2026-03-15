"""Blog post scraper for GAUSS function mention counting.

Fetches blog listing pages from aptech.com/blog and scans post content
for mentions of known GAUSS function names.
"""

from __future__ import annotations

import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from urllib.error import URLError


_USER_AGENT = "gauss-doc-qa/0.1 (documentation-quality-tool)"
_BLOG_BASE_URL = "https://www.aptech.com/blog/"
_REQUEST_DELAY = 0.5  # seconds between requests


class _TextExtractor(HTMLParser):
    """Simple HTML parser that extracts visible text content."""

    def __init__(self):
        super().__init__()
        self._text_parts: list[str] = []
        self._skip_tags = {"script", "style", "noscript"}
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._text_parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._text_parts)


class _LinkExtractor(HTMLParser):
    """Extract blog post URLs from a listing page."""

    def __init__(self, base_url: str):
        super().__init__()
        self.post_urls: list[str] = []
        self._base_url = base_url
        self._seen: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        if not href or href in self._seen:
            return
        # Match blog post URLs (contain /blog/ but not just /blog/ itself or pagination)
        if "/blog/" in href and href != self._base_url and href.rstrip("/") != self._base_url.rstrip("/"):
            # Skip pagination links like /blog/page/2/
            if "/blog/page/" in href:
                return
            # Skip category/tag links
            if "/blog/category/" in href or "/blog/tag/" in href:
                return
            self._seen.add(href)
            self.post_urls.append(href)


def _fetch_url(url: str) -> str | None:
    """Fetch a URL and return HTML content, or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, OSError, TimeoutError, UnicodeDecodeError) as exc:
        print(f"Warning: Failed to fetch {url}: {exc}", file=sys.stderr)
        return None


def scrape_blog_mentions(
    known_functions: set[str],
    max_pages: int = 10,
) -> dict[str, int]:
    """Scrape aptech.com/blog for mentions of known GAUSS functions.

    Args:
        known_functions: Set of function names to search for.
        max_pages: Maximum number of blog listing pages to fetch.

    Returns:
        Dict mapping function_name -> total_mention_count across all posts.
        Returns empty dict if network requests fail.
    """
    if not known_functions:
        return {}

    # Build word-boundary regex, sort by length descending for correct matching
    pattern = re.compile(
        r"\b(" + "|".join(
            re.escape(f) for f in sorted(known_functions, key=len, reverse=True)
        ) + r")\b",
        re.IGNORECASE,
    )

    counts: dict[str, int] = {}
    post_urls: list[str] = []

    # Fetch listing pages to discover post URLs
    for page_num in range(1, max_pages + 1):
        if page_num == 1:
            url = _BLOG_BASE_URL
        else:
            url = f"{_BLOG_BASE_URL}page/{page_num}/"

        html = _fetch_url(url)
        if html is None:
            break

        extractor = _LinkExtractor(_BLOG_BASE_URL)
        try:
            extractor.feed(html)
        except Exception:
            break

        if not extractor.post_urls:
            break  # No more posts found

        post_urls.extend(extractor.post_urls)
        time.sleep(_REQUEST_DELAY)

    # Fetch each post and count function mentions
    for post_url in post_urls:
        html = _fetch_url(post_url)
        if html is None:
            time.sleep(_REQUEST_DELAY)
            continue

        text_extractor = _TextExtractor()
        try:
            text_extractor.feed(html)
        except Exception:
            time.sleep(_REQUEST_DELAY)
            continue

        text = text_extractor.get_text()

        for match in pattern.finditer(text):
            func_name = match.group(1)
            # Normalize to the canonical case from known_functions
            func_lower = func_name.lower()
            canonical = None
            for kf in known_functions:
                if kf.lower() == func_lower:
                    canonical = kf
                    break
            if canonical:
                counts[canonical] = counts.get(canonical, 0) + 1

        time.sleep(_REQUEST_DELAY)

    return counts

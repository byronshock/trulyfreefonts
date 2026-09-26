"""The methodology, privacy and about pages: Markdown to HTML, and the methodology extract.

Markdown is rendered with ``MarkdownIt("commonmark", {"html": False}).enable("table")`` plus
``mdit_py_plugins.anchors.anchors_plugin`` for stable heading ids. ``html=False`` means page
text can never inject a ``<script>`` or ``style`` attribute past the CSP.

``/methodology/`` is generated from ``docs/ranking-methodology.md`` so the two can't drift.
It takes the numbered ``## N.`` sections in ``METHODOLOGY_SECTIONS``; a missing section fails
the build loudly.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
METHODOLOGY_MD = REPO_ROOT / "docs" / "ranking-methodology.md"
CONTENT_DIR = REPO_ROOT / "site" / "content"

# §1 in plain words, §5 the rankings (the two desktop views), §6 tiers, §11 known biases.
METHODOLOGY_SECTIONS: tuple[int, ...] = (1, 5, 6, 11)


def render_markdown(text: str) -> str:
    """Render Markdown to HTML with raw HTML disabled and anchored headings."""
    raise NotImplementedError("M2 step 7")


def extract_sections(
    markdown: str, numbers: tuple[int, ...] = METHODOLOGY_SECTIONS
) -> dict[int, str]:
    """Return each numbered ``## N.`` section's Markdown (heading included), by number.

    Raises ``KeyError`` naming the first missing section.
    """
    raise NotImplementedError("M2 step 7")


def page_contexts(doc: dict) -> dict[str, dict]:
    """Return the template context of each content page, keyed by URL path (``/privacy/``)."""
    raise NotImplementedError("M2 step 7")

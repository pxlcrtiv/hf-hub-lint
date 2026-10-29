"""Card-content checks: presence, length, frontmatter, links, sections."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding
from hf_hub_lint.checks.frontmatter import _yaml_block


def ch_card_present(p: dict) -> list[Finding]:
    card = (p.get("card") or "").strip()
    if len(card) < 40:
        return [Finding(
            id="CARD_MISSING", severity="error",
            title="Missing model card / README",
            detail="The repository has no README.md (or one shorter than 40 chars). Recruiters, users, and the Hub UI all render the card first.",
            fix="Add a README.md: what the artifact is, what it does, how to use it.",
        )]
    return []


def ch_card_length(p: dict) -> list[Finding]:
    card = p.get("card") or ""
    if 40 <= len(card.strip()) < 250:
        return [Finding(
            id="CARD_TRIM", severity="info",
            title="Model card is very short",
            detail=f"README.md is only {len(card.strip())} chars — likely a stub.",
            fix="Expand: description, intended use, training data, limitations, license.",
        )]
    return []


def ch_frontmatter(p: dict) -> list[Finding]:
    if _yaml_block(p.get("card") or "").strip():
        return []
    return [Finding(
        id="FRONTMATTER", severity="warn",
        title="No YAML frontmatter in the card",
        detail="The Hub renders structured metadata (license, tags, metrics) from the card's frontmatter block.",
        fix="Start README.md with a --- delimited block of key: value pairs.",
    )]


def ch_http_links(p: dict) -> list[Finding]:
    card = p.get("card") or ""
    if "http://" in card:
        return [Finding(
            id="INSECURE_URL", severity="warn",
            title="Plain-HTTP link(s) found in the card",
            detail="Browser/hub tooling may block or flag http:// resources.",
            fix="Replace http:// links with https://.",
        )]
    return []


def ch_card_sections(p: dict) -> list[Finding]:
    card = p.get("card") or ""
    missing = [s for s in ("## Model Details", "## Uses", "## Limitations") if s.lower() not in card.lower()]
    if len(missing) <= 1:
        return []
    return [Finding(
        id="CARD_SECTIONS", severity="info",
        title="Model card missing key sections",
        detail=f"Missing: {', '.join(missing)}. A complete card has details, uses, and limitations.",
        fix="Follow the Hub model-card template.",
    )]

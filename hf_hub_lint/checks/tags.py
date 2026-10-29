"""Tag checks."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding, _meta


def ch_tags(p: dict) -> list[Finding]:
    tags = _meta(p).get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    if len(tags) >= 3:
        return []
    return [Finding(
        id="TAGS_MIN", severity="info",
        title="Fewer than 3 tags",
        detail=f"Only {len(tags)} tag(s) set. Tags drive Hub search/discoverability.",
        fix="Add descriptive tags (framework, modality, task, language) in the Hub settings.",
    )]

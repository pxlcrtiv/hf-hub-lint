"""Dataset-scoped metadata checks."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding, _fm, _meta


def ch_datasets(p: dict) -> list[Finding]:
    fm = _fm(p)
    datasets = fm.get("datasets") or _meta(p).get("datasets") or []
    if datasets:
        return []
    return [Finding(
        id="DATASETS_FIELD", severity="info",
        title="No datasets listed",
        detail="Training/eval data not referenced; hurts reproducibility trust.",
        fix="Add 'datasets: [org/name]' to the frontmatter.",
    )]

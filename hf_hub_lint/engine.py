"""Lint engine: run applicable checks over a payload, score, and bucket findings."""

from __future__ import annotations

from dataclasses import dataclass, field

from hf_hub_lint.checks import Finding, applicable_checks, parse_card

SEVERITY_WEIGHT = {"error": 1.0, "warn": 0.5, "info": 0.0}
BANDS = [(90, "A (excellent)"), (75, "B (good)"), (60, "C (needs work)"), (0, "D (poor)")]


@dataclass
class LintResult:
    repo_id: str
    repo_type: str
    findings: list[Finding] = field(default_factory=list)
    score: float = 100.0
    band: str = "A (excellent)"
    errors: int = 0
    warnings: int = 0
    infos: int = 0

    def by_severity(self, severity: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def summary(self) -> str:
        return (
            f"{self.repo_id} ({self.repo_type}): score {self.score:.0f}/100 — "
            f"{self.errors} error(s), {self.warnings} warning(s), {self.infos} info"
        )


def lint_payload(payload: dict) -> LintResult:
    """Run all applicable checks; payloads come from HubClient.normalize()
    or from a fixture file (same shape)."""
    payload = dict(payload)
    payload["frontmatter"] = parse_card(payload.get("card"))

    repo_type = payload.get("type", "model")
    result = LintResult(repo_id=payload.get("repo_id", "?"), repo_type=repo_type)
    findings: list[Finding] = []
    for check in applicable_checks(repo_type):
        got = check.run(payload)
        if got:
            findings.extend(got)

    # Dedupe by (id, severity) — a check may legitimately fire variations.
    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for f in findings:
        key = (f.id, f.severity)
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    # Order: severity desc, then id asc (deterministic).
    order = {"error": 0, "warn": 1, "info": 2}
    unique.sort(key=lambda f: (order.get(f.severity, 3), f.id))

    result.findings = unique
    result.errors = sum(1 for f in unique if f.severity == "error")
    result.warnings = sum(1 for f in unique if f.severity == "warn")
    result.infos = sum(1 for f in unique if f.severity == "info")

    if unique:
        # Weighted penalty: 100 − Σ(weight × 12) per finding, floor 5.
        penalty = sum(SEVERITY_WEIGHT[f.severity] for f in unique) * 12
        result.score = max(5.0, 100.0 - penalty)
    result.score = round(result.score, 1)
    result.band = next(b for cutoff, b in BANDS if result.score >= cutoff)
    return result
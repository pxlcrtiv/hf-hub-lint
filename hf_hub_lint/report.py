"""Report rendering: plain text, markdown, JSON."""

from __future__ import annotations

import json

from hf_hub_lint.engine import LintResult

SEV_LABEL = {"error": "ERROR", "warn": "WARN", "info": "info"}


def render_text(result: LintResult) -> str:
    lines = [f"hf-hub-lint · {result.repo_id} ({result.repo_type})", f"Score: {result.score:.0f}/100 — band {result.band}", ""]
    if not result.findings:
        lines.append("No findings — clean bill of health.")
        return "\n".join(lines)
    for f in result.findings:
        lines.append(f"[{SEV_LABEL[f.severity]}] {f.id}: {f.title}")
        if f.detail:
            lines.append(f"    {f.detail}")
        if f.fix and f.fix != "-":
            lines.append(f"    fix: {f.fix}")
    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def render_markdown(result: LintResult) -> str:
    lines = [
        f"# hf-hub-lint report — `{result.repo_id}`",
        "",
        f"- **Type:** {result.repo_type}",
        f"- **Score:** {result.score:.0f}/100 — band **{result.band}**",
        f"- **Findings:** {result.errors} error(s), {result.warnings} warning(s), {result.infos} info",
        "",
        "| Severity | ID | Finding | Detail | Fix |",
        "| --- | --- | --- | --- | --- |",
    ]
    for f in result.findings:
        lines.append(f"| {f.severity} | `{f.id}` | {f.title} | {f.detail} | {f.fix} |")
    return "\n".join(lines)


def render_json(result: LintResult) -> str:
    return json.dumps(
        {
            "repo_id": result.repo_id,
            "type": result.repo_type,
            "score": result.score,
            "band": result.band,
            "counts": {"errors": result.errors, "warnings": result.warnings, "infos": result.infos},
            "findings": [
                {"id": f.id, "severity": f.severity, "title": f.title, "detail": f.detail, "fix": f.fix}
                for f in result.findings
            ],
        },
        indent=2,
    )
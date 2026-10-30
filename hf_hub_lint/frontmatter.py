"""Frontmatter parser for Hugging Face Hub model-card README files.

Public surface
--------------
- FrontmatterParseResult : dataclass adapter returned by ``parse_card``.
- parse_card(card)       : high-level entry point → FrontmatterParseResult.
- _yaml_block(text)      : extract raw YAML block between ``---`` delimiters.
- _simple_yaml(text)     : minimal YAML-subset parser → dict.

All parsing is pure, deterministic, and performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FrontmatterParseResult:
    """Structured result of a frontmatter parse attempt."""

    data: dict = field(default_factory=dict)
    raw_block: str = ""
    success: bool = False
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _yaml_block(text: str) -> str:
    """Return the YAML frontmatter block (between leading --- lines), or ''."""
    if not text:
        return ""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return ""


def _simple_yaml(text: str) -> dict:
    """Minimal YAML-subset parser: top-level `key: value` / `key: [a, b]`."""
    out: dict[str, object] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-")):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().strip('"\'')
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = (
                [v.strip().strip('"\'') for v in inner.split(",")] if inner else []
            )
        elif val in {"true", "false"}:
            out[key] = val == "true"
        elif val:
            out[key] = val.strip('"\'')
        else:
            out[key] = None
    return out


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------

def parse_card(card: str | None) -> FrontmatterParseResult:
    """Parse frontmatter from card text into a FrontmatterParseResult.

    Returns a result with ``success=True`` when a YAML block is found and
    parsed, or ``success=False`` with an explanatory error otherwise.
    """
    if not card:
        return FrontmatterParseResult(
            success=False,
            errors=["card text is empty"],
        )

    block = _yaml_block(card)
    if not block.strip():
        return FrontmatterParseResult(
            success=False,
            raw_block="",
            errors=["no frontmatter block found"],
        )

    data = _simple_yaml(block)
    return FrontmatterParseResult(
        data=data,
        raw_block=block,
        success=True,
        errors=[],
    )

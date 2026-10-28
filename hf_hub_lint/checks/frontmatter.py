"""Frontmatter parsing for model cards."""

from __future__ import annotations

FRONTMATTER_KEYS = {"license", "tags", "datasets", "base_model", "metrics", "library_name", "language", "pipeline_tag", "sdk", "widget"}


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
            out[key] = [v.strip().strip('"\'') for v in inner.split(",")] if inner else []
        elif val in {"true", "false"}:
            out[key] = val == "true"
        elif val:
            out[key] = val.strip('"\'')
        else:
            out[key] = None
    return out


def parse_card(card: str | None) -> dict | None:
    """Parse frontmatter from card text into a dict (empty dict if none)."""
    block = _yaml_block(card or "")
    if not block.strip():
        return None
    return _simple_yaml(block)

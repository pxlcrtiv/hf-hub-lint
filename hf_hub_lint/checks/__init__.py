"""Check definitions.

Every check is a pure function over a normalized payload dict:

    payload = {
        "repo_id": str,
        "type": "model" | "dataset" | "space",
        "card": str | None,            # README.md / model card text
        "frontmatter": dict | None,    # parsed YAML-ish card metadata
        "meta": dict | None,           # HF API metadata (tags, license, ...)
        "files": list[str] | None,     # file names at repo root
    }

Checks MUST be deterministic and MUST NOT do I/O (no network, no fs).
Findings carry (id, severity, title, detail, fix).

The concrete checks live in focused submodules (card, license, tags, model,
datasets, space) and the registry composes them. This package is the public
surface of the checks module.
"""

from hf_hub_lint.checks.base import Check, Finding
from hf_hub_lint.checks.frontmatter import parse_card
from hf_hub_lint.checks.registry import CHECKS, applicable_checks

__all__ = ["CHECKS", "Check", "Finding", "applicable_checks", "parse_card"]

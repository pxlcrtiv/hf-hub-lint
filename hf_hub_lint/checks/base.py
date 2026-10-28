"""Check vocabulary: findings, checks, and the payload accessors they share."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    id: str
    severity: str  # error | warn | info
    title: str
    detail: str = ""
    fix: str = ""
    applies_to: tuple[str, ...] = ("model", "dataset", "space")


@dataclass
class Check:
    id: str
    severity: str
    title: str
    applies_to: tuple[str, ...]
    run: callable  # (payload, meta_defaults) -> list[Finding] | None


def _fm(payload) -> dict:
    return payload.get("frontmatter") or {}


def _meta(payload) -> dict:
    return payload.get("meta") or {}

"""License checks."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding, _fm, _meta

KNOWN_LICENSES = {
    "apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause", "cc0-1.0", "cc-by-4.0",
    "cc-by-sa-4.0", "cc-by-nc-4.0", "cc-by-nc-sa-4.0", "gpl-2.0", "gpl-3.0",
    "lgpl-2.1", "lgpl-3.0", "agpl-3.0", "mpl-2.0", "other", "unknown",
    "unlicense", "openrail", "bigscience-openrail-m", "bigcode-openrail-m",
    "openrail++", "creativeml-openrail-m", "deepfloyd-if-license", "bsl-1.0",
    "llama2", "llama3", "llama3.1", "llama3.2", "gemma", "gemma2", "gemma3",
    "qwen", "qwen2", "qwen2.5", "microsoft-research-license", "fair", "falcon-180b",
}


def ch_license(p: dict) -> list[Finding]:
    meta = _meta(p)
    fm = _fm(p)
    license_val = meta.get("license") or fm.get("license") or ""
    if isinstance(license_val, list):
        license_val = license_val[0] if license_val else ""
    if license_val:
        if str(license_val).strip().lower() not in KNOWN_LICENSES:
            return [Finding(
                id="LICENSE_UNKNOWN", severity="warn",
                title="Unrecognized license identifier",
                detail=f"license={license_val!r} is not a known Hub license id.",
                fix="Use a Hub license id (apache-2.0, mit, cc-by-4.0, ...) or 'other'.",
            )]
        return []
    return [Finding(
        id="LICENSE_MISSING", severity="error",
        title="No license declared",
        detail="Neither the API metadata nor the card frontmatter declares a license.",
        fix="Add 'license: <id>' to the frontmatter, or set it in the Hub repo settings.",
    )]

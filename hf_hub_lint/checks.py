"""Check definitions.

Every check is a pure function over a normalized payload dict:

    payload = {
        "repo_id": str,
        "type": "model" | "dataset" | "space",
        "card": str | None,            # README.md / model card text
        "frontmatter": FrontmatterParseResult,  # single parse of the card
        "meta": dict | None,           # HF API metadata (tags, license, ...)
        "files": list[str] | None,     # file names at repo root
    }

Checks MUST be deterministic and MUST NOT do I/O (no network, no fs).
Findings carry (id, severity, title, detail, fix).

Public interface
----------------
run_checks(payload, repo_type) -> list[Finding]
    Dispatch every check applicable to ``repo_type``, collect their findings,
    dedupe by (id, severity), sort by severity desc then id asc, and return.

A finding's id/severity/title is the SINGLE SOURCE OF TRUTH: it is authored
by the check that produces it, and no registry entry holds a separate copy
that can drift (the old Check.id/severity/title were deleted).

Fields removed after the refactor
---------------------------------
- Check.id / Check.severity / Check.title: no longer stored on the registry
  entry; each finding carries its own (single-sourced) id/severity/title.
- Finding.applies_to: no longer used; dispatch is resolved by the Check
  registry's applies_to, so a per-finding applies_to is dead surface.
"""

from __future__ import annotations

from dataclasses import dataclass

from hf_hub_lint.frontmatter import FrontmatterParseResult

# Recognized repository types on the Hub.
VALID_SPACE_SDKS = {"streamlit", "gradio", "static", "docker", "custom"}
KNOWN_LIBRARIES = {
    "transformers", "peft", "diffusers", "timm", "sentence-transformers",
    "spacy", "fastai", "keras", "ctransformers", "mlx", "open_clip", "stable-baselines3",
}
KNOWN_LICENSES = {
    "apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause", "cc0-1.0", "cc-by-4.0",
    "cc-by-sa-4.0", "cc-by-nc-4.0", "cc-by-nc-sa-4.0", "gpl-2.0", "gpl-3.0",
    "lgpl-2.1", "lgpl-3.0", "agpl-3.0", "mpl-2.0", "other", "unknown",
    "unlicense", "openrail", "bigscience-openrail-m", "bigcode-openrail-m",
    "openrail++", "creativeml-openrail-m", "deepfloyd-if-license", "bsl-1.0", "llama2", "llama3", "llama3.1", "llama3.2", "gemma", "gemma2", "gemma3",
    "qwen", "qwen2", "qwen2.5", "microsoft-research-license", "fair", "falcon-180b",
}
FRONTMATTER_KEYS = {"license", "tags", "datasets", "base_model", "metrics", "library_name", "language", "pipeline_tag", "sdk", "widget"}


@dataclass
class Finding:
    id: str
    severity: str  # error | warn | info
    title: str
    detail: str = ""
    fix: str = ""


@dataclass
class Check:
    applies_to: tuple[str, ...]
    run: callable  # (payload) -> list[Finding] | None


def _fm(payload) -> dict:
    """Read parsed metadata from the single frontmatter result in the payload."""
    result = payload.get("frontmatter")
    if isinstance(result, FrontmatterParseResult):
        return result.data
    return result or {}


def _meta(payload) -> dict:
    return payload.get("meta") or {}


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

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
    """Report frontmatter problems from the engine's single parse result."""
    result = p.get("frontmatter")
    if isinstance(result, FrontmatterParseResult):
        if result.success:
            return []
        errors = list(result.errors)
    else:
        errors = []
        if result:  # tolerate a pre-parsed dict passed directly to the check
            return []
    detail = (
        "The Hub renders structured metadata (license, tags, metrics) from the card's frontmatter block."
    )
    if errors:
        detail += " " + "; ".join(errors) + "."
    return [Finding(
        id="FRONTMATTER", severity="warn",
        title="No YAML frontmatter in the card",
        detail=detail,
        fix="Start README.md with a --- delimited block of key: value pairs.",
    )]


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


def ch_library(p: dict) -> list[Finding]:
    if p.get("type") != "model":
        return []
    lib = _meta(p).get("library_name") or _fm(p).get("library_name") or ""
    if not lib:
        return [Finding(
            id="LIBRARY_NAME", severity="warn",
            title="library_name not set",
            detail="The Hub can't auto-load the model (transformers, diffusers, ...) without this.",
            fix="Set library_name in the API metadata or frontmatter.",
        )]
    if str(lib) not in KNOWN_LIBRARIES:
        return [Finding(
            id="LIBRARY_UNKNOWN", severity="info",
            title=f"Unusual library_name={lib!r}",
            detail="Not in the common set; if it is a real framework, ignore.",
            fix="-",
        )]
    return []


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


def ch_base_model(p: dict) -> list[Finding]:
    if p.get("type") != "model":
        return []
    base = _fm(p).get("base_model")
    if base:
        return []
    return [Finding(
        id="BASE_MODEL", severity="info",
        title="base_model not declared",
        detail="For fine-tuned models, the base model matters for licensing and reproduction.",
        fix="Add 'base_model: org/model' to the frontmatter.",
    )]


def ch_metrics(p: dict) -> list[Finding]:
    if p.get("type") != "model":
        return []
    metrics = _fm(p).get("metrics") or _meta(p).get("metrics") or []
    if metrics:
        return []
    return [Finding(
        id="METRICS", severity="info",
        title="No evaluation metrics",
        detail="A model without stated metrics can't be compared.",
        fix="Add a metrics list (accuracy, F1, perplexity, ...) + eval values in the card.",
    )]


def ch_config_json(p: dict) -> list[Finding]:
    if p.get("type") != "model":
        return []
    files = p.get("files") or []
    if "config.json" not in files:
        return [Finding(
            id="CONFIG_JSON", severity="warn",
            title="config.json missing",
            detail="Transformers/diffusers loaders expect config.json at the repo root.",
            fix="Push a valid config.json (or run save_pretrained()).",
        )]
    return []


def ch_space_sdk(p: dict) -> list[Finding]:
    if p.get("type") != "space":
        return []
    sdk = _fm(p).get("sdk") or _meta(p).get("sdk") or ""
    if sdk in VALID_SPACE_SDKS:
        return []
    if sdk:
        return [Finding(
            id="SDK_UNKNOWN", severity="error",
            title=f"Unknown Space SDK: {sdk!r}",
            detail="The Hub won't build the Space with an unrecognized SDK.",
            fix="Use one of: streamlit, gradio, static, docker, custom.",
        )]
    return [Finding(
        id="SDK_MISSING", severity="error",
        title="Space SDK not declared",
        detail="The Hub needs to know how to run the app.",
        fix="Add 'sdk: streamlit' (or gradio/static/docker) to the frontmatter.",
    )]


def ch_pipeline_tag(p: dict) -> list[Finding]:
    if p.get("type") != "model":
        return []
    tag = _meta(p).get("pipeline_tag") or _fm(p).get("pipeline_tag") or ""
    if tag:
        return []
    return [Finding(
        id="PIPELINE_TAG", severity="warn",
        title="pipeline_tag not set",
        detail="Without it the Hub can't offer the 'Deploy' / inference widgets.",
        fix="Set pipeline_tag (text-classification, text-generation, ...).",
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
    if p.get("type") not in ("model", "dataset"):
        return []
    missing = [s for s in ("## Model Details", "## Uses", "## Limitations") if s.lower() not in card.lower()]
    if len(missing) <= 1:
        return []
    return [Finding(
        id="CARD_SECTIONS", severity="info",
        title="Model card missing key sections",
        detail=f"Missing: {', '.join(missing)}. A complete card has details, uses, and limitations.",
        fix="Follow the Hub model-card template.",
    )]


CHECKS: list[Check] = [
    Check(applies_to=("model", "dataset", "space"), run=ch_card_present),
    Check(applies_to=("model", "dataset", "space"), run=ch_card_length),
    Check(applies_to=("model", "dataset", "space"), run=ch_frontmatter),
    Check(applies_to=("model", "dataset", "space"), run=ch_license),
    Check(applies_to=("model", "dataset", "space"), run=ch_tags),
    Check(applies_to=("model",), run=ch_library),
    Check(applies_to=("model", "dataset"), run=ch_datasets),
    Check(applies_to=("model",), run=ch_base_model),
    Check(applies_to=("model",), run=ch_metrics),
    Check(applies_to=("model",), run=ch_config_json),
    Check(applies_to=("space",), run=ch_space_sdk),
    Check(applies_to=("model",), run=ch_pipeline_tag),
    Check(applies_to=("model", "dataset", "space"), run=ch_http_links),
    Check(applies_to=("model", "dataset"), run=ch_card_sections),
]


def run_checks(payload: dict, repo_type: str) -> list[Finding]:
    """Run every check applicable to ``repo_type`` and return its findings.

    The single interface for the checks module. It:
      1. dispatches each check to those whose ``applies_to`` covers ``repo_type``,
      2. runs the check body against the payload,
      3. dedupe findings by (id, severity),
      4. sorts by severity (error < warn < info) then id ascending,
      5. returns the resulting list of Findings.

    The Finding's id/severity/title is the single source of truth (defined in
    the check body, not duplicated in a registry entry).
    """
    findings: list[Finding] = []
    for check in CHECKS:
        if repo_type in check.applies_to:
            got = check.run(payload)
            if got:
                findings.extend(got)

    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for f in findings:
        key = (f.id, f.severity)
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    order = {"error": 0, "warn": 1, "info": 2}
    unique.sort(key=lambda f: (order.get(f.severity, 3), f.id))
    return unique

"""Model-scoped metadata checks."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding, _fm, _meta

KNOWN_LIBRARIES = {
    "transformers", "peft", "diffusers", "timm", "sentence-transformers",
    "spacy", "fastai", "keras", "ctransformers", "mlx", "open_clip", "stable-baselines3",
}


def ch_library(p: dict) -> list[Finding]:
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


def ch_base_model(p: dict) -> list[Finding]:
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
    files = p.get("files") or []
    if "config.json" not in files:
        return [Finding(
            id="CONFIG_JSON", severity="warn",
            title="config.json missing",
            detail="Transformers/diffusers loaders expect config.json at the repo root.",
            fix="Push a valid config.json (or run save_pretrained()).",
        )]
    return []


def ch_pipeline_tag(p: dict) -> list[Finding]:
    tag = _meta(p).get("pipeline_tag") or _fm(p).get("pipeline_tag") or ""
    if tag:
        return []
    return [Finding(
        id="PIPELINE_TAG", severity="warn",
        title="pipeline_tag not set",
        detail="Without it the Hub can't offer the 'Deploy' / inference widgets.",
        fix="Set pipeline_tag (text-classification, text-generation, ...).",
    )]

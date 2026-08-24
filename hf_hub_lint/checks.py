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
"""

from __future__ import annotations

from dataclasses import dataclass

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
    "openrail++", "creativeml-openrail-m", "deepfloyd-if-license", "bsl-1.0",
    "llama2", "llama3", "llama3.1", "llama3.2", "gemma", "gemma2", "gemma3",
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
    if _yaml_block(p.get("card") or "").strip():
        return []
    return [Finding(
        id="FRONTMATTER", severity="warn",
        title="No YAML frontmatter in the card",
        detail="The Hub renders structured metadata (license, tags, metrics) from the card's frontmatter block.",
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
    Check("CARD_MISSING", "error", "Model card present", ("model", "dataset", "space"), ch_card_present),
    Check("CARD_TRIM", "info", "Card not a stub", ("model", "dataset", "space"), ch_card_length),
    Check("FRONTMATTER", "warn", "Structured metadata", ("model", "dataset", "space"), ch_frontmatter),
    Check("LICENSE", "error", "License declared", ("model", "dataset", "space"), ch_license),
    Check("TAGS_MIN", "info", "Discoverable tags", ("model", "dataset", "space"), ch_tags),
    Check("LIBRARY_NAME", "warn", "library_name", ("model",), ch_library),
    Check("DATASETS_FIELD", "info", "Datasets referenced", ("model", "dataset"), ch_datasets),
    Check("BASE_MODEL", "info", "base_model declared", ("model",), ch_base_model),
    Check("METRICS", "info", "Evaluation metrics", ("model",), ch_metrics),
    Check("CONFIG_JSON", "warn", "config.json present", ("model",), ch_config_json),
    Check("SPACE_SDK", "error", "Space SDK declared", ("space",), ch_space_sdk),
    Check("PIPELINE_TAG", "warn", "pipeline_tag set", ("model",), ch_pipeline_tag),
    Check("INSECURE_URL", "warn", "No plain-HTTP links", ("model", "dataset", "space"), ch_http_links),
    Check("CARD_SECTIONS", "info", "Card sections complete", ("model", "dataset"), ch_card_sections),
]


def applicable_checks(repo_type: str) -> list[Check]:
    return [c for c in CHECKS if repo_type in c.applies_to]


def parse_card(card: str | None) -> dict | None:
    """Parse frontmatter from card text into a dict (empty dict if none)."""
    block = _yaml_block(card or "")
    if not block.strip():
        return None
    return _simple_yaml(block)
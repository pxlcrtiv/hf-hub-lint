"""The check registry: ordered CHECKS by finding id, filtered by repo type."""

from __future__ import annotations

from hf_hub_lint.checks.base import Check
from hf_hub_lint.checks.card import (
    ch_card_length,
    ch_card_present,
    ch_card_sections,
    ch_frontmatter,
    ch_http_links,
)
from hf_hub_lint.checks.datasets import ch_datasets
from hf_hub_lint.checks.license import ch_license
from hf_hub_lint.checks.model import (
    ch_base_model,
    ch_config_json,
    ch_library,
    ch_metrics,
    ch_pipeline_tag,
)
from hf_hub_lint.checks.space import ch_space_sdk
from hf_hub_lint.checks.tags import ch_tags

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

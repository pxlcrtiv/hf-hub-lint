"""Space-scoped checks."""

from __future__ import annotations

from hf_hub_lint.checks.base import Finding, _fm, _meta

VALID_SPACE_SDKS = {"streamlit", "gradio", "static", "docker", "custom"}


def ch_space_sdk(p: dict) -> list[Finding]:
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

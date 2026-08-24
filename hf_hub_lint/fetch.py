"""Hub API access — small, injectable, and fully optional.

The engine only ever sees the normalized payload dict produced here.
`HubClient` talks to the PUBLIC Hub API (no token). Every network call has a
short timeout; any failure raises FetchError, which the CLI reports cleanly.
Tests substitute a FakeClient, so the whole suite stays offline.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

API = "https://huggingface.co/api"
RAW = "https://huggingface.co"
TIMEOUT = 15


class FetchError(Exception):
    """Raised when the Hub is unreachable or the repo is not public."""


class HubClient:
    def __init__(self, api: str = API, raw: str = RAW, timeout: int = TIMEOUT) -> None:
        self.api = api
        self.raw = raw
        self.timeout = timeout

    def _get(self, url: str) -> str:
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise FetchError(f"{url}: gated/private repo (401) — public repos only") from e
            if e.code == 404:
                raise FetchError(f"{url}: not found (404)") from e
            raise FetchError(f"{url}: HTTP {e.code}") from e
        except OSError as e:
            raise FetchError(f"{url}: {e}") from e

    def normalize(self, repo_id: str) -> dict[str, Any]:
        """Fetch + normalize a Hub repo into the payload the checks consume."""
        meta_raw = self._get(f"{self.api}/models/{repo_id}")
        meta: dict[str, Any] = json.loads(meta_raw)
        repo_type = "model"
        if "modelId" not in meta and "sdk" in meta:
            repo_type = "space"
        # datasets expose `id` + `tags`; models expose `modelId`.
        if "modelId" not in meta and "dataset" in str(meta.get("tags", "")).lower():
            repo_type = "dataset"
        try:
            card = self._get(f"{self.raw}/{repo_id}/raw/main/README.md")
        except FetchError:
            card = None
        files: list[str] = []
        try:
            tree = json.loads(self._get(f"{self.api}/{repo_type}s/{repo_id}/tree/main?recursive=false"))
            files = [f.get("path", "") for f in tree if isinstance(f, dict)]
        except (FetchError, json.JSONDecodeError):
            try:
                if self._get(f"{self.raw}/{repo_id}/raw/main/config.json"):
                    files.append("config.json")
            except FetchError:
                pass
        return {
            "repo_id": repo_id,
            "type": repo_type,
            "card": card,
            "frontmatter": None,  # filled by engine via checks.parse_card
            "meta": meta,
            "files": files,
        }
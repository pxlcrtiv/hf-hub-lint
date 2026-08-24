"""CLI: hf-hub-lint <repo_id> [options]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hf_hub_lint import __version__
from hf_hub_lint.engine import lint_payload
from hf_hub_lint.fetch import FetchError, HubClient
from hf_hub_lint.report import render_json, render_markdown, render_text


def _load_fixture(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        data = data[0]  # fixture gallery: take the first unless --index given
    return data


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hf-hub-lint",
        description="Lint Hugging Face Hub repositories (models, datasets, spaces): "
        "card completeness, license, metadata hygiene, config sanity. "
        "Deterministic checks; zero API keys.",
    )
    p.add_argument("repo_id", nargs="?", help="Hub repo id, e.g. MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
    p.add_argument("--fixture", metavar="PATH", help="Lint a local fixture JSON instead of the live Hub (offline mode)")
    p.add_argument("--type", choices=["model", "dataset", "space"], help="Force repo type (fixture mode)")
    p.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    p.add_argument("-o", "--output", metavar="PATH", help="Write report to a file (default: stdout)")
    p.add_argument("--strict", action="store_true", help="Exit 1 when any error-level finding exists")
    p.add_argument("--version", action="version", version=f"hf-hub-lint {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.repo_id and not args.fixture:
        print("error: pass a repo id (hf-hub-lint org/repo) or --fixture PATH", file=sys.stderr)
        return 2

    try:
        if args.fixture:
            payload = _load_fixture(args.fixture)
            if args.type:
                payload["type"] = args.type
            payload.setdefault("repo_id", Path(args.fixture).stem)
            payload.setdefault("card", "")
            payload.setdefault("meta", {})
            payload.setdefault("files", [])
            src = f"fixture:{args.fixture}"
        else:
            payload = HubClient().normalize(args.repo_id)
            src = f"hub:{payload['repo_id']}"
    except FetchError as e:
        print(f"error: could not fetch repo — {e}", file=sys.stderr)
        print("tip: use --fixture to lint offline, or check the repo is public.", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(f"error: bad fixture or API response — {e}", file=sys.stderr)
        return 1

    result = lint_payload(payload)

    rendered = {"text": render_text, "markdown": render_markdown, "json": render_json}[args.format](result)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n", encoding="utf-8")
        print(f"report written to {out} (source: {src})")
        print(result.summary())
    else:
        sys.stdout.write(rendered.rstrip() + "\n")

    if args.strict and result.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
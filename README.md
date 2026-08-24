# hf-hub-lint

[![CI](https://img.shields.io/github/actions/workflow/status/pxlcrtiv/hf-hub-lint/ci.yml?branch=main&label=CI)](https://github.com/pxlcrtiv/hf-hub-lint/actions)
[![License](https://img.shields.io/github/license/pxlcrtiv/hf-hub-lint)](LICENSE)
[![Stars](https://img.shields.io/github/stars/pxlcrtiv/hf-hub-lint)](https://github.com/pxlcrtiv/hf-hub-lint/stargazers)
[![Forks](https://img.shields.io/github/forks/pxlcrtiv/hf-hub-lint)](https://github.com/pxlcrtiv/hf-hub-lint/forks)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

**Lint Hugging Face Hub repositories the way you lint code.** `hf-hub-lint` runs
deterministic checks over a Hub repo — model card completeness, license
declaration, metadata hygiene, config sanity — and prints a weighted score
(0–100) with an actionable fix for every finding.

Zero runtime dependencies. Zero API keys. Works on the live public Hub, or
fully offline against a fixture.

## Problem

- 🚨 Repos with no license are legally unusable for most teams — and it's the
  #1 blocker reviewers hit.
- 🎭 A model card with no metrics, no base model, and no datasets is a
  trust-killer for recruiters and users.
- 🤷 The Hub's own UI hides metadata problems instead of surfacing them.

## Solution

One command turns a repo into a checklist:

```text
$ hf-hub-lint acme/starter-model
hf-hub-lint · acme/starter-model (model)
Score: 94/100 — band A (excellent)

[WARN] INSECURE_URL: Plain-HTTP link(s) found in the card
    Browser/hub tooling may block or flag http:// resources.
    fix: Replace http:// links with https://.
[info] BASE_MODEL: base_model not declared
    For fine-tuned models, the base model matters for licensing and reproduction.
    fix: Add 'base_model: org/model' to the frontmatter.
[info] METRICS: No evaluation metrics
    A model without stated metrics can't be compared.
    fix: Add a metrics list (accuracy, F1, perplexity, ...) + eval values in the card.
```

## Checks

| ID | Severity | Applies to | What it verifies |
| --- | --- | --- | --- |
| `CARD_MISSING` | error | model · dataset · space | README.md present and ≥40 chars |
| `CARD_TRIM` | info | all | Card isn't a stub (<250 chars) |
| `FRONTMATTER` | warn | all | YAML frontmatter block present |
| `LICENSE` | error | all | License declared (meta or card) & recognized |
| `TAGS_MIN` | info | all | ≥3 tags for discoverability |
| `LIBRARY_NAME` | warn | model | Framework declared for auto-loading |
| `DATASETS_FIELD` | info | model · dataset | Training data referenced |
| `BASE_MODEL` | info | model | Base model declared (fine-tunes) |
| `METRICS` | info | model | Evaluation metrics declared |
| `CONFIG_JSON` | warn | model | config.json at repo root |
| `SPACE_SDK` | error | space | sdk ∈ streamlit/gradio/static/docker/custom |
| `PIPELINE_TAG` | warn | model | pipeline_tag set (widgets/Deploy) |
| `INSECURE_URL` | warn | all | No plain-`http://` links |
| `CARD_SECTIONS` | info | model · dataset | Model Details / Uses / Limitations present |

**Score:** `100 − Σ(severity weight × 12)` where error=1.0, warn=0.5, info=0.0;
floor 5, bands A ≥90, B ≥75, C ≥60, D <60.

## Quickstart

```bash
pip install -e .          # or: pip install -r requirements.txt && pip install -e .
# live Hub (public repos, no token):
hf-hub-lint MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli
# offline fixture (demo / CI / air-gapped):
hf-hub-lint --fixture hf_hub_lint/data/fixtures/fixture_model.json
# reports:
hf-hub-lint org/model --format markdown -o report.md
hf-hub-lint org/model --format json -o report.json
# CI gate (exit 1 on any error-level finding):
hf-hub-lint org/model --strict
```

### Real run — live Hub (2026-08-24)

```text
$ hf-hub-lint MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli --format json
score 100.0, band A (excellent), 0 errors, 0 warnings, 4 info
  info BASE_MODEL     - base_model not declared
  info CARD_SECTIONS  - Model card missing key sections
  info DATASETS_FIELD - No datasets listed
  info METRICS        - No evaluation metrics
```

A genuinely excellent card gets a perfect score; the infos are even honest —
that repo *is* missing explicit metrics and base_model fields.

### Real run — fixture dataset (offline)

```text
$ hf-hub-lint --fixture hf_hub_lint/data/fixtures/fixture_dataset.json --strict
acme/raw-scrape (dataset): score 82/100 — 1 error(s), 1 warning(s), 4 info
# exit code 1 in --strict: LICENSE_MISSING is an error
```

Sample report: [examples/demo-report.md](examples/demo-report.md)

## Project layout

```text
hf_hub_lint/
  checks.py    # 14 pure, deterministic check functions (no I/O)
  fetch.py     # injectable public-Hub client (urllib only)
  engine.py    # scoring + severity ordering
  report.py    # text / markdown / JSON renderers
  cli.py       # argparse CLI
  data/fixtures/  # model, dataset, space fixtures (offline demos + tests)
tests/         # 20 offline tests, zero network
scripts/       # daily_update.py (Daily Green) + tips_pool.json
```

Design rules: checks are pure functions over one payload dict, findings are
(actionable fix > description), output is deterministic, the suite never
touches the network, and the runtime has **zero dependencies** — `urllib` only.

## Daily Green automation

This repo commits one dated, non-empty entry per day via
`scripts/daily_update.py` (launchd 12:07+18:07 local → GH Actions 12:00 UTC →
catch-up backfill ≤14 days), rotating tips from `scripts/tips_pool.json`.
Pause: `touch .daily-pause`. Customize: edit the pool. See the script header.

## Caveats

- The score measures **metadata hygiene**, not model quality — treat it as a
  checklist, not a verdict.
- Live mode reads the public Hub (any public repo; gated/private repos are
  reported cleanly, not leaked). Rate limits apply to anonymous API usage.
- `--strict` exits 1 on error-level findings only (warnings don't fail CI).

## Sibling repos

Part of the [pxlcrtiv](https://github.com/pxlcrtiv) AI/ML × blockchain
portfolio: [slither-chat](https://github.com/pxlcrtiv/slither-chat) (audit
copilot), [model-ledger](https://github.com/pxlcrtiv/model-ledger) (on-chain
model provenance), [vector-scout](https://github.com/pxlcrtiv/vector-scout)
(semantic search), [inject-scout](https://github.com/pxlcrtiv/inject-scout)
(prompt-injection scanner), [chain-scout](https://github.com/pxlcrtiv/chain-scout).

## License

MIT — see [LICENSE](LICENSE). Contributions welcome: see [CONTRIBUTING](CONTRIBUTING.md).
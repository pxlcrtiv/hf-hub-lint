# Hub & model-card tips of the day

> Maintained by `scripts/daily_update.py` (Daily Green automation) — one
> dated, non-empty metadata tip per day, rotated from the pool in
> `scripts/tips_pool.json`. Pause by creating a `.daily-pause` file in the
> repo root, or unload the scheduler job (see README, Daily Green).


## 2026-08-24 — Tip of the day: License before code

A repo with no license is legally unusable for most companies. Set the license tag in Hub settings AND in the card frontmatter.

> `hf-hub-lint org/model --format markdown`


## 2026-08-25 — Tip of the day: Tags drive discoverability

Hub search, filters, and the Models/Datasets pages rank by tags. Aim for 5+ (framework, task, modality, language, license).


## 2026-08-26 — Tip of the day: frontmatter = structured metadata

YAML frontmatter in the card is parsed by the Hub into fields (license, tags, metrics) that APIs and widgets use. Keep keys lowercase.


## 2026-08-27 — Tip of the day: library_name unlocks auto-loading

Setting library_name (transformers, diffusers...) lets the Hub offer 'Use in Transformers' code snippets and auto-download.


## 2026-08-28 — Tip of the day: config.json is not optional

Gated loading, pipelines, and most frameworks require config.json with model_type. Always save_pretrained() it.


## 2026-08-29 — Tip of the day: State metrics or stay silent

A claimed accuracy with no eval set or methodology is worse than none. Report metric, dataset, and split together.


## 2026-08-30 — Tip of the day: base_model is a legal field now

Derivative models should declare base_model — licensing and attribution of fine-tunes depend on it.


## 2026-08-31 — Tip of the day: Datasets are part of reproducibility

Link the training data via the datasets field. It is the single biggest trust signal for ML repos.


## 2026-09-01 — Tip of the day: pipeline_tag == instant demo

Models with pipeline_tag render inference widgets on the Hub page — the fastest 'wow' for visitors.


## 2026-09-02 — Tip of the day: Spaces need an explicit SDK

sdk: streamlit | gradio | static | docker | custom in frontmatter; an unbuildable Space is a dead link.


## 2026-09-03 — Tip of the day: HTTPS or it didn't happen

Plain http:// links in cards get flagged by scanners and often blocked by corporate proxies. Force https.


## 2026-09-04 — Tip of the day: Lint before you publish

Run hf-hub-lint on a repo before sharing it — a 90+ score card takes 5 minutes and removes an obvious first impression problem.

> `hf-hub-lint --fixture examples/fixture_model.json`


## 2026-09-05 — Tip of the day: Gated repos still need cards

A gated model's card is public even when weights are not — reviewers decide whether to request access based on it.


## 2026-09-06 — Tip of the day: Deterministic linting scales

Script hf-hub-lint --json into CI so card regressions fail the build before they ship to the Hub.

> `hf-hub-lint org/model --format json`


## 2026-09-07 — Tip of the day: One model card template

Copy an excellent card (e.g. any top-100 model) and adapt it. The Sections check here flags what a template usually has.


## 2026-09-08 — Tip of the day: Inference widgets need examples

Add a widget example (sample input) to the card so the live widget shows real output on first load.


## 2026-09-09 — Tip of the day: Version your Hub repo

Use git tags on Hub repos; the API exposes them and downstream users pin versions.


## 2026-09-10 — Tip of the day: Dataset cards need provenance

Include collection method, date, and license of source data — the #1 review question for datasets.


## 2026-09-11 — Tip of the day: Keep README encoding sane

UTF-8, no BOM, LF endings. Broken encodings make the card render garbled on the Hub.


## 2026-09-12 — Tip of the day: Emoji are fine, noise is not

A banner emoji or two is OK; a wall of them hurts searchability and looks spammy to reviewers.


## 2026-09-13 — Tip of the day: CI-lint your own docs

Add the linter to a pre-commit hook; catch CARD_TRIM before your README becomes a stub.

> `pip install hf-hub-lint`


## 2026-09-14 — Tip of the day: The score is a heuristic

hf-hub-lint scores metadata hygiene, not model quality. Use it as a checklist, not a judgment of the artifact.


## 2026-09-15 — Tip of the day: Metadata debt compounds

Fix metadata when the repo is fresh; nobody retrofits a model card on a 2-year-old repo.

> `hf-hub-lint --strict org/model`


## 2026-09-16 — Tip of the day: Model cards are your front page

The README.md of a Hub repo renders before anything else — a card with Model Details, Uses, and Limitations sections converts viewers into users.

> `hf-hub-lint org/model`


## 2026-09-17 — Tip of the day: License before code

A repo with no license is legally unusable for most companies. Set the license tag in Hub settings AND in the card frontmatter.

> `hf-hub-lint org/model --format markdown`


## 2026-09-18 — Tip of the day: Tags drive discoverability

Hub search, filters, and the Models/Datasets pages rank by tags. Aim for 5+ (framework, task, modality, language, license).


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


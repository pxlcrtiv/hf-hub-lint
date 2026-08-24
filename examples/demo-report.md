# hf-hub-lint report — `acme/raw-scrape`

- **Type:** dataset
- **Score:** 82/100 — band **B (good)**
- **Findings:** 1 error(s), 1 warning(s), 4 info

| Severity | ID | Finding | Detail | Fix |
| --- | --- | --- | --- | --- |
| error | `LICENSE_MISSING` | No license declared | Neither the API metadata nor the card frontmatter declares a license. | Add 'license: <id>' to the frontmatter, or set it in the Hub repo settings. |
| warn | `FRONTMATTER` | No YAML frontmatter in the card | The Hub renders structured metadata (license, tags, metrics) from the card's frontmatter block. | Start README.md with a --- delimited block of key: value pairs. |
| info | `CARD_SECTIONS` | Model card missing key sections | Missing: ## Uses, ## Limitations. A complete card has details, uses, and limitations. | Follow the Hub model-card template. |
| info | `CARD_TRIM` | Model card is very short | README.md is only 98 chars — likely a stub. | Expand: description, intended use, training data, limitations, license. |
| info | `DATASETS_FIELD` | No datasets listed | Training/eval data not referenced; hurts reproducibility trust. | Add 'datasets: [org/name]' to the frontmatter. |
| info | `TAGS_MIN` | Fewer than 3 tags | Only 1 tag(s) set. Tags drive Hub search/discoverability. | Add descriptive tags (framework, modality, task, language) in the Hub settings. |

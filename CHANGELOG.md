# Changelog

All notable changes to hf-hub-lint are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] — 2026-08-24

### Added
- Initial release: `hf-hub-lint` CLI with 12 deterministic checks for Hugging
  Face Hub repositories (model cards, datasets, spaces).
- Online mode (public Hub API, no token) and offline `--fixture` mode.
- Weighted lint score (0–100), severity bands, markdown/JSON reports.
- `--strict` flag (non-zero exit on any error-level finding).
- 20-check built-in fixture gallery; 16 offline pytest suite; Daily Green
  automation (`scripts/daily_update.py` + 24-tip pool).
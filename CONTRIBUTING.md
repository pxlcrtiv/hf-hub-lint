# Contributing

Thanks for helping make hf-hub-lint better. This is a small, focused tool:
**deterministic, offline-testable, zero-runtime-dependencies** checks for
Hugging Face Hub repositories and model cards. Please keep those properties.

## Ground rules

- **No runtime dependencies.** New checks must work with the Python standard
  library. Network calls belong only behind the injectable fetch layer
  (`hf_hub_lint/fetch.py`) and must be optional at test time.
- **Deterministic output.** A check for the same payload must always produce
  the same finding. No timestamps, no randomness, no dictionary-ordering
  dependence in findings.
- **Every check needs a fixture case.** Add or extend a fixture in
  `hf_hub_lint/data/fixtures/` and a golden test in `tests/` that asserts the
  exact finding id + severity.
- **Tests stay offline.** `pytest` must pass with no network. Live-API tests
  are opt-in with `-m live`.
- **Match the score contract.** Changing scoring semantics needs a README
  update (the formula is documented) and golden-score updates in tests.

## Daily Green

The repo commits one dated entry per day via `scripts/daily_update.py`
(pool: `scripts/tips_pool.json`). Add tips to the pool; never edit
`docs/daily-tips.md` by hand.

## PR process

1. Fork, branch, change, test: `python -m pytest tests/ -q` (all green).
2. `ruff check` clean (`pip install ruff`).
3. CLI smoke: `hf-hub-lint --fixture examples/fixture_model.json`.
4. Open the PR; reference the check id(s) you added and the fixture used.

## Style

- Type hints on all public functions; `py3.10+`.
- Errors are actionable: each finding says what to fix, not just what is wrong.
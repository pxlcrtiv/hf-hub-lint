"""Offline test suite for hf-hub-lint — no network, deterministic."""

import json
from pathlib import Path

import pytest

from hf_hub_lint.checks import Finding, applicable_checks, parse_card
from hf_hub_lint.engine import lint_payload
from hf_hub_lint.report import render_json, render_markdown, render_text

FIX_DIR = Path(__file__).parent.parent / "hf_hub_lint" / "data" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIX_DIR / name).read_text(encoding="utf-8"))


def good_model() -> dict:
    return {
        "repo_id": "x/y",
        "type": "model",
        "card": "---\nlicense: mit\nlibrary_name: transformers\npipeline_tag: text-classification\nmetrics: [accuracy]\ndatasets: [imdb]\nbase_model: bert-base-uncased\ntags: [nlp, sentiment]\n---\n\n# Model\n\n" + "Detailed card. " * 40,
        "meta": {"license": "mit", "library_name": "transformers", "pipeline_tag": "text-classification", "tags": ["a", "b", "c"]},
        "files": ["README.md", "config.json"],
    }


# ---------------------------------------------------------------- checks


def test_fixture_model_finds_expected_issues():
    """The golden model fixture: no metrics, no base_model, plain-HTTP link."""
    res = lint_payload(load("fixture_model.json"))
    ids = {f.id for f in res.findings}
    assert {"METRICS", "BASE_MODEL", "INSECURE_URL", "DATASETS_FIELD"} <= ids
    assert "LICENSE_MISSING" not in ids
    assert "CARD_MISSING" not in ids
    assert res.errors == 0  # fixture is a *good* card with info-level gaps


def test_fixture_dataset_flags_missing_license():
    res = lint_payload(load("fixture_dataset.json"))
    assert any(f.id == "LICENSE_MISSING" and f.severity == "error" for f in res.findings)
    assert any(f.id == "CARD_SECTIONS" for f in res.findings)
    assert any(f.id == "FRONTMATTER" for f in res.findings)


def test_fixture_space_flags_bad_sdk():
    res = lint_payload(load("fixture_space.json"))
    assert any(f.id == "SDK_UNKNOWN" and f.severity == "error" for f in res.findings)
    # space checks only — model checks never run
    assert not any(f.id == "CONFIG_JSON" for f in res.findings)


def test_good_card_scores_high():
    res = lint_payload(good_model())
    assert res.errors == 0 and res.warnings == 0
    assert res.score >= 85


def test_missing_card_is_error():
    p = good_model()
    p["card"] = ""
    res = lint_payload(p)
    assert any(f.id == "CARD_MISSING" and f.severity == "error" for f in res.findings)


def test_license_unknown_warn():
    p = good_model()
    p["meta"]["license"] = "my-custom-license"
    res = lint_payload(p)
    assert any(f.id == "LICENSE_UNKNOWN" and f.severity == "warn" for f in res.findings)


def test_config_json_missing_flags_config():
    p = good_model()
    p["files"] = ["README.md"]
    res = lint_payload(p)
    assert any(f.id == "CONFIG_JSON" for f in res.findings)


def test_frontmatter_parse():
    card = "---\nlicense: mit\ntags: [a, b]\nmetrics: [accuracy]\n---\n\nBody"
    fm = parse_card(card)
    assert fm["license"] == "mit"
    assert fm["tags"] == ["a", "b"]
    assert fm["metrics"] == ["accuracy"]
    assert parse_card("no frontmatter here") is None


def test_check_determinism_and_order():
    p = load("fixture_model.json")
    r1, r2 = lint_payload(p), lint_payload(p)
    assert [f.id for f in r1.findings] == [f.id for f in r2.findings]
    # errors sort before warns before infos
    sevs = [f.severity for f in r1.findings]
    assert sevs == sorted(sevs, key={"error": 0, "warn": 1, "info": 2}.get)


def test_applicable_checks_by_type():
    model_ids = {c.id for c in applicable_checks("model")}
    space_ids = {c.id for c in applicable_checks("space")}
    assert "CONFIG_JSON" in model_ids and "SPACE_SDK" not in model_ids
    assert "SPACE_SDK" in space_ids and "CONFIG_JSON" not in space_ids


def test_score_floor_and_band():
    bad = good_model()
    bad["card"] = ""
    bad["meta"] = {"tags": []}
    res = lint_payload(bad)
    assert res.score >= 5.0
    assert res.score < 90
    assert res.band in {"B (good)", "C (needs work)", "D (poor)"}


# ---------------------------------------------------------------- reports


def test_renderers_contain_core_fields():
    res = lint_payload(load("fixture_model.json"))
    txt, md, js = render_text(res), render_markdown(res), render_json(res)
    assert "acme/starter-model" in txt and "Score:" in txt
    assert "| Severity | ID |" in md
    data = json.loads(js)
    assert data["repo_id"] == "acme/starter-model"
    assert {"score", "band", "counts", "findings"} <= set(data)


def test_clean_payload_no_findings():
    res = lint_payload(good_model())
    assert res.errors == 0 and res.warnings == 0
    # removing the license from BOTH meta and frontmatter must flag it
    p = good_model()
    del p["meta"]["license"]
    p["card"] = p["card"].replace("license: mit\n", "")
    res2 = lint_payload(p)
    assert any(f.id == "LICENSE_MISSING" for f in res2.findings)


def test_finding_dataclass_fields():
    f = Finding(id="X", severity="warn", title="t", detail="d", fix="f")
    assert f.applies_to == ("model", "dataset", "space")


# CLI (offline paths only)


def test_cli_fixture_text(capsys):
    from hf_hub_lint.cli import main

    rc = main(["--fixture", str(FIX_DIR / "fixture_model.json")])
    assert rc == 0
    assert "acme/starter-model" in capsys.readouterr().out


def test_cli_strict_exit_code(capsys):
    from hf_hub_lint.cli import main

    rc = main(["--fixture", str(FIX_DIR / "fixture_dataset.json"), "--strict"])
    assert rc == 1  # error-level finding present
    assert "LICENSE_MISSING" in capsys.readouterr().out


def test_cli_json_output(tmp_path):
    from hf_hub_lint.cli import main

    out = tmp_path / "r.json"
    rc = main(["--fixture", str(FIX_DIR / "fixture_model.json"), "--format", "json", "-o", str(out)])
    assert rc == 0
    data = json.loads(out.read_text())
    assert data["score"] >= 0


def test_cli_no_args_usage():
    from hf_hub_lint.cli import main

    assert main([]) == 2


def test_cli_missing_fixture():
    from hf_hub_lint.cli import main

    assert main(["--fixture", "/nonexistent.json"]) == 1


def test_cli_force_type():
    from hf_hub_lint.cli import main

    # A model payload forced to 'space' runs space checks only -> SDK finding.
    rc = main(["--fixture", str(FIX_DIR / "fixture_model.json"), "--type", "space"])
    assert rc == 0


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Guarantee the suite never touches the network."""
    from hf_hub_lint import fetch

    def boom(*a, **k):
        raise AssertionError("network access in tests")

    monkeypatch.setattr(fetch.HubClient, "_get", boom)
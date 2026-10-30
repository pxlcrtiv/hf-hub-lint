"""Direct edge-case tests for hf_hub_lint.frontmatter."""

from hf_hub_lint.frontmatter import (
    FrontmatterParseResult,
    _simple_yaml,
    _yaml_block,
    parse_card,
)

# ---------------------------------------------------------------------------
# _yaml_block
# ---------------------------------------------------------------------------

def test_yaml_block_basic():
    text = "---\nkey: val\n---\nBody"
    assert _yaml_block(text) == "key: val"


def test_yaml_block_no_frontmatter():
    assert _yaml_block("No frontmatter here") == ""


def test_yaml_block_empty_string():
    assert _yaml_block("") == ""


def test_yaml_block_only_opening_delim():
    """No closing --- → block not closed, return empty."""
    assert _yaml_block("---\nkey: val\nBody") == ""


def test_yaml_block_closing_at_end():
    text = "---\nkey: val\n---"
    assert _yaml_block(text) == "key: val"


def test_yaml_block_leading_blank_lines():
    """First non-blank line must be ---."""
    assert _yaml_block("\n\n---\nkey: val\n---") == ""


def test_yaml_block_multiple_blocks():
    """Only the first block is returned (first closing --- wins)."""
    text = "---\nkey: val1\n---\n---\nkey: val2\n---"
    assert _yaml_block(text) == "key: val1"


# ---------------------------------------------------------------------------
# _simple_yaml
# ---------------------------------------------------------------------------

def test_simple_yaml_basic_key_value():
    assert _simple_yaml("license: mit") == {"license": "mit"}


def test_simple_yaml_skips_comment_lines():
    assert _simple_yaml("# a comment\nlicense: mit") == {"license": "mit"}


def test_simple_yaml_skips_list_items():
    """Lines starting with '-' after stripping are ignored (not key: value)."""
    assert _simple_yaml("- item1\n- item2\nkey: val") == {"key": "val"}


def test_simple_yaml_empty_list_value():
    assert _simple_yaml("tags: []") == {"tags": []}


def test_simple_yaml_list_value():
    assert _simple_yaml("tags: [nlp, sentiment]") == {"tags": ["nlp", "sentiment"]}


def test_simple_yaml_list_with_quoted_items():
    assert _simple_yaml('tags: ["nlp", "sentiment"]') == {"tags": ["nlp", "sentiment"]}


def test_simple_yaml_boolean_true():
    assert _simple_yaml("debug: true") == {"debug": True}


def test_simple_yaml_boolean_false():
    assert _simple_yaml("debug: false") == {"debug": False}


def test_simple_yaml_empty_value_is_none():
    assert _simple_yaml("key:") == {"key": None}


def test_simple_yaml_strips_quotes_from_value():
    assert _simple_yaml('name: "hello world"') == {"name": "hello world"}
    assert _simple_yaml("name: 'hello world'") == {"name": "hello world"}


def test_simple_yaml_key_quotes_stripped():
    assert _simple_yaml('"quoted key": val') == {"quoted key": "val"}


def test_simple_yaml_no_colon_skipped():
    assert _simple_yaml("no-colon-line\nkey: val") == {"key": "val"}


def test_simple_yaml_empty_input():
    assert _simple_yaml("") == {}


def test_simple_yaml_whitespace_only():
    assert _simple_yaml("   \n\t\n") == {}


def test_simple_yaml_multiple_keys():
    text = "license: mit\ntags: [a, b]\npipeline_tag: text-classification"
    result = _simple_yaml(text)
    assert result["license"] == "mit"
    assert result["tags"] == ["a", "b"]
    assert result["pipeline_tag"] == "text-classification"


def test_simple_yaml_last_duplicate_key_wins():
    result = _simple_yaml("key: first\nkey: second")
    assert result["key"] == "second"


# ---------------------------------------------------------------------------
# parse_card
# ---------------------------------------------------------------------------

def test_parse_card_returns_failure_without_frontmatter():
    result = parse_card("Just a README body")
    assert result.success is False
    assert result.data == {}


def test_parse_card_returns_failure_for_none():
    result = parse_card(None)
    assert result.success is False
    assert result.data == {}


def test_parse_card_empty_string():
    result = parse_card("")
    assert result.success is False
    assert result.data == {}


def test_parse_card_basic():
    card = "---\nlicense: mit\ntags: [a, b]\n---\n\nBody"
    result = parse_card(card)
    assert result.success is True
    assert result.data == {"license": "mit", "tags": ["a", "b"]}


def test_parse_card_with_body_only():
    """Frontmatter block present; body after closing --- is ignored."""
    card = "---\nlicense: mit\n---\n\n# Model\n\nDetails here."
    result = parse_card(card)
    assert result.success is True
    assert result.data == {"license": "mit"}


# ---------------------------------------------------------------------------
# FrontmatterParseResult adapter
# ---------------------------------------------------------------------------

def test_frontmatter_parse_result_fields():
    r = FrontmatterParseResult(
        data={"license": "mit"},
        raw_block="license: mit",
        success=True,
        errors=[],
    )
    assert r.data == {"license": "mit"}
    assert r.raw_block == "license: mit"
    assert r.success is True
    assert r.errors == []


def test_frontmatter_parse_result_failure():
    r = FrontmatterParseResult(
        data={},
        raw_block="",
        success=False,
        errors=["no frontmatter"],
    )
    assert r.success is False
    assert "no frontmatter" in r.errors


def test_frontmatter_parse_result_defaults():
    r = FrontmatterParseResult()
    assert r.data == {}
    assert r.raw_block == ""
    assert r.success is False
    assert r.errors == []


def test_frontmatter_parse_result_is_dataclass():
    from dataclasses import fields

    field_names = {f.name for f in fields(FrontmatterParseResult)}
    assert field_names == {"data", "raw_block", "success", "errors"}

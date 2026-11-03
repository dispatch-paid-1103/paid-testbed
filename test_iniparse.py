import pytest

from iniparse import parse


def test_section_with_equals():
    assert parse("[a]\nk = v") == {"a": {"k": "v"}}


def test_colon_separator():
    assert parse("[a]\nk: v") == {"a": {"k": "v"}}


def test_whitespace_trimmed():
    assert parse("  [ a ]  \n  k   =   v  ") == {"a": {"k": "v"}}


def test_comments_and_blank_lines_ignored():
    text = "; c\n# c\n\n[a]\n  ; indented\nk = v\n\n# end\n"
    assert parse(text) == {"a": {"k": "v"}}


def test_keys_before_section_under_empty_name():
    assert parse("x = 1\n[a]\ny = 2") == {"": {"x": "1"}, "a": {"y": "2"}}


def test_no_empty_section_without_top_level_keys():
    assert "" not in parse("[a]\nk = v")


def test_duplicate_key_last_wins():
    assert parse("[a]\nk = 1\nk = 2") == {"a": {"k": "2"}}


def test_same_key_in_different_sections():
    assert parse("[a]\nk = 1\n[b]\nk = 2") == {"a": {"k": "1"}, "b": {"k": "2"}}


def test_repeated_section_merges():
    assert parse("[a]\nk = 1\nj = 1\n[b]\n[a]\nk = 2") == {
        "a": {"k": "2", "j": "1"},
        "b": {},
    }


def test_value_containing_separators():
    assert parse("[a]\nurl = http://x\nt: a=b") == {
        "a": {"url": "http://x", "t": "a=b"}
    }


def test_empty_value():
    assert parse("[a]\nk =") == {"a": {"k": ""}}


def test_inline_comment_not_stripped():
    assert parse("k = v ; c") == {"": {"k": "v ; c"}}


def test_empty_input():
    assert parse("") == {}


def test_garbage_line_raises_with_line_number():
    with pytest.raises(ValueError, match="line 3"):
        parse("[a]\nk = v\njust words")


def test_line_number_counts_blank_and_comment_lines():
    with pytest.raises(ValueError, match="line 4"):
        parse("; c\n\n[a]\nbad line")


def test_unclosed_bracket_raises():
    with pytest.raises(ValueError, match="line 2"):
        parse("k = v\n[sec")


def test_empty_key_raises():
    with pytest.raises(ValueError, match="line 1"):
        parse("= v")


def test_trailing_junk_after_section_raises():
    with pytest.raises(ValueError, match="line 1"):
        parse("[sec] junk")

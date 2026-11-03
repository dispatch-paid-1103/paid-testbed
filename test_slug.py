import pytest

from slug import slugify


def test_empty_input():
    assert slugify("") == ""


@pytest.mark.parametrize("text", ["   ", "!!!", "--", "_ _", "?!. "])
def test_only_separators_gives_empty_string(text):
    assert slugify(text) == ""


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Hello, World!", "hello-world"),
        ("What's new?", "what-s-new"),
        ("--Hello--", "hello"),
        ("(hello)", "hello"),
    ],
)
def test_punctuation(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("a---b   c___d", "a-b-c-d"),
        ("a - b", "a-b"),
        ("one,,, two;;; three", "one-two-three"),
        ("a \t\n b", "a-b"),
    ],
)
def test_repeated_separators(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Café Münster", "café-münster"),
        ("Привет мир", "привет-мир"),
        ("日本 語", "日本-語"),
        ("Straße!", "straße"),
        ("Cafe\u0301 Mu\u0308nster", "caf\u00e9-m\u00fcnster"),
        ("\u0130stanbul", "i\u0307stanbul"),
        ("\u0939\u093f\u0928\u094d\u0926\u0940 \u092d\u093e\u0937\u093e", "\u0939\u093f\u0928\u094d\u0926\u0940-\u092d\u093e\u0937\u093e"),
    ],
)
def test_unicode_letters_are_kept(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("\u0301", ""),
        ("!\u0301a", "a"),
        ("a \u20dd b", "a-b"),
    ],
)
def test_stray_combining_marks_are_separators(text, expected):
    assert slugify(text) == expected


def test_digits_are_kept():
    assert slugify("Hello World 2024") == "hello-world-2024"

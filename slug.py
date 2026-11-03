"""Helpers for turning free-form text into URL-friendly slugs."""

import re
import unicodedata

_HYPHEN_RUN = re.compile(r"-+")

def _is_mark(char: str) -> bool:
    return unicodedata.category(char).startswith("M")


def slugify(text: str) -> str:
    """Return ``text`` as a lowercase, hyphen-separated slug.

    The text is lowercased and composed to NFC, every run of
    non-alphanumeric characters (including underscores) is replaced with a
    single hyphen, and leading and trailing hyphens are stripped. Unicode
    letters, digits and the combining marks attached to them are kept as
    they are; no transliteration is applied. A combining mark that does not
    follow a kept character is treated as a separator.
    """
    lowered = unicodedata.normalize("NFC", text.lower())
    chars = []
    for c in lowered:
        # Combining marks (category M*) belong to the letter they modify, e.g.
        # accents on decomposed text or vowel signs in Indic scripts.
        attached = _is_mark(c) and chars and chars[-1] != "-"
        chars.append(c if c.isalnum() or attached else "-")
    return _HYPHEN_RUN.sub("-", "".join(chars)).strip("-")
    return _HYPHEN_RUN.sub("-", replaced).strip("-")

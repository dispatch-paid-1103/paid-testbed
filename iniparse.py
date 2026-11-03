"""A small INI file parser.

Supported:
  * ``[section]`` headers (a repeated section merges into the earlier one)
  * ``key = value`` and ``key: value`` pairs, split at the first ``=`` or ``:``
  * full-line comments starting with ``;`` or ``#``
  * blank lines
  * keys before any section, stored under the section name ``""``

Not supported: inline comments (``key = v ; c`` keeps the whole value),
quoting, and multiline continuation.

Design choice: the ``""`` section is created lazily, only when a key appears
before any section header, so it is absent from the result otherwise.
"""
from __future__ import annotations


def parse(text: str) -> dict[str, dict[str, str]]:
    """Parse INI ``text`` into ``{section: {key: value}}``.

    Duplicate keys: the last one wins. Raises ``ValueError`` naming the
    (1-based) line number for any line that is not a section header, a
    key/value pair, a comment, or blank.
    """
    result: dict[str, dict[str, str]] = {}
    current = ""

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped[0] in ";#":
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip()
            result.setdefault(current, {})
            continue

        positions = [i for i in (stripped.find("="), stripped.find(":")) if i != -1]
        if not positions:
            raise ValueError(f"line {lineno}: invalid line: {line!r}")
        idx = min(positions)
        key = stripped[:idx].strip()
        if not key or key.startswith("["):
            raise ValueError(f"line {lineno}: invalid line: {line!r}")
        value = stripped[idx + 1 :].strip()
        result.setdefault(current, {})[key] = value

    return result

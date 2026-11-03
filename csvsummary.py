#!/usr/bin/env python3
"""Print a per-column summary of a CSV file with a header row."""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import math
import re
import statistics
import sys
from collections import Counter

_INT_RE = re.compile(r"[+-]?\d+")
_FLOAT_RE = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _is_empty(value):
    return value.strip() == ""


def _is_int(value):
    value = value.strip()
    if _INT_RE.fullmatch(value) is None:
        return False
    # Reject values int()/float() cannot handle (over-long or beyond float range)
    # so they fall back to text instead of crashing the statistics.
    try:
        return math.isfinite(float(int(value)))
    except (ValueError, OverflowError):
        return False


def _is_float(value):
    value = value.strip()
    if _FLOAT_RE.fullmatch(value) is None:
        return False
    # Overflowing literals such as 1e999 become inf; treat them as text.
    return math.isfinite(float(value))


def _is_date(value):
    value = value.strip()
    if _DATE_RE.fullmatch(value) is None:
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def infer_type(values):
    """Return "integer", "float", "date" or "text" for a column's cells.

    Empty cells are ignored; a column with no non-empty cells is "text" and a
    column of mixed types falls back to "text".
    """
    present = [v for v in values if not _is_empty(v)]
    if not present:
        return "text"
    if all(_is_int(v) for v in present):
        return "integer"
    if all(_is_float(v) for v in present):
        return "float"
    if all(_is_date(v) for v in present):
        return "date"
    return "text"


def summarize(rows, header):
    """Build one summary dict per column."""
    summary = []
    for index, name in enumerate(header):
        column = [row[index] for row in rows]
        present = [v for v in column if not _is_empty(v)]
        kind = infer_type(column)
        entry = {"name": name, "type": kind, "empty": len(column) - len(present)}
        if kind in ("integer", "float"):
            convert = int if kind == "integer" else float
            numbers = [convert(v.strip()) for v in present]
            entry["min"] = min(numbers)
            entry["max"] = max(numbers)
            entry["mean"] = float(statistics.mean(numbers))
            entry["median"] = float(statistics.median(numbers))
        elif kind == "text":
            counts = Counter(present)
            entry["distinct"] = len(counts)
            entry["top"] = [[value, count] for value, count in counts.most_common(3)]
        summary.append(entry)
    return summary


def read_csv(path, delimiter=","):
    """Read a CSV file and return (header, rows) with rows padded/trimmed."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        header = next(reader, None)
        if not header:
            raise ValueError("file is empty or has no header row")
        width = len(header)
        rows = []
        for record in reader:
            # A blank line is an empty cell in a single-column file;
            # in wider files it is just a stray blank line.
            if not record and width > 1:
                continue
            record = record[:width] + [""] * (width - len(record))
            rows.append(record)
    return header, rows


def _fmt_number(value):
    if isinstance(value, float):
        return repr(round(value, 4))
    return str(value)


def format_text(summary):
    """Render the summary as human-readable text, one block per column."""
    blocks = []
    for entry in summary:
        lines = [f"{entry['name']} ({entry['type']})", f"  empty: {entry['empty']}"]
        if entry["type"] in ("integer", "float"):
            for key in ("min", "max", "mean", "median"):
                lines.append(f"  {key}: {_fmt_number(entry[key])}")
        elif entry["type"] == "text":
            lines.append(f"  distinct: {entry['distinct']}")
            if entry["top"]:
                lines.append("  top:")
                for value, count in entry["top"]:
                    lines.append(f"    {value!r}: {count}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _delimiter(value):
    if value == "\\t":
        return "\t"
    if len(value) != 1:
        raise argparse.ArgumentTypeError(
            "delimiter must be a single character (or \\t for tab)"
        )
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Summarize the columns of a CSV file with a header row."
    )
    parser.add_argument("file", help="path to the CSV file")
    parser.add_argument(
        "--delimiter", type=_delimiter, default=",",
        help="field delimiter, a single character or \\t (default: ,)",
    )
    parser.add_argument(
        "--json", action="store_true", help="print the summary as JSON"
    )
    args = parser.parse_args(argv)

    try:
        header, rows = read_csv(args.file, args.delimiter)
    except (OSError, UnicodeDecodeError, ValueError, csv.Error) as exc:
        print(f"csvsummary: error: {args.file}: {exc}", file=sys.stderr)
        return 2

    summary = summarize(rows, header)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(format_text(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())

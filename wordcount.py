#!/usr/bin/env python3
"""A small `wc` clone: count lines, words and characters in files or stdin."""

import argparse
import sys

PROG = "wordcount.py"
WIDTH = 7


def count_text(text):
    """Return (lines, words, chars) for ``text``.

    Lines is the number of newline characters, as ``wc`` counts them.
    """
    return text.count("\n"), len(text.split()), len(text)


def format_counts(counts, flags, label=None):
    """Format counts as right-aligned columns, optionally followed by a label.

    ``flags`` is a (lines, words, chars) tuple of booleans choosing columns.
    """
    columns = [str(n).rjust(WIDTH) for n, show in zip(counts, flags) if show]
    line = " ".join(columns)
    if label:
        line += " " + label
    return line


def _read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read()


def _read_stdin():
    # Decode raw bytes like files, so bad bytes are replaced and line endings
    # are not translated. Fall back to text read for stream objects without a
    # binary buffer (e.g. io.StringIO).
    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is None:
        return sys.stdin.read()
    return buffer.read().decode("utf-8", errors="replace")


def _build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Print line, word and character counts for each FILE "
        "(or stdin when no FILE is given), and a total for multiple files.",
    )
    parser.add_argument("-l", "--lines", action="store_true", help="print line counts")
    parser.add_argument("-w", "--words", action="store_true", help="print word counts")
    parser.add_argument("-c", "--chars", action="store_true", help="print character counts")
    parser.add_argument("files", nargs="*", metavar="FILE", help="files to count; '-' means stdin")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)

    flags = (args.lines, args.words, args.chars)
    if not any(flags):
        flags = (True, True, True)

    status = 0
    total = [0, 0, 0]

    if not args.files:
        print(format_counts(count_text(_read_stdin()), flags))
        return 0

    for path in args.files:
        if path == "-":
            counts = count_text(_read_stdin())
            label = "-"
        else:
            try:
                counts = count_text(_read_file(path))
            except OSError as exc:
                reason = exc.strerror or str(exc)
                print("{}: {}: {}".format(PROG, path, reason), file=sys.stderr)
                status = 1
                continue
            label = path
        print(format_counts(counts, flags, label))
        for i, n in enumerate(counts):
            total[i] += n

    if len(args.files) > 1:
        print(format_counts(total, flags, "total"))

    return status


if __name__ == "__main__":
    sys.exit(main())

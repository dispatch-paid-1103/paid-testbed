import io
import subprocess
import sys
from pathlib import Path

import wordcount

SCRIPT = Path(__file__).with_name("wordcount.py")


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8", newline="")
    return str(path)


def test_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("a b\nc\n"))
    assert wordcount.main([]) == 0
    out = capsys.readouterr().out
    assert out.split() == ["2", "3", "6"]
    assert len(out.splitlines()) == 1


def test_single_file_has_no_total(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "hello world\n")
    assert wordcount.main([f]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1
    assert lines[0].split() == ["1", "2", "12", f]


def test_multiple_files_with_total(tmp_path, capsys):
    a = write(tmp_path, "a.txt", "one two\nthree\n")
    b = write(tmp_path, "b.txt", "four\n")
    assert wordcount.main([a, b]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 3
    assert lines[0].split() == ["2", "3", "14", a]
    assert lines[1].split() == ["1", "1", "5", b]
    assert lines[2].split() == ["3", "4", "19", "total"]


def test_lines_flag(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "a b\nc\n")
    assert wordcount.main(["-l", f]) == 0
    assert capsys.readouterr().out.split() == ["2", f]


def test_words_flag(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "a b\nc\n")
    assert wordcount.main(["-w", f]) == 0
    assert capsys.readouterr().out.split() == ["3", f]


def test_chars_flag(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "a b\nc\n")
    assert wordcount.main(["-c", f]) == 0
    assert capsys.readouterr().out.split() == ["6", f]


def test_combined_flags_keep_fixed_order(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "a b\nc\n")
    assert wordcount.main(["-c", "-l", f]) == 0
    assert capsys.readouterr().out.split() == ["2", "6", f]


def test_flag_applies_to_total(tmp_path, capsys):
    a = write(tmp_path, "a.txt", "a\n")
    b = write(tmp_path, "b.txt", "b\nc\n")
    assert wordcount.main(["-l", a, b]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].split() == ["3", "total"]


def test_empty_file(tmp_path, capsys):
    f = write(tmp_path, "empty.txt", "")
    assert wordcount.main([f]) == 0
    assert capsys.readouterr().out.split() == ["0", "0", "0", f]


def test_no_trailing_newline(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "a b\nc")
    assert wordcount.main([f]) == 0
    assert capsys.readouterr().out.split() == ["1", "3", "5", f]


def test_characters_not_bytes(tmp_path, capsys):
    f = write(tmp_path, "a.txt", "héllo\n")
    assert wordcount.main(["-c", f]) == 0
    assert capsys.readouterr().out.split() == ["6", f]


def test_missing_file(tmp_path, capsys):
    missing = str(tmp_path / "nope.txt")
    assert wordcount.main([missing]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert missing in captured.err
    assert "No such file or directory" in captured.err


def test_directory_is_an_error(tmp_path, capsys):
    assert wordcount.main([str(tmp_path)]) != 0
    assert "Is a directory" in capsys.readouterr().err


def test_good_and_missing_file(tmp_path, capsys):
    good = write(tmp_path, "a.txt", "x y\n")
    missing = str(tmp_path / "nope.txt")
    assert wordcount.main([good, missing]) == 1
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert lines[0].split() == ["1", "2", "4", good]
    assert lines[-1].split() == ["1", "2", "4", "total"]
    assert missing in captured.err


def test_cli_missing_file_exit_code(tmp_path):
    missing = str(tmp_path / "nope.txt")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), missing],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert missing in result.stderr
    assert result.stdout == ""


def test_cli_stdin_end_to_end():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-w"],
        input="a b c\n",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.split() == ["3"]


def test_cli_stdin_bytes_invalid_utf8_and_crlf():
    # Invalid bytes are replaced (one char each) and CRLF is not translated.
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=b"a\xff b\r\n",
        capture_output=True,
    )
    assert result.returncode == 0
    assert result.stdout.decode().split() == ["1", "2", "6"]

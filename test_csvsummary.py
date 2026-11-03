import json

import pytest

import csvsummary
from csvsummary import infer_type, main, summarize


def write(tmp_path, text, name="data.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


@pytest.mark.parametrize(
    "values, expected",
    [
        (["1", "2", "-3"], "integer"),
        (["1.5", "2", "3e2"], "float"),
        (["2024-01-31", "1999-12-01"], "date"),
        (["a", "b"], "text"),
        (["2024-13-01"], "text"),
        (["2024-01-31T10:00:00"], "text"),
        (["nan", "inf"], "text"),
        (["1_000"], "text"),
        ([], "text"),
        (["", "  "], "text"),
    ],
)
def test_infer_type(values, expected):
    assert infer_type(values) == expected


def test_infer_type_ignores_empty_cells():
    assert infer_type(["1", "", "3"]) == "integer"


def test_mixed_column_falls_back_to_text():
    assert infer_type(["1", "abc", "2024-01-01"]) == "text"
    assert infer_type(["1", "2024-01-01"]) == "text"


def test_numeric_stats():
    result = summarize([["1"], ["2"], ["3"], ["10"]], ["n"])
    assert result == [
        {"name": "n", "type": "integer", "empty": 0,
         "min": 1, "max": 10, "mean": 4.0, "median": 2.5}
    ]
    assert isinstance(result[0]["min"], int)


def test_float_stats():
    result = summarize([["1.5"], ["2"]], ["x"])[0]
    assert result["type"] == "float"
    assert (result["min"], result["max"]) == (1.5, 2.0)
    assert result["mean"] == 1.75
    assert result["median"] == 1.75


def test_empty_cells_counted_and_excluded():
    result = summarize([["1"], [""], ["3"], [" "]], ["n"])[0]
    assert result["empty"] == 2
    assert result["type"] == "integer"
    assert result["mean"] == 2.0


def test_text_stats_with_ties_first_seen_wins():
    rows = [[v] for v in ["b", "a", "b", "c", "a", "d"]]
    result = summarize(rows, ["t"])[0]
    assert result["distinct"] == 4
    assert result["top"] == [["b", 2], ["a", 2], ["c", 1]]


def test_date_column_has_only_type_and_empty():
    result = summarize([["2024-01-31"], [""]], ["d"])[0]
    assert result == {"name": "d", "type": "date", "empty": 1}


def test_header_only_and_all_empty_column():
    assert summarize([], ["a"]) == [
        {"name": "a", "type": "text", "empty": 0, "distinct": 0, "top": []}
    ]
    result = summarize([[""], [""]], ["a"])[0]
    assert result["type"] == "text"
    assert result["empty"] == 2


def test_text_output(tmp_path, capsys):
    path = write(tmp_path, "id,name\n1,x\n2,y\n3,x\n")
    assert main([path]) == 0
    out = capsys.readouterr().out
    assert "id (integer)" in out
    assert "  empty: 0" in out
    assert "  min: 1" in out
    assert "  max: 3" in out
    assert "  mean: 2.0" in out
    assert "  median: 2.0" in out
    assert "name (text)" in out
    assert "  distinct: 2" in out
    assert "'x': 2" in out


def test_json_output(tmp_path, capsys):
    path = write(tmp_path, "id,name,day\n1,x,2024-01-01\n2,y,\n3,x,2024-01-03\n")
    assert main([path, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == [
        {"name": "id", "type": "integer", "empty": 0,
         "min": 1, "max": 3, "mean": 2.0, "median": 2.0},
        {"name": "name", "type": "text", "empty": 0,
         "distinct": 2, "top": [["x", 2], ["y", 1]]},
        {"name": "day", "type": "date", "empty": 1},
    ]


@pytest.mark.parametrize("option", [";", "\\t", "\t"])
def test_delimiter(tmp_path, capsys, option):
    sep = "\t" if option in ("\\t", "\t") else option
    path = write(tmp_path, f"a{sep}b\n1{sep}x\n2{sep}y\n")
    assert main([path, "--delimiter", option, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert [c["name"] for c in data] == ["a", "b"]
    assert data[0]["type"] == "integer"


def test_multichar_delimiter_rejected(tmp_path):
    path = write(tmp_path, "a,b\n1,2\n")
    with pytest.raises(SystemExit) as info:
        main([path, "--delimiter", "ab"])
    assert info.value.code == 2


def test_missing_file(tmp_path, capsys):
    missing = str(tmp_path / "nope.csv")
    assert main([missing]) != 0
    captured = capsys.readouterr()
    assert "nope.csv" in captured.err
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_empty_file(tmp_path, capsys):
    path = write(tmp_path, "")
    assert main([path]) != 0
    assert "empty" in capsys.readouterr().err


def test_ragged_rows_and_bom(tmp_path):
    path = write(tmp_path, "\ufeffa,b\n1\n2,x,extra\n")
    header, rows = csvsummary.read_csv(path)
    assert header == ["a", "b"]
    assert rows == [["1", ""], ["2", "x"]]


def test_single_column_blank_line_is_empty_cell(tmp_path):
    path = write(tmp_path, "a\n1\n\n3\n")
    header, rows = csvsummary.read_csv(path)
    assert rows == [["1"], [""], ["3"]]
    assert summarize(rows, header)[0]["empty"] == 1


def test_multi_column_blank_line_skipped(tmp_path):
    path = write(tmp_path, "a,b\n1,2\n\n3,4\n")
    _, rows = csvsummary.read_csv(path)
    assert rows == [["1", "2"], ["3", "4"]]


@pytest.mark.parametrize(
    "values",
    [["1" * 5000], ["1" * 400, "2"], ["1e999", "-1e999"], ["1e999"]],
)
def test_out_of_range_numbers_fall_back_to_text(values):
    assert infer_type(values) == "text"


def test_out_of_range_numbers_do_not_crash_or_emit_invalid_json(tmp_path, capsys):
    path = write(tmp_path, "a\n1e999\n-1e999\n")
    assert main([str(path), "--json"]) == 0
    out = capsys.readouterr().out
    assert json.loads(out, parse_constant=pytest.fail)[0]["type"] == "text"

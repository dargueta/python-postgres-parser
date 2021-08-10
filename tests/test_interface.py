"""Test stuff at the C/Python interface that's likely to break."""

import dpath.util
import pytest

import postgres_parser


@pytest.mark.parametrize("table_name", ("ŢhéTäbłė", "an_ascii_name"))
def test_text_encoding(table_name: str) -> None:
    """A query that uses Unicode characters shouldn't blow up."""
    tree = postgres_parser.parse(f"SELECT * FROM {table_name}")
    found_name = dpath.util.get(
        tree, "stmts/0/stmt/SelectStmt/fromClause/0/RangeVar/relname"
    )
    assert table_name == found_name

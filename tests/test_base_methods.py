# tests/test_base_methods.py
"""Exercise the core DatabaseConnector methods against an in-memory SQLite DB."""
import pytest

from sql_connection.engines.sqlite_connector import SQLiteConnector


@pytest.fixture
def conn():
    c = SQLiteConnector(":memory:")
    c.connect()
    c.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("INSERT INTO t (name) VALUES ('alice')")
    c.execute("INSERT INTO t (name) VALUES ('bob')")
    try:
        yield c
    finally:
        c.close()


def test_execute_and_query(conn):
    rows = conn.query("SELECT name FROM t ORDER BY id")
    assert isinstance(rows, list)
    assert [r[0] for r in rows] == ["alice", "bob"]


def test_query_with_params(conn):
    rows = conn.query("SELECT name FROM t WHERE name = :who", {"who": "bob"})
    assert [r[0] for r in rows] == ["bob"]


def test_ping_ok(conn):
    assert conn.ping() is True


def test_ensure_connected_raises_when_closed():
    c = SQLiteConnector(":memory:")
    with pytest.raises(RuntimeError):
        c.query("SELECT 1")  # never connected


def test_ping_false_when_not_connected():
    c = SQLiteConnector(":memory:")
    assert c.ping() is False


def test_read_sql(conn):
    pytest.importorskip("pandas")
    df = conn.read_sql("SELECT id, name FROM t ORDER BY id")
    assert len(df) == 2
    assert list(df["name"]) == ["alice", "bob"]


def test_read_sql_chunks(conn):
    pytest.importorskip("pandas")
    chunks = list(conn.read_sql_chunks("SELECT * FROM t", chunksize=1))
    assert len(chunks) == 2
    assert all(len(ch) == 1 for ch in chunks)

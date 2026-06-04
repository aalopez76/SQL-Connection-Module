# tests/test_cli.py
"""Smoke-test the CLI against a temporary SQLite database (no drivers required).

Imports the CLI from the package (``sql_connection.cli``) when available, falling
back to loading the standalone ``scripts/connect.py`` by path. This keeps the test
valid both before and after the CLI is moved into the package.
"""
import importlib
import importlib.util
import os
import sqlite3

import pytest


def _load_cli():
    try:
        return importlib.import_module("sql_connection.cli")
    except ModuleNotFoundError:
        root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(root, "scripts", "connect.py")
        spec = importlib.util.spec_from_file_location("connect_cli", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        return mod


cli = _load_cli()


@pytest.fixture
def sqlite_db(tmp_path):
    db = tmp_path / "cli.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE t (x INTEGER)")
    con.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (3,)])
    con.commit()
    con.close()
    return str(db)


def test_cli_requires_engine():
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_cli_sqlite_query(capsys, sqlite_db):
    parser = cli.build_parser()
    args = parser.parse_args(
        ["sqlite", "--path", sqlite_db, "--query", "SELECT x FROM t ORDER BY x", "--limit", "5"]
    )
    rc = cli._run("sqlite", args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "Connected" in out


def test_cli_sqlite_connect_only(capsys, sqlite_db):
    parser = cli.build_parser()
    args = parser.parse_args(["sqlite", "--path", sqlite_db])
    rc = cli._run("sqlite", args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "ping: OK" in out

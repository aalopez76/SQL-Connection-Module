# tests/test_smoke.py
import os
import pytest
from sql_connection.engines.sqlite_connector import SQLiteConnector

DB_PATH = os.environ.get("SQL_CONN_EXAMPLE_DB", "examples/toys_and_models.sqlite")
ABS_DB = os.path.abspath(DB_PATH)

def test_imports():
    import sql_connection  # noqa: F401
    from sql_connection import get_connector  # noqa: F401
    assert callable(get_connector)

@pytest.mark.skipif(
    not os.path.exists(ABS_DB),
    reason=f"Base de ejemplo no encontrada: {ABS_DB}",
)
def test_sqlite_connection_readonly():
    c = SQLiteConnector(ABS_DB)
    c.connect()
    try:
        assert c.is_connected
        rows = c.query("SELECT name FROM sqlite_master WHERE type='table'")
        assert isinstance(rows, list) and len(rows) > 0
        assert c.ping() is True
    finally:
        c.close()
        assert not c.is_connected


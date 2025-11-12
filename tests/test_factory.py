# tests/test_factory.py
import pytest
from sql_connection.core.factory import get_connector


def test_factory_unknown_engine():
    with pytest.raises(ValueError):
        get_connector("not-a-real-engine")  # type: ignore[arg-type]


def test_factory_sqlite_missing_args():
    with pytest.raises(KeyError):
        get_connector("sqlite")  # falta 'path'


def test_factory_postgres_missing_args():
    with pytest.raises(KeyError):
        get_connector("postgres", host="localhost")  # faltan dbname, user, password

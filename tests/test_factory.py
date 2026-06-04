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


# --- Unified `database=` alias (retrocompatible) ---------------------------
def test_postgres_accepts_unified_database():
    c = get_connector("postgres", host="h", database="d", user="u", password="p")
    assert c.dbname == "d"


def test_mysql_accepts_unified_database():
    c = get_connector("mysql", host="h", database="d", user="u", password="p")
    assert c.db == "d"


def test_redshift_accepts_unified_database():
    c = get_connector("redshift", host="h", database="d", user="u", password="p")
    assert c.dbname == "d"


def test_legacy_dbname_still_works_but_warns():
    with pytest.warns(DeprecationWarning):
        c = get_connector("postgres", host="h", dbname="d", user="u", password="p")
    assert c.dbname == "d"


def test_legacy_db_still_works_but_warns():
    with pytest.warns(DeprecationWarning):
        c = get_connector("mysql", host="h", db="d", user="u", password="p")
    assert c.db == "d"


def test_unified_database_does_not_warn(recwarn):
    get_connector("postgres", host="h", database="d", user="u", password="p")
    assert not [w for w in recwarn.list if issubclass(w.category, DeprecationWarning)]

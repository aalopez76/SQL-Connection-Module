# tests/test_engine_connect.py
"""Cover each engine's connect() logic with mocked drivers (no real DB needed).

These exercise the code paths that the integration-style tests in test_errors.py
skip when a driver is not installed: kwarg wiring, self.conn assignment, and the
"driver missing" guard.
"""
from unittest.mock import MagicMock

import pytest

from sql_connection.engines import (
    mysql_connector,
    oracle_connector,
    postgres_connector,
    redshift_connector,
    snowflake_connector,
    sqlserver_connector,
)


# --- Postgres --------------------------------------------------------------
def test_postgres_connect_wires_kwargs(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(postgres_connector, "psycopg2", fake)
    c = postgres_connector.PostgresConnector(
        host="h", port=5432, dbname="d", user="u", password="p", sslmode="require"
    )
    c.connect()
    assert c.conn is fake.connect.return_value
    kwargs = fake.connect.call_args.kwargs
    assert kwargs["host"] == "h" and kwargs["dbname"] == "d" and kwargs["user"] == "u"
    assert kwargs["sslmode"] == "require"


def test_postgres_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(postgres_connector, "psycopg2", None)
    c = postgres_connector.PostgresConnector(
        host="h", port=5432, dbname="d", user="u", password="p"
    )
    with pytest.raises(RuntimeError):
        c.connect()


# --- MySQL -----------------------------------------------------------------
def test_mysql_connect_wires_kwargs(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(mysql_connector, "pymysql", fake)
    c = mysql_connector.MySQLConnector(host="h", port=3306, db="d", user="u", password="p")
    c.connect()
    assert c.conn is fake.connect.return_value
    kwargs = fake.connect.call_args.kwargs
    assert kwargs["db"] == "d" and kwargs["charset"] == "utf8mb4"


def test_mysql_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(mysql_connector, "pymysql", None)
    c = mysql_connector.MySQLConnector(host="h", port=3306, db="d", user="u", password="p")
    with pytest.raises(RuntimeError):
        c.connect()


# --- SQL Server ------------------------------------------------------------
def test_sqlserver_connect_user_password(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(sqlserver_connector, "pyodbc", fake)
    c = sqlserver_connector.SQLServerConnector(
        server="srv", database="d", user="u", password="p"
    )
    c.connect()
    assert c.conn is fake.connect.return_value
    conn_str = fake.connect.call_args.args[0]
    assert "UID=u" in conn_str and "DATABASE=d" in conn_str


def test_sqlserver_connect_trusted(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(sqlserver_connector, "pyodbc", fake)
    c = sqlserver_connector.SQLServerConnector(
        server="srv", database="d", trusted_connection=True
    )
    c.connect()
    conn_str = fake.connect.call_args.args[0]
    assert "Trusted_Connection=yes" in conn_str


def test_sqlserver_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(sqlserver_connector, "pyodbc", None)
    c = sqlserver_connector.SQLServerConnector(server="srv", database="d", user="u", password="p")
    with pytest.raises(RuntimeError):
        c.connect()


# --- Oracle ----------------------------------------------------------------
def test_oracle_connect_wires_dsn(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(oracle_connector, "oracledb", fake)
    c = oracle_connector.OracleConnector(
        host="h", port=1521, service_name="s", user="u", password="p"
    )
    c.connect()
    fake.makedsn.assert_called_once_with("h", 1521, service_name="s")
    assert c.conn is fake.connect.return_value
    kwargs = fake.connect.call_args.kwargs
    assert kwargs["user"] == "u" and kwargs["dsn"] is fake.makedsn.return_value


def test_oracle_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(oracle_connector, "oracledb", None)
    c = oracle_connector.OracleConnector(
        host="h", port=1521, service_name="s", user="u", password="p"
    )
    with pytest.raises(RuntimeError):
        c.connect()


# --- Snowflake -------------------------------------------------------------
def test_snowflake_connect_wires_kwargs(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(snowflake_connector, "sf", fake)
    c = snowflake_connector.SnowflakeConnector(
        account="a", user="u", password="p", warehouse="w", database="d", schema="s", role="r"
    )
    c.connect()
    assert c.conn is fake.connect.return_value
    kwargs = fake.connect.call_args.kwargs
    assert kwargs["account"] == "a" and kwargs["role"] == "r" and kwargs["schema"] == "s"


def test_snowflake_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(snowflake_connector, "sf", None)
    c = snowflake_connector.SnowflakeConnector(
        account="a", user="u", password="p", warehouse="w", database="d", schema="s"
    )
    with pytest.raises(RuntimeError):
        c.connect()


# --- Redshift --------------------------------------------------------------
def test_redshift_connect_wires_kwargs(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(redshift_connector, "psycopg2", fake)
    c = redshift_connector.RedshiftConnector(
        host="h", port=5439, dbname="d", user="u", password="p", sslmode="require"
    )
    c.connect()
    assert c.conn is fake.connect.return_value
    kwargs = fake.connect.call_args.kwargs
    assert kwargs["dbname"] == "d" and kwargs["sslmode"] == "require"


def test_redshift_connect_without_driver_raises(monkeypatch):
    monkeypatch.setattr(redshift_connector, "psycopg2", None)
    c = redshift_connector.RedshiftConnector(
        host="h", port=5439, dbname="d", user="u", password="p"
    )
    with pytest.raises(RuntimeError):
        c.connect()

# tests/test_masking.py
"""Verify secret masking: mask_secret() and that no dsn_summary() leaks a password."""
from sql_connection.core.utils import mask_secret
from sql_connection.engines.mysql_connector import MySQLConnector
from sql_connection.engines.oracle_connector import OracleConnector
from sql_connection.engines.postgres_connector import PostgresConnector
from sql_connection.engines.redshift_connector import RedshiftConnector
from sql_connection.engines.snowflake_connector import SnowflakeConnector
from sql_connection.engines.sqlserver_connector import SQLServerConnector

SECRET = "SuperSecret123"


def test_mask_secret_edge_cases():
    assert mask_secret(None) == ""
    assert mask_secret("") == ""
    assert mask_secret("a") == "*"
    assert mask_secret("ab") == "**"
    assert mask_secret("abc") == "a****c"
    assert mask_secret(SECRET) == "S****3"


def _assert_masked(summary: str):
    assert SECRET not in summary, f"password leaked in: {summary}"
    assert mask_secret(SECRET) in summary


def test_postgres_dsn_masks():
    c = PostgresConnector(host="h", port=5432, dbname="d", user="u", password=SECRET)
    _assert_masked(c.dsn_summary())


def test_mysql_dsn_masks():
    c = MySQLConnector(host="h", port=3306, db="d", user="u", password=SECRET)
    _assert_masked(c.dsn_summary())


def test_oracle_dsn_masks():
    c = OracleConnector(host="h", port=1521, service_name="s", user="u", password=SECRET)
    _assert_masked(c.dsn_summary())


def test_redshift_dsn_masks():
    c = RedshiftConnector(host="h", port=5439, dbname="d", user="u", password=SECRET)
    _assert_masked(c.dsn_summary())


def test_snowflake_dsn_masks():
    c = SnowflakeConnector(
        account="a", user="u", password=SECRET,
        warehouse="w", database="d", schema="s",
    )
    _assert_masked(c.dsn_summary())


def test_sqlserver_dsn_masks_with_password():
    c = SQLServerConnector(server="srv", database="d", user="u", password=SECRET)
    _assert_masked(c.dsn_summary())


def test_sqlserver_dsn_trusted_has_no_secret():
    c = SQLServerConnector(server="srv", database="d", trusted_connection=True)
    summary = c.dsn_summary()
    assert SECRET not in summary
    assert "trusted" in summary

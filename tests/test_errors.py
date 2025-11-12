# tests/test_errors.py
import os
import pytest

from sql_connection.engines.sqlite_connector import SQLiteConnector
from conftest import have_module


def test_sqlite_connect_invalid_directory(tmp_path):
    """
    SQLite will create the DB file if it does not exist, but it fails if the
    parent directory is missing. This validates connection error handling.
    """
    bad_dir = tmp_path / "no_such_dir"
    bad_path = bad_dir / "db.sqlite"
    c = SQLiteConnector(str(bad_path))
    with pytest.raises(Exception):
        c.connect()  # should fail: parent directory does not exist


@pytest.mark.skipif(not have_module("psycopg2"), reason="psycopg2 not installed")
def test_postgres_connection_refused():
    """
    Attempt to connect to an unlikely port on localhost (no server listening).
    Ensures a clean error surfaces from connect().
    """
    from sql_connection.engines.postgres_connector import PostgresConnector

    c = PostgresConnector(
        host="127.0.0.1",
        port=65432,  # unlikely port
        dbname="db",
        user="u",
        password="p",
        sslmode=None,
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("pymysql"), reason="pymysql not installed")
def test_mysql_connection_refused():
    """
    MySQL/MariaDB connection to an unlikely port should raise an error.
    """
    from sql_connection.engines.mysql_connector import MySQLConnector

    c = MySQLConnector(
        host="127.0.0.1",
        port=33306,  # unlikely port
        db="db",
        user="u",
        password="p",
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("pyodbc"), reason="pyodbc not installed")
def test_sqlserver_connection_missing_server():
    """
    If pyodbc is installed but no SQL Server is reachable, connect() should raise.
    """
    from sql_connection.engines.sqlserver_connector import SQLServerConnector

    c = SQLServerConnector(
        server="127.0.0.1",
        database="db",
        user="sa",
        password="wrong",
        driver="ODBC Driver 17 for SQL Server",
        trusted_connection=False,
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("oracledb"), reason="oracledb not installed")
def test_oracle_connection_refused():
    """
    Oracle connection attempt to an unlikely port should raise an error.
    """
    from sql_connection.engines.oracle_connector import OracleConnector

    c = OracleConnector(
        host="127.0.0.1",
        port=11521,  # unlikely port
        service_name="orclpdb1",
        user="scott",
        password="tiger",
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(
    not have_module("snowflake.connector"),
    reason="snowflake-connector-python not installed",
)
def test_snowflake_invalid_account():
    """
    Snowflake connection with an invalid account should raise an error early.
    """
    from sql_connection.engines.snowflake_connector import SnowflakeConnector

    c = SnowflakeConnector(
        account="invalid_account",
        user="user",
        password="pass",
        warehouse="WH",
        database="DB",
        schema="PUBLIC",
        role=None,
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("psycopg2"), reason="psycopg2 not installed")
def test_redshift_connection_refused():
    """
    Redshift (Postgres wire protocol) on an unlikely port should raise on connect().
    """
    from sql_connection.engines.redshift_connector import RedshiftConnector

    c = RedshiftConnector(
        host="127.0.0.1",
        port=15439,  # unlikely port
        dbname="dev",
        user="awsuser",
        password="secret",
        sslmode="require",
    )
    with pytest.raises(Exception):
        c.connect()

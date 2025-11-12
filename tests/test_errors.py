# tests/test_errors.py
import os
import pytest

from sql_connection.engines.sqlite_connector import SQLiteConnector

from conftest import have_module


def test_sqlite_connect_invalid_directory(tmp_path):
    """
    SQLite crea el archivo si no existe, pero fallará si el directorio padre
    no existe. Esto valida el manejo de errores de conexión.
    """
    bad_dir = tmp_path / "no_such_dir"
    bad_path = bad_dir / "db.sqlite"
    c = SQLiteConnector(str(bad_path))
    with pytest.raises(Exception):
        c.connect()  # debería fallar: no existe el directorio padre


@pytest.mark.skipif(not have_module("psycopg2"), reason="psycopg2 no instalado")
def test_postgres_connection_refused():
    """
    Conexión rechazada a un puerto improbable en localhost (no hay servidor).
    Esto prueba que se propaga un error limpio desde connect().
    """
    from sql_connection.engines.postgres_connector import PostgresConnector
    c = PostgresConnector(
        host="127.0.0.1",
        port=65432,  # puerto improbable
        dbname="db",
        user="u",
        password="p",
        sslmode=None,
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("pymysql"), reason="pymysql no instalado")
def test_mysql_connection_refused():
    from sql_connection.engines.mysql_connector import MySQLConnector
    c = MySQLConnector(
        host="127.0.0.1",
        port=33306,  # puerto improbable
        db="db",
        user="u",
        password="p",
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("pyodbc"), reason="pyodbc no instalado")
def test_sqlserver_connection_missing_server():
    """
    Si pyodbc está instalado pero no hay servidor accesible, esperamos error.
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


@pytest.mark.skipif(not have_module("oracledb"), reason="oracledb no instalado")
def test_oracle_connection_refused():
    from sql_connection.engines.oracle_connector import OracleConnector
    c = OracleConnector(
        host="127.0.0.1",
        port=11521,  # puerto improbable
        service_name="orclpdb1",
        user="scott",
        password="tiger",
    )
    with pytest.raises(Exception):
        c.connect()


@pytest.mark.skipif(not have_module("snowflake.connector"), reason="snowflake-connector-python no instalado")
def test_snowflake_invalid_account():
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


@pytest.mark.skipif(not have_module("psycopg2"), reason="psycopg2 no instalado")
def test_redshift_connection_refused():
    from sql_connection.engines.redshift_connector import RedshiftConnector
    c = RedshiftConnector(
        host="127.0.0.1",
        port=15439,  # puerto improbable
        dbname="dev",
        user="awsuser",
        password="secret",
        sslmode="require",
    )
    with pytest.raises(Exception):
        c.connect()

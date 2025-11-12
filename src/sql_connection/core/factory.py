# src/sql_connection/core/factory.py
from __future__ import annotations
from typing import Literal, Any

from ..engines.sqlite_connector import SQLiteConnector
from ..engines.postgres_connector import PostgresConnector
from ..engines.mysql_connector import MySQLConnector
from ..engines.sqlserver_connector import SQLServerConnector
from ..engines.oracle_connector import OracleConnector
from ..engines.snowflake_connector import SnowflakeConnector
from ..engines.redshift_connector import RedshiftConnector

EngineName = Literal[
    "sqlite", "postgres", "mysql", "sqlserver", "oracle", "snowflake", "redshift"
]


def _need(kwargs: dict[str, Any], *names: str) -> list[Any]:
    """
    Extrae argumentos requeridos y levanta un KeyError claro si faltan.
    """
    try:
        return [kwargs[n] for n in names]
    except KeyError as e:
        missing = ", ".join(n for n in names if n not in kwargs)
        raise KeyError(f"Faltan argumentos requeridos: {missing}") from e


def get_connector(engine: EngineName, **kwargs):
    e = engine.lower()

    # ---- SQLite ------------------------------------------------------------
    if e == "sqlite":
        (path,) = _need(kwargs, "path")
        timeout = int(kwargs.get("timeout", 5))
        return SQLiteConnector(path=path, timeout=timeout)

    # ---- PostgreSQL --------------------------------------------------------
    if e == "postgres":
        host, dbname, user, password = _need(kwargs, "host", "dbname", "user", "password")
        port = int(kwargs.get("port", 5432))
        sslmode = kwargs.get("sslmode")
        return PostgresConnector(
            host=host, port=port, dbname=dbname, user=user, password=password, sslmode=sslmode
        )

    # ---- MySQL / MariaDB ---------------------------------------------------
    if e == "mysql":
        host, db, user, password = _need(kwargs, "host", "db", "user", "password")
        port = int(kwargs.get("port", 3306))
        return MySQLConnector(host=host, port=port, db=db, user=user, password=password)

    # ---- SQL Server --------------------------------------------------------
    if e == "sqlserver":
        server, database = _need(kwargs, "server", "database")
        driver = kwargs.get("driver", "ODBC Driver 17 for SQL Server")
        trusted = bool(kwargs.get("trusted_connection", False))
        if trusted:
            return SQLServerConnector(server=server, database=database, trusted_connection=True, driver=driver)
        user = kwargs.get("user")
        password = kwargs.get("password")
        if not (user and password):
            raise KeyError("Para SQL Server sin 'trusted_connection' se requieren 'user' y 'password'.")
        return SQLServerConnector(server=server, database=database, user=user, password=password, driver=driver)

    # ---- Oracle ------------------------------------------------------------
    if e == "oracle":
        host, service_name, user, password = _need(kwargs, "host", "service_name", "user", "password")
        port = int(kwargs.get("port", 1521))
        return OracleConnector(host=host, port=port, service_name=service_name, user=user, password=password)

    # ---- Snowflake ---------------------------------------------------------
    if e == "snowflake":
        account, user, password, warehouse, database, schema = _need(
            kwargs, "account", "user", "password", "warehouse", "database", "schema"
        )
        role = kwargs.get("role")
        return SnowflakeConnector(
            account=account, user=user, password=password,
            warehouse=warehouse, database=database, schema=schema, role=role
        )

    # ---- Redshift ----------------------------------------------------------
    if e == "redshift":
        host, dbname, user, password = _need(kwargs, "host", "dbname", "user", "password")
        port = int(kwargs.get("port", 5439))
        sslmode = kwargs.get("sslmode", "require")
        return RedshiftConnector(host=host, port=port, dbname=dbname, user=user, password=password, sslmode=sslmode)

    # -----------------------------------------------------------------------
    raise ValueError(f"Motor no soportado: {engine}")


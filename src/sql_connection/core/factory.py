# src/sql_connection/core/factory.py
from __future__ import annotations

import warnings
from typing import Any, Literal

from ..engines.mysql_connector import MySQLConnector
from ..engines.oracle_connector import OracleConnector
from ..engines.postgres_connector import PostgresConnector
from ..engines.redshift_connector import RedshiftConnector
from ..engines.snowflake_connector import SnowflakeConnector
from ..engines.sqlite_connector import SQLiteConnector
from ..engines.sqlserver_connector import SQLServerConnector
from .base_connector import DatabaseConnector

EngineName = Literal[
    "sqlite",
    "postgres",
    "mysql",
    "sqlserver",
    "oracle",
    "snowflake",
    "redshift",
]


# Engines whose connector expects a legacy database-name kwarg. The unified,
# recommended kwarg across all engines is ``database`` (already native to SQL Server).
_LEGACY_DB_KWARG = {"mysql": "db", "postgres": "dbname", "redshift": "dbname"}


def _normalize_database_kwarg(engine: str, kwargs: dict[str, Any]) -> None:
    """
    Accept a unified ``database=`` argument across engines.

    Legacy per-engine names (``db`` for MySQL, ``dbname`` for Postgres/Redshift)
    keep working but emit a ``DeprecationWarning``. When ``database`` is supplied it
    is mapped to the kwarg the concrete connector expects and takes precedence.
    """
    legacy = _LEGACY_DB_KWARG.get(engine)
    if legacy is None:
        return  # sqlite (no db), sqlserver (already 'database'), oracle (service_name)
    if legacy in kwargs:
        warnings.warn(
            f"Passing '{legacy}=' to get_connector('{engine}', ...) is deprecated; "
            "use 'database=' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
    if "database" in kwargs:
        kwargs[legacy] = kwargs.pop("database")


def _need(kwargs: dict[str, Any], *names: str) -> list[Any]:
    """
    Extract required keyword arguments, raising a clear KeyError when missing.

    Parameters
    ----------
    kwargs : dict[str, Any]
        The keyword args passed into the factory.
    names : str
        Required parameter names.

    Returns
    -------
    list[Any]
        Values corresponding to the required names, in order.

    Raises
    ------
    KeyError
        If any required parameter is missing, a message listing all missing keys
        is raised.
    """
    try:
        return [kwargs[n] for n in names]
    except KeyError as e:
        missing = ", ".join(n for n in names if n not in kwargs)
        raise KeyError(f"Missing required argument(s): {missing}") from e


def get_connector(engine: EngineName, **kwargs: Any) -> DatabaseConnector:
    """
    Factory: return a concrete DatabaseConnector for the requested engine.

    Notes
    -----
    This function validates a minimal set of required parameters per engine and
    normalizes a few optional ones (e.g., ports, timeouts). Secrets should be
    passed in via kwargs; the connectors are responsible for masking secrets in
    `dsn_summary()`.

    The recommended, unified way to name the database is ``database=`` for every
    engine. The legacy per-engine names (``db`` for MySQL, ``dbname`` for
    Postgres/Redshift) still work but emit a ``DeprecationWarning``.

    Parameters
    ----------
    engine : EngineName
        One of: "sqlite", "postgres", "mysql", "sqlserver", "oracle", "snowflake", "redshift".
    **kwargs : Any
        Engine-specific arguments (see below).

    Required kwargs by engine
    -------------------------
    - sqlite:
        path (str), optional: timeout (int, default=5)
    - postgres:
        host (str), dbname (str), user (str), password (str),
        optional: port (int, default=5432), sslmode (str|None)
    - mysql:
        host (str), db (str), user (str), password (str),
        optional: port (int, default=3306)
    - sqlserver:
        server (str), database (str),
        EITHER trusted_connection=True (optional: driver)
        OR user (str) AND password (str) (optional: driver)
        optional: driver (str, default="ODBC Driver 17 for SQL Server")
    - oracle:
        host (str), service_name (str), user (str), password (str),
        optional: port (int, default=1521)
    - snowflake:
        account (str), user (str), password (str),
        warehouse (str), database (str), schema (str),
        optional: role (str|None)
    - redshift:
        host (str), dbname (str), user (str), password (str),
        optional: port (int, default=5439), sslmode (str, default="require")

    Returns
    -------
    DatabaseConnector
        A ready-to-connect connector instance for the chosen engine.

    Raises
    ------
    KeyError
        If required parameters are missing.
    ValueError
        If the engine is not supported.
    """
    e = engine.lower()
    _normalize_database_kwarg(e, kwargs)

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
            return SQLServerConnector(
                server=server, database=database, trusted_connection=True, driver=driver
            )
        user = kwargs.get("user")
        password = kwargs.get("password")
        if not (user and password):
            raise KeyError(
                "For SQL Server without 'trusted_connection', both 'user' and 'password' "
                "are required."
            )
        return SQLServerConnector(
            server=server, database=database, user=user, password=password, driver=driver
        )

    # ---- Oracle ------------------------------------------------------------
    if e == "oracle":
        host, service_name, user, password = _need(
            kwargs, "host", "service_name", "user", "password"
        )
        port = int(kwargs.get("port", 1521))
        return OracleConnector(
            host=host, port=port, service_name=service_name, user=user, password=password
        )

    # ---- Snowflake ---------------------------------------------------------
    if e == "snowflake":
        account, user, password, warehouse, database, schema = _need(
            kwargs, "account", "user", "password", "warehouse", "database", "schema"
        )
        role = kwargs.get("role")
        return SnowflakeConnector(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role,
        )

    # ---- Redshift ----------------------------------------------------------
    if e == "redshift":
        host, dbname, user, password = _need(kwargs, "host", "dbname", "user", "password")
        port = int(kwargs.get("port", 5439))
        sslmode = kwargs.get("sslmode", "require")
        return RedshiftConnector(
            host=host, port=port, dbname=dbname, user=user, password=password, sslmode=sslmode
        )

    # -----------------------------------------------------------------------
    raise ValueError(f"Unsupported engine: {engine!r}")



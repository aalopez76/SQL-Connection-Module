from __future__ import annotations
from typing import Literal

from ..engines.sqlite_connector import SQLiteConnector
from ..engines.postgres_connector import PostgresConnector
from ..engines.mysql_connector import MySQLConnector
from ..engines.sqlserver_connector import SQLServerConnector
from ..engines.oracle_connector import OracleConnector
from ..engines.snowflake_connector import SnowflakeConnector
from ..engines.redshift_connector import RedshiftConnector

EngineName = Literal["sqlite", "postgres", "mysql", "sqlserver", "oracle", "snowflake", "redshift"]

def get_connector(engine: EngineName, **kwargs):
    e = engine.lower()
    if e == "sqlite":
        return SQLiteConnector(path=kwargs["path"])
    elif e == "postgres":
        return PostgresConnector(
            host=kwargs["host"],
            port=int(kwargs.get("port", 5432)),
            dbname=kwargs["dbname"],
            user=kwargs["user"],
            password=kwargs["password"],
            sslmode=kwargs.get("sslmode"),
        )
    elif e == "mysql":
    return MySQLConnector(
        host=kwargs["host"], port=int(kwargs.get("port", 3306)),
        db=kwargs["db"], user=kwargs["user"], password=kwargs["password"]
    )
    raise ValueError(f"Motor no soportado: {engine}")

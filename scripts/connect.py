#!/usr/bin/env python3
"""
CLI de conexión multi-motor para SQL-Connection-Module.

Ejemplos:
  # SQLite
  python scripts/connect.py sqlite --path examples/toys_and_models.sqlite

  # PostgreSQL
  python scripts/connect.py postgres --host localhost --port 5432 \
      --dbname mydb --user myuser --password

  # MySQL/MariaDB
  python scripts/connect.py mysql --host localhost --port 3306 \
      --db mydb --user myuser --password

  # SQL Server (Trusted Connection)
  python scripts/connect.py sqlserver --server localhost --database MyDb --trusted-connection

  # SQL Server (usuario/contraseña)
  python scripts/connect.py sqlserver --server localhost --database MyDb \
      --user sa --password --driver "ODBC Driver 17 for SQL Server"

  # Oracle
  python scripts/connect.py oracle --host localhost --port 1521 \
      --service-name orclpdb1 --user scott --password

  # Snowflake
  python scripts/connect.py snowflake --account xy12345.us-east-1 \
      --user me --password --warehouse WH --database DB --schema PUBLIC --role ANALYST

  # Redshift
  python scripts/connect.py redshift --host mycluster.abcd123.redshift.amazonaws.com \
      --port 5439 --dbname dev --user awsuser --password

Parámetros comunes:
  --query "SELECT 1"  Ejecuta una consulta de SOLO LECTURA y muestra las primeras filas.
  --limit N           Limita las filas impresas de --query (default: 20).
"""

from __future__ import annotations
import argparse
import sys
from getpass import getpass
from typing import Any

from sql_connection import get_connector


def add_common_query_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--query", help="Consulta SQL de solo lectura a ejecutar", default=None)
    p.add_argument("--limit", type=int, default=20, help="Máximo de filas a imprimir con --query (default: 20)")


def add_sqlite(subparsers) -> None:
    sp = subparsers.add_parser("sqlite", help="Conexión a SQLite")
    sp.add_argument("--path", required=True, help="Ruta al .sqlite")
    sp.add_argument("--timeout", type=int, default=5, help="Timeout de conexión en segundos (default: 5)")
    add_common_query_flags(sp)


def add_postgres(subparsers) -> None:
    sp = subparsers.add_parser("postgres", help="Conexión a PostgreSQL")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=5432)
    sp.add_argument("--dbname", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    sp.add_argument("--sslmode", choices=["disable", "require", "verify-full"], default=None)
    add_common_query_flags(sp)


def add_mysql(subparsers) -> None:
    sp = subparsers.add_parser("mysql", help="Conexión a MySQL/MariaDB")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=3306)
    sp.add_argument("--db", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    add_common_query_flags(sp)


def add_sqlserver(subparsers) -> None:
    sp = subparsers.add_parser("sqlserver", help="Conexión a SQL Server (ODBC)")
    sp.add_argument("--server", required=True)
    sp.add_argument("--database", required=True)
    sp.add_argument("--driver", default="ODBC Driver 17 for SQL Server")
    sp.add_argument("--trusted-connection", action="store_true", help="Usar autenticación integrada")
    sp.add_argument("--user", help="Usuario (si no es trusted-connection)")
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    add_common_query_flags(sp)


def add_oracle(subparsers) -> None:
    sp = subparsers.add_parser("oracle", help="Conexión a Oracle")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=1521)
    sp.add_argument("--service-name", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    add_common_query_flags(sp)


def add_snowflake(subparsers) -> None:
    sp = subparsers.add_parser("snowflake", help="Conexión a Snowflake")
    sp.add_argument("--account", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    sp.add_argument("--warehouse", required=True)
    sp.add_argument("--database", required=True)
    sp.add_argument("--schema", required=True)
    sp.add_argument("--role", default=None)
    add_common_query_flags(sp)


def add_redshift(subparsers) -> None:
    sp = subparsers.add_parser("redshift", help="Conexión a Amazon Redshift")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=5439)
    sp.add_argument("--dbname", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument("--password", action="store_true", help="Solicitar password interactivamente")
    sp.add_argument("--sslmode", default="require")
    add_common_query_flags(sp)


def _password_if_flag(args: argparse.Namespace) -> str | None:
    return getpass("Password: ") if getattr(args, "password", False) else None


def _run(engine: str, args: argparse.Namespace) -> int:
    kw: dict[str, Any] = {}

    if engine == "sqlite":
        kw = {"path": args.path, "timeout": args.timeout}

    elif engine == "postgres":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host, "port": args.port, "dbname": args.dbname,
            "user": args.user, "password": (pwd or ""),
            "sslmode": args.sslmode,
        }

    elif engine == "mysql":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host, "port": args.port, "db": args.db,
            "user": args.user, "password": (pwd or ""),
        }

    elif engine == "sqlserver":
        if args.trusted_connection:
            kw = {
                "server": args.server, "database": args.database,
                "driver": args.driver, "trusted_connection": True,
            }
        else:
            if not args.user:
                print("❌ Debes proporcionar --user o usar --trusted-connection.", file=sys.stderr)
                return 2
            pwd = _password_if_flag(args)
            # si no usó --password o quedó vacío, pedimos uno explícitamente
            if not pwd:
                pwd = getpass("Password: ")
            kw = {
                "server": args.server, "database": args.database,
                "user": args.user, "password": pwd,
                "driver": args.driver, "trusted_connection": False,
            }

    elif engine == "oracle":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host, "port": args.port, "service_name": args.service_name,
            "user": args.user, "password": (pwd or ""),
        }

    elif engine == "snowflake":
        pwd = _password_if_flag(args)
        kw = {
            "account": args.account, "user": args.user, "password": (pwd or ""),
            "warehouse": args.warehouse, "database": args.database, "schema": args.schema,
            "role": args.role,
        }

    elif engine == "redshift":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host, "port": args.port, "dbname": args.dbname,
            "user": args.user, "password": (pwd or ""), "sslmode": args.sslmode,
        }

    else:
        print(f"Motor no soportado: {engine}", file=sys.stderr)
        return 2

    # Conectar y mostrar estado
    connector = get_connector(engine, **kw)
    try:
        connector.connect()
        print(f"Conectado: {connector.dsn_summary()} | ping: {'OK' if connector.ping() else 'FAIL'}")

        # Consulta de solo lectura, si se solicita
        if args.query:
            try:
                # Si hay pandas instalado, intenta read_sql para mejor formato
                try:
                    import pandas as pd  # noqa: F401
                    df = connector.read_sql(args.query)
                    if len(df) > args.limit:
                        print(df.head(args.limit))
                        print(f"... ({len(df)} filas; mostrando {args.limit})")
                    else:
                        print(df)
                except Exception:
                    rows = connector.query(args.query)
                    to_show = rows[: args.limit]
                    for r in to_show:
                        print(r)
                    if len(rows) > args.limit:
                        print(f"... ({len(rows)} filas; mostrando {args.limit})")
            except Exception as ex:
                print(f"Error ejecutando consulta: {ex}", file=sys.stderr)
                return 2
        return 0
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Error al conectar: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            connector.close()
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CLI de conexión multi-motor (SQL-Connection-Module)")
    sub = p.add_subparsers(dest="engine", required=True)

    add_sqlite(sub)
    add_postgres(sub)
    add_mysql(sub)
    add_sqlserver(sub)
    add_oracle(sub)
    add_snowflake(sub)
    add_redshift(sub)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    rc = _run(args.engine, args)
    sys.exit(rc)


if __name__ == "__main__":
    main()


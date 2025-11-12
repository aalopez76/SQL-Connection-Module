#!/usr/bin/env python3
"""
Multi-engine SQL connection CLI for SQL-Connection-Module.

Examples
--------
# SQLite
python scripts/connect.py sqlite --path examples/toys_and_models.sqlite

# PostgreSQL
python scripts/connect.py postgres --host localhost --port 5432 \
    --dbname mydb --user myuser --password

# MySQL / MariaDB
python scripts/connect.py mysql --host localhost --port 3306 \
    --db mydb --user myuser --password

# SQL Server (Trusted Connection)
python scripts/connect.py sqlserver --server localhost --database MyDb --trusted-connection

# SQL Server (User/Password)
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

Common flags
------------
--query "SELECT 1"   Execute a READ-ONLY SQL query and print the first rows.
--limit N            Row limit to print for --query (default: 20).
"""

from __future__ import annotations

import argparse
import sys
from getpass import getpass
from typing import Any

from sql_connection import get_connector


# ----------------------------
# Argument builders
# ----------------------------
def add_common_query_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--query",
        help="Read-only SQL to execute after connecting.",
        default=None,
    )
    p.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum rows to print for --query (default: 20).",
    )


def add_sqlite(subparsers) -> None:
    sp = subparsers.add_parser("sqlite", help="Connect to SQLite")
    sp.add_argument("--path", required=True, help="Path to the .sqlite file.")
    sp.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Connection timeout in seconds (default: 5).",
    )
    add_common_query_flags(sp)


def add_postgres(subparsers) -> None:
    sp = subparsers.add_parser("postgres", help="Connect to PostgreSQL")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=5432)
    sp.add_argument("--dbname", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    sp.add_argument(
        "--sslmode",
        choices=["disable", "require", "verify-full"],
        default=None,
    )
    add_common_query_flags(sp)


def add_mysql(subparsers) -> None:
    sp = subparsers.add_parser("mysql", help="Connect to MySQL / MariaDB")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=3306)
    sp.add_argument("--db", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    add_common_query_flags(sp)


def add_sqlserver(subparsers) -> None:
    sp = subparsers.add_parser("sqlserver", help="Connect to SQL Server (ODBC)")
    sp.add_argument("--server", required=True)
    sp.add_argument("--database", required=True)
    sp.add_argument("--driver", default="ODBC Driver 17 for SQL Server")
    sp.add_argument(
        "--trusted-connection",
        action="store_true",
        help="Use integrated authentication.",
    )
    sp.add_argument(
        "--user",
        help="Username (required if not using --trusted-connection).",
    )
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    add_common_query_flags(sp)


def add_oracle(subparsers) -> None:
    sp = subparsers.add_parser("oracle", help="Connect to Oracle")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=1521)
    sp.add_argument("--service-name", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    add_common_query_flags(sp)


def add_snowflake(subparsers) -> None:
    sp = subparsers.add_parser("snowflake", help="Connect to Snowflake")
    sp.add_argument("--account", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    sp.add_argument("--warehouse", required=True)
    sp.add_argument("--database", required=True)
    sp.add_argument("--schema", required=True)
    sp.add_argument("--role", default=None)
    add_common_query_flags(sp)


def add_redshift(subparsers) -> None:
    sp = subparsers.add_parser("redshift", help="Connect to Amazon Redshift")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", type=int, default=5439)
    sp.add_argument("--dbname", required=True)
    sp.add_argument("--user", required=True)
    sp.add_argument(
        "--password",
        action="store_true",
        help="Prompt for password interactively.",
    )
    sp.add_argument("--sslmode", default="require")
    add_common_query_flags(sp)


# ----------------------------
# Helpers
# ----------------------------
def _password_if_flag(args: argparse.Namespace) -> str | None:
    return getpass("Password: ") if getattr(args, "password", False) else None


# ----------------------------
# Runner
# ----------------------------
def _run(engine: str, args: argparse.Namespace) -> int:
    kw: dict[str, Any] = {}

    if engine == "sqlite":
        kw = {"path": args.path, "timeout": args.timeout}

    elif engine == "postgres":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host,
            "port": args.port,
            "dbname": args.dbname,
            "user": args.user,
            "password": (pwd or ""),
            "sslmode": args.sslmode,
        }

    elif engine == "mysql":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host,
            "port": args.port,
            "db": args.db,
            "user": args.user,
            "password": (pwd or ""),
        }

    elif engine == "sqlserver":
        if args.trusted_connection:
            kw = {
                "server": args.server,
                "database": args.database,
                "driver": args.driver,
                "trusted_connection": True,
            }
        else:
            if not args.user:
                print(
                    "❌ You must provide --user or use --trusted-connection.",
                    file=sys.stderr,
                )
                return 2
            pwd = _password_if_flag(args) or getpass("Password: ")
            kw = {
                "server": args.server,
                "database": args.database,
                "user": args.user,
                "password": pwd,
                "driver": args.driver,
                "trusted_connection": False,
            }

    elif engine == "oracle":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host,
            "port": args.port,
            "service_name": args.service_name,
            "user": args.user,
            "password": (pwd or ""),
        }

    elif engine == "snowflake":
        pwd = _password_if_flag(args)
        kw = {
            "account": args.account,
            "user": args.user,
            "password": (pwd or ""),
            "warehouse": args.warehouse,
            "database": args.database,
            "schema": args.schema,
            "role": args.role,
        }

    elif engine == "redshift":
        pwd = _password_if_flag(args)
        kw = {
            "host": args.host,
            "port": args.port,
            "dbname": args.dbname,
            "user": args.user,
            "password": (pwd or ""),
            "sslmode": args.sslmode,
        }

    else:
        print(f"Unsupported engine: {engine}", file=sys.stderr)
        return 2

    # Connect and optionally execute a read-only query
    connector = get_connector(engine, **kw)
    try:
        connector.connect()
        print(
            f"Connected: {connector.dsn_summary()} | ping: "
            f"{'OK' if connector.ping() else 'FAIL'}"
        )

        if args.query:
            try:
                # Prefer pandas if available for nicer tabular output
                try:
                    import pandas as pd  # noqa: F401
                    df = connector.read_sql(args.query)
                    if len(df) > args.limit:
                        print(df.head(args.limit))
                        print(f"... ({len(df)} rows; showing {args.limit})")
                    else:
                        print(df)
                except Exception:
                    rows = connector.query(args.query)
                    to_show = rows[: args.limit]
                    for r in to_show:
                        print(r)
                    if len(rows) > args.limit:
                        print(f"... ({len(rows)} rows; showing {args.limit})")
            except Exception as ex:
                print(f"Error executing query: {ex}", file=sys.stderr)
                return 2

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Connection error: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            connector.close()
        except Exception:
            pass


# ----------------------------
# CLI entrypoint
# ----------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Multi-engine SQL connection CLI (SQL-Connection-Module)"
    )
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

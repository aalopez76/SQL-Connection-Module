#!/usr/bin/env python3
import argparse
from sql_connection import get_connector

def main():
    parser = argparse.ArgumentParser(description="CLI de conexión SQL")
    sub = parser.add_subparsers(dest="engine", required=True)

    p_sqlite = sub.add_parser("sqlite")
    p_sqlite.add_argument("--path", required=True)

    p_pg = sub.add_parser("postgres")
    p_pg.add_argument("--host", default="localhost")
    p_pg.add_argument("--port", type=int, default=5432)
    p_pg.add_argument("--dbname", required=True)
    p_pg.add_argument("--user", required=True)
    p_pg.add_argument("--password", required=True)
    p_pg.add_argument("--sslmode", default=None)

    args = parser.parse_args()

    if args.engine == "sqlite":
        c = get_connector("sqlite", path=args.path)
    elif args.engine == "postgres":
        c = get_connector("postgres", host=args.host, port=args.port,
                          dbname=args.dbname, user=args.user,
                          password=args.password, sslmode=args.sslmode)
    else:
        raise SystemExit("Motor no soportado aún en el CLI.")

    c.connect()
    print(f"Conectado: {c.dsn_summary()} | ping: {'OK' if c.ping() else 'FALLÓ'}")
    c.close()

if __name__ == "__main__":
    main()

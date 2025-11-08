from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generator

try:
    import pandas as pd
except Exception:
    pd = None


class DatabaseConnector(ABC):
    """Interfaz base para conectores SQL."""

    def __init__(self) -> None:
        self.conn = None  # objeto conexión del driver

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    @abstractmethod
    def connect(self) -> None: ...

    def close(self) -> None:
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None

    @property
    def is_connected(self) -> bool:
        return self.conn is not None

    @abstractmethod
    def dsn_summary(self) -> str: ...

    # utilitarios si hay pandas
    def read_sql(self, sql: str, params: dict | None = None):
        if pd is None:
            raise RuntimeError("pandas no está instalado.")
        if not self.conn:
            raise RuntimeError("No hay conexión activa.")
        return pd.read_sql(sql, self.conn, params=params or {})

    def read_sql_chunks(self, sql: str, params: dict | None = None, chunksize: int = 100_000
                        ) -> Generator["pd.DataFrame", None, None]:
        if pd is None:
            raise RuntimeError("pandas no está instalado.")
        if not self.conn:
            raise RuntimeError("No hay conexión activa.")
        return pd.read_sql(sql, self.conn, params=params or {}, chunksize=chunksize)

    def execute(self, sql: str, params: dict | None = None) -> None:
        if not self.conn:
            raise RuntimeError("No hay conexión activa.")
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or {})
            try:
                self.conn.commit()
            except Exception:
                pass
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def ping(self) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1")
            _ = cur.fetchone()
            cur.close()
            return True
        except Exception:
            return False

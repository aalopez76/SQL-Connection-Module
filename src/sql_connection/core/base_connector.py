from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

try:
    import pandas as pd  # type: ignore
except Exception:  # pandas is optional
    pd = None


class DatabaseConnector(ABC):
    """
    Abstract base class for SQL connectors.

    This interface standardizes:
      - Connection lifecycle (connect/close, context manager support)
      - Health checks (ping)
      - Read-only queries returning rows
      - Optional pandas-based reads (full or chunked)
      - Executing DDL/DML without returning rows

    Concrete engines should set `self.conn` to a DB-API 2.0–compatible connection
    (or a close analogue) after `connect()`, and implement `dsn_summary()` to expose
    a non-sensitive connection summary string (e.g., host/port/db, masked secrets).
    """

    def __init__(self) -> None:
        self.conn: Any = None  # DB-API connection object

    # ----------------------------
    # Context manager integration
    # ----------------------------
    def __enter__(self) -> "DatabaseConnector":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        # Returning False propagates any exception to the caller
        return False

    # ----------------------------
    # Connection lifecycle
    # ----------------------------
    @abstractmethod
    def connect(self) -> None:
        """Establish an underlying driver connection and assign it to `self.conn`."""
        ...

    def close(self) -> None:
        """Close the underlying connection if open."""
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None

    @property
    def is_connected(self) -> bool:
        """Return True if an underlying connection is present."""
        return self.conn is not None

    @abstractmethod
    def dsn_summary(self) -> str:
        """
        Return a short, non-sensitive DSN-like summary string for logging/display.
        Secrets MUST be masked (e.g., password).
        """
        ...

    # ----------------------------
    # Internals
    # ----------------------------
    def _ensure_connected(self) -> None:
        if not self.conn:
            raise RuntimeError("No active connection. Call `connect()` first.")

    # ----------------------------
    # Pandas-based reads (optional)
    # ----------------------------
    def read_sql(self, sql: str, params: Optional[dict] = None):
        """
        Read a full result set into a pandas DataFrame.

        Requires pandas to be installed. Raises a RuntimeError if pandas is absent
        or if there is no active connection.
        """
        if pd is None:
            raise RuntimeError("pandas is not installed. Install `pandas` to use read_sql().")
        self._ensure_connected()
        return pd.read_sql(sql, self.conn, params=params or {})

    def read_sql_chunks(
        self,
        sql: str,
        params: Optional[dict] = None,
        chunksize: int = 100_000,
    ) -> Generator["pd.DataFrame", None, None]:
        """
        Stream results into chunked pandas DataFrames.

        Useful for large result sets that cannot fit into memory.
        """
        if pd is None:
            raise RuntimeError("pandas is not installed. Install `pandas` to use read_sql_chunks().")
        self._ensure_connected()
        return pd.read_sql(sql, self.conn, params=params or {}, chunksize=chunksize)

    # ----------------------------
    # Executing statements (no rows)
    # ----------------------------
    def execute(self, sql: str, params: Optional[dict] = None) -> None:
        """
        Execute a DDL/DML statement (no rows expected).

        Commits if the underlying driver is transactional. Swallows driver-specific
        commit errors (e.g., autocommit modes) without failing the call.
        """
        self._ensure_connected()
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or {})
            try:
                self.conn.commit()
            except Exception:
                # Some drivers are autocommit or do not require explicit commit
                pass
        finally:
            try:
                cur.close()
            except Exception:
                pass

    # ----------------------------
    # Read-only query returning rows
    # ----------------------------
    def query(self, sql: str, params: Optional[dict] = None) -> list[tuple[Any, ...]]:
        """
        Execute a read-only query and return all rows as a list of tuples.

        For tabular analysis, prefer `read_sql()` when pandas is available.
        """
        self._ensure_connected()
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or {})
            rows = cur.fetchall()
            return rows
        finally:
            try:
                cur.close()
            except Exception:
                pass

    # ----------------------------
    # Health check
    # ----------------------------
    def ping(self) -> bool:
        """
        Perform a lightweight health check against the database.

        Engines may override this if they require an engine-specific probe.
        """
        try:
            self._ensure_connected()
            cur = self.conn.cursor()
            try:
                cur.execute("SELECT 1")
                _ = cur.fetchone()
                return True
            finally:
                try:
                    cur.close()
                except Exception:
                    pass
        except Exception:
            return False



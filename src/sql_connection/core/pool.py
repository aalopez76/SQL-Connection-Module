"""A small, engine-agnostic connection pool for DatabaseConnector instances."""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from .base_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Thread-safe pool of connected ``DatabaseConnector`` instances.

    Connectors are created lazily via ``factory`` (typically a ``get_connector(...)``
    call wrapped in a lambda) up to ``max_size`` and then reused. Acquire/release is
    best done through the ``connection()`` context manager.

    Parameters
    ----------
    factory : Callable[[], DatabaseConnector]
        Builds a fresh, *not yet connected* connector. ``connect()`` is called by
        the pool.
    max_size : int
        Maximum number of live connections (>= 1).
    pre_ping : bool
        If True, ``ping()`` an idle connection on acquire and transparently replace
        it if the check fails.

    Examples
    --------
    >>> pool = ConnectionPool(
    ...     lambda: get_connector("sqlite", path="app.sqlite"), max_size=4
    ... )
    >>> with pool.connection() as conn:
    ...     rows = conn.query("SELECT 1")
    >>> pool.closeall()
    """

    def __init__(
        self,
        factory: Callable[[], DatabaseConnector],
        max_size: int = 5,
        pre_ping: bool = False,
    ) -> None:
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        self._factory = factory
        self._max_size = max_size
        self._pre_ping = pre_ping
        self._idle: deque[DatabaseConnector] = deque()
        self._created = 0
        self._closed = False
        self._cond = threading.Condition()

    # ------------------------------------------------------------------
    def acquire(self, timeout: float | None = None) -> DatabaseConnector:
        """
        Check out a connected connector, creating one if capacity allows.

        Blocks until a connector is available or ``timeout`` seconds elapse.

        Raises
        ------
        RuntimeError
            If the pool is closed.
        TimeoutError
            If no connector becomes available within ``timeout``.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        with self._cond:
            while True:
                if self._closed:
                    raise RuntimeError("Pool is closed")

                while self._idle:
                    conn = self._idle.popleft()
                    if self._pre_ping and not conn.ping():
                        self._discard_locked(conn)
                        continue
                    return conn

                if self._created < self._max_size:
                    conn = self._factory()
                    conn.connect()
                    self._created += 1
                    return conn

                # Pool exhausted: wait for a release.
                remaining = None if deadline is None else deadline - time.monotonic()
                if remaining is not None and remaining <= 0:
                    raise TimeoutError(
                        f"No connection available within {timeout}s "
                        f"(max_size={self._max_size})"
                    )
                self._cond.wait(remaining)

    def release(self, conn: DatabaseConnector) -> None:
        """Return a connector to the pool (or close it if the pool is closed)."""
        with self._cond:
            if self._closed:
                self._discard_locked(conn)
            else:
                self._idle.append(conn)
            self._cond.notify()

    @contextmanager
    def connection(self, timeout: float | None = None) -> Iterator[DatabaseConnector]:
        """Acquire a connector for the duration of the ``with`` block."""
        conn = self.acquire(timeout=timeout)
        try:
            yield conn
        finally:
            self.release(conn)

    def closeall(self) -> None:
        """Close every idle connection and mark the pool closed."""
        with self._cond:
            self._closed = True
            while self._idle:
                self._discard_locked(self._idle.popleft())
            self._cond.notify_all()

    # ------------------------------------------------------------------
    def _discard_locked(self, conn: DatabaseConnector) -> None:
        """Close a connector and free its slot. Caller must hold the lock."""
        try:
            conn.close()
        except Exception:  # pragma: no cover - close is best-effort
            logger.debug("Error closing pooled connection", exc_info=True)
        self._created = max(0, self._created - 1)

    @property
    def size(self) -> int:
        """Number of live (created and not discarded) connections."""
        return self._created

    @property
    def idle(self) -> int:
        """Number of connections currently checked in and available."""
        return len(self._idle)

# tests/test_pool.py
import pytest

from sql_connection.core.pool import ConnectionPool
from sql_connection.engines.sqlite_connector import SQLiteConnector


def _factory():
    return SQLiteConnector(":memory:")


def test_pool_reuses_connection():
    pool = ConnectionPool(_factory, max_size=2)
    try:
        c1 = pool.acquire()
        pool.release(c1)
        c2 = pool.acquire()
        assert c1 is c2  # reused, not a new connection
        assert pool.size == 1
    finally:
        pool.closeall()


def test_pool_grows_to_max_and_times_out():
    pool = ConnectionPool(_factory, max_size=2)
    try:
        a = pool.acquire()
        b = pool.acquire()
        assert pool.size == 2
        assert a is not b
        with pytest.raises(TimeoutError):
            pool.acquire(timeout=0.05)
    finally:
        pool.closeall()


def test_pool_context_manager_releases():
    pool = ConnectionPool(_factory, max_size=1)
    try:
        with pool.connection() as conn:
            assert conn.is_connected
        # released back -> can acquire again immediately
        with pool.connection(timeout=0.1) as conn2:
            assert conn2.is_connected
        assert pool.size == 1
    finally:
        pool.closeall()


def test_pool_closeall_blocks_further_use():
    pool = ConnectionPool(_factory, max_size=1)
    pool.acquire()
    pool.closeall()
    with pytest.raises(RuntimeError):
        pool.acquire()


def test_pool_pre_ping_replaces_dead_connection():
    pool = ConnectionPool(_factory, max_size=1, pre_ping=True)
    try:
        c1 = pool.acquire()
        c1.close()          # simulate a dropped connection
        pool.release(c1)
        c2 = pool.acquire()  # pre_ping discards c1, builds a fresh one
        assert c2.is_connected
        assert c2 is not c1
    finally:
        pool.closeall()


def test_pool_invalid_max_size():
    with pytest.raises(ValueError):
        ConnectionPool(_factory, max_size=0)

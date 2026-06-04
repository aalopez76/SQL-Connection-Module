# tests/test_retries.py
import pytest

from sql_connection.core.base_connector import DatabaseConnector
from sql_connection.engines.sqlite_connector import SQLiteConnector


class _FlakyConnector(DatabaseConnector):
    """Fails `fail_times` before succeeding; counts connect() calls."""

    def __init__(self, fail_times: int):
        super().__init__()
        self.fail_times = fail_times
        self.calls = 0

    def connect(self) -> None:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError("transient")
        self.conn = object()  # pretend we connected

    def dsn_summary(self) -> str:
        return "flaky://"


def test_retries_succeeds_after_transient_failures():
    c = _FlakyConnector(fail_times=2)
    c.connect_with_retries(attempts=3, base_delay=0, backoff=1)
    assert c.is_connected
    assert c.calls == 3


def test_retries_exhausted_reraises_last_error():
    c = _FlakyConnector(fail_times=5)
    with pytest.raises(ConnectionError):
        c.connect_with_retries(attempts=3, base_delay=0)
    assert c.calls == 3


def test_retries_invalid_attempts():
    c = _FlakyConnector(fail_times=0)
    with pytest.raises(ValueError):
        c.connect_with_retries(attempts=0)


def test_retries_only_catches_listed_exceptions():
    c = _FlakyConnector(fail_times=1)
    # ConnectionError is not a TypeError, so it should propagate immediately.
    with pytest.raises(ConnectionError):
        c.connect_with_retries(attempts=3, base_delay=0, exceptions=(TypeError,))
    assert c.calls == 1


def test_retries_real_sqlite_first_try():
    c = SQLiteConnector(":memory:")
    try:
        c.connect_with_retries(attempts=2, base_delay=0)
        assert c.ping() is True
    finally:
        c.close()

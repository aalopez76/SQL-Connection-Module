import logging
import sqlite3

from ..core.base_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SQLiteConnector(DatabaseConnector):
    def __init__(self, path: str, timeout: int = 5):
        super().__init__()
        self.path = path
        self.timeout = timeout

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.path, timeout=self.timeout)
        self.conn.row_factory = sqlite3.Row
        logger.debug("Connected: %s", self.dsn_summary())

    def dsn_summary(self) -> str:
        return f"sqlite:///{self.path}"

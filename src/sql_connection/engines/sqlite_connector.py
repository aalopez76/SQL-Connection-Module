import sqlite3
from ..core.base_connector import DatabaseConnector

class SQLiteConnector(DatabaseConnector):
    def __init__(self, path: str, timeout: int = 5):
        super().__init__()
        self.path = path
        self.timeout = timeout

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.path, timeout=self.timeout)
        self.conn.row_factory = sqlite3.Row

    def dsn_summary(self) -> str:
        return f"sqlite:///{self.path}"

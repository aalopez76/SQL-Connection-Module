import logging

from ..core.base_connector import DatabaseConnector
from ..core.utils import mask_secret

try:
    import pymysql
except Exception:
    pymysql = None

logger = logging.getLogger(__name__)


class MySQLConnector(DatabaseConnector):
    def __init__(self, host: str, port: int, db: str, user: str, password: str):
        super().__init__()
        self.host, self.port, self.db = host, port, db
        self.user, self.password = user, password

    def connect(self) -> None:
        if pymysql is None:
            raise RuntimeError("pymysql no está instalado.")
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            db=self.db,
            user=self.user,
            password=self.password,
            charset="utf8mb4",
        )
        logger.debug("Connected: %s", self.dsn_summary())

    def dsn_summary(self) -> str:
        return (
            f"mysql://{self.user}:{mask_secret(self.password)}@"
            f"{self.host}:{self.port}/{self.db}"
        )

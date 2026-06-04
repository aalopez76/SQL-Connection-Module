import logging

from ..core.base_connector import DatabaseConnector
from ..core.utils import mask_secret

try:
    import psycopg2
except Exception:
    psycopg2 = None

logger = logging.getLogger(__name__)


class RedshiftConnector(DatabaseConnector):
    def __init__(
        self,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
        sslmode: str = "require",
    ):
        super().__init__()
        self.host, self.port, self.dbname = host, port, dbname
        self.user, self.password, self.sslmode = user, password, sslmode

    def connect(self) -> None:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary no está instalado.")
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            sslmode=self.sslmode,
        )
        logger.debug("Connected: %s", self.dsn_summary())

    def dsn_summary(self) -> str:
        return (
            f"redshift://{self.user}:{mask_secret(self.password)}@"
            f"{self.host}:{self.port}/{self.dbname}?sslmode={self.sslmode}"
        )

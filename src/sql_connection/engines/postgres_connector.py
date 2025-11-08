from typing import Optional
from ..core.base_connector import DatabaseConnector
from ..core.utils import mask_secret

try:
    import psycopg2
    import psycopg2.extras
except Exception:
    psycopg2 = None


class PostgresConnector(DatabaseConnector):
    def __init__(self, host: str, port: int, dbname: str,
                 user: str, password: str,
                 sslmode: Optional[str] = None, connect_timeout: int = 10):
        super().__init__()
        self.host, self.port, self.dbname = host, port, dbname
        self.user, self.password = user, password
        self.sslmode, self.connect_timeout = sslmode, connect_timeout

    def connect(self) -> None:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary no está instalado.")
        kwargs = dict(
            host=self.host, port=self.port, dbname=self.dbname,
            user=self.user, password=self.password,
            connect_timeout=self.connect_timeout,
            cursor_factory=getattr(psycopg2.extras, "DictCursor", None),
        )
        if self.sslmode:
            kwargs["sslmode"] = self.sslmode
        self.conn = psycopg2.connect(**kwargs)

    def dsn_summary(self) -> str:
        ssl = f"?sslmode={self.sslmode}" if self.sslmode else ""
        return f"postgresql://{self.user}:{mask_secret(self.password)}@{self.host}:{self.port}/{self.dbname}{ssl}"

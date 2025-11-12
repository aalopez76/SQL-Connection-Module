# src/sql_connection/engines/oracle_connector.py
from ..core.base_connector import DatabaseConnector
from ..core.utils import mask_secret

try:
    import oracledb
except Exception:
    oracledb = None


class OracleConnector(DatabaseConnector):
    def __init__(self, host: str, port: int, service_name: str, user: str, password: str):
        super().__init__()
        self.host = host
        self.port = port
        self.service_name = service_name
        self.user = user
        self.password = password

    def connect(self) -> None:
        if oracledb is None:
            raise RuntimeError("oracledb no está instalado.")
        dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
        self.conn = oracledb.connect(user=self.user, password=self.password, dsn=dsn)

    def dsn_summary(self) -> str:
        return (
            f"oracle://{self.user}:{mask_secret(self.password)}@"
            f"{self.host}:{self.port}/{self.service_name}"
        )

    def ping(self) -> bool:
        """Ping compatible con Oracle."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 1 FROM DUAL")
            _ = cur.fetchone()
            cur.close()
            return True
        except Exception:
            return False


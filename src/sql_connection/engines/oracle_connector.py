from ..core.base_connector import DatabaseConnector
try:
    import oracledb
except Exception:
    oracledb = None

class OracleConnector(DatabaseConnector):
    def __init__(self, host: str, port: int, service_name: str, user: str, password: str):
        super().__init__()
        self.host, self.port, self.service_name = host, port, service_name
        self.user, self.password = user, password

    def connect(self) -> None:
        if oracledb is None:
            raise RuntimeError("oracledb no está instalado.")
        dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
        self.conn = oracledb.connect(user=self.user, password=self.password, dsn=dsn)

    def dsn_summary(self) -> str:
        return f"oracle://{self.user}@{self.host}:{self.port}/{self.service_name}"

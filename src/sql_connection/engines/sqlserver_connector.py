from ..core.base_connector import DatabaseConnector
from ..core.utils import mask_secret

try:
    import pyodbc
except Exception:
    pyodbc = None


class SQLServerConnector(DatabaseConnector):
    def __init__(
        self,
        server: str,
        database: str,
        user: str | None = None,
        password: str | None = None,
        driver: str = "ODBC Driver 17 for SQL Server",
        trusted_connection: bool = False,
    ):
        super().__init__()
        self.server, self.database = server, database
        self.user, self.password = user, password
        self.driver, self.trusted = driver, trusted_connection

    def connect(self) -> None:
        if pyodbc is None:
            raise RuntimeError("pyodbc no está instalado.")

        if self.trusted:
            conn_str = (
                f"DRIVER={{{self.driver}}};SERVER={self.server};"
                f"DATABASE={self.database};Trusted_Connection=yes;"
            )
        else:
            if not (self.user and self.password):
                raise RuntimeError("Se requieren 'user' y 'password' para SQL Server no confiado.")
            conn_str = (
                f"DRIVER={{{self.driver}}};SERVER={self.server};"
                f"DATABASE={self.database};UID={self.user};PWD={self.password};"
            )
        self.conn = pyodbc.connect(conn_str)

    def dsn_summary(self) -> str:
        if self.trusted:
            who = "trusted"
            return f"mssql://{who}@{self.server}/{self.database}"
        return (
            f"mssql://{self.user}:{mask_secret(self.password)}@"
            f"{self.server}/{self.database}"
        )

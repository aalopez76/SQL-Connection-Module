from ..core.base_connector import DatabaseConnector
try:
    import snowflake.connector as sf
except Exception:
    sf = None

class SnowflakeConnector(DatabaseConnector):
    def __init__(self, account: str, user: str, password: str, warehouse: str, database: str, schema: str, role: str | None = None):
        super().__init__()
        self.account, self.user, self.password = account, user, password
        self.warehouse, self.database, self.schema, self.role = warehouse, database, schema, role

    def connect(self) -> None:
        if sf is None:
            raise RuntimeError("snowflake-connector-python no está instalado.")
        kwargs = dict(account=self.account, user=self.user, password=self.password,
                      warehouse=self.warehouse, database=self.database, schema=self.schema)
        if self.role:
            kwargs["role"] = self.role
        self.conn = sf.connect(**kwargs)

    def dsn_summary(self) -> str:
        role = f"&role={self.role}" if self.role else ""
        return f"snowflake://{self.user}@{self.account}/{self.database}/{self.schema}?warehouse={self.warehouse}{role}"

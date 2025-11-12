# Test 1: Importación mínima
def test_imports():
    import sql_connection
    from sql_connection import get_connector
    assert callable(get_connector)


# Test 2: Conexión funcional con SQLite (solo lectura)
from sql_connection.engines.sqlite_connector import SQLiteConnector
import os

def test_sqlite_connection_readonly():
    # Ruta a la base de datos de ejemplo (ajústala si estás en otro entorno)
    db_path = os.path.abspath("examples/toys_and_models.sqlite")
    assert os.path.exists(db_path), f"No se encontró la base de datos: {db_path}"

    c = SQLiteConnector(db_path)
    c.connect()
    assert c.is_connected, "No se estableció la conexión SQLite"

    # Verificar una consulta simple (por ejemplo, leer nombres de tablas)
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    assert isinstance(result, list), "La consulta no devolvió una lista"
    assert len(result) > 0, "No se encontraron tablas en la base de datos"

    # Validar ping
    assert c.ping() is True, "Ping falló"

    # Cerrar conexión
    c.close()
    assert not c.is_connected, "La conexión no se cerró correctamente"


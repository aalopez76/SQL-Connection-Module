# tests/test_smoke.py

import os
import pytest


def test_imports():
    """Smoke test mínimo: el paquete y la fábrica se importan correctamente."""
    import sql_connection  # noqa: F401
    from sql_connection import get_connector  # noqa: F401
    assert callable(get_connector)


from sql_connection.engines.sqlite_connector import SQLiteConnector


@pytest.mark.skipif(
    not os.path.exists(os.path.abspath("examples/toys_and_models.sqlite")),
    reason="Base de ejemplo no encontrada: examples/toys_and_models.sqlite",
)
def test_sqlite_connection_readonly():
    """
    Verifica una conexión real de SOLO LECTURA contra la base de ejemplo.
    - Abre conexión
    - Lista tablas con query()
    - Verifica ping
    - Cierra conexión
    """
    db_path = os.path.abspath("examples/toys_and_models.sqlite")
    assert os.path.exists(db_path), f"No se encontró la base: {db_path}"

    c = SQLiteConnector(db_path)
    c.connect()
    try:
        assert c.is_connected, "No se estableció la conexión SQLite"

        # Solo lectura: listar tablas
        rows = c.query("SELECT name FROM sqlite_master WHERE type='table'")
        assert isinstance(rows, list), "La consulta no devolvió una lista"
        assert len(rows) > 0, "No se encontraron tablas en la base de datos"

        # Ping debe responder True
        assert c.ping() is True, "Ping falló"
    finally:
        c.close()
        assert not c.is_connected, "La conexión no se cerró correctamente"

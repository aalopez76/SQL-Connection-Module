# tests/conftest.py
import os
import pytest

@pytest.fixture(scope="session")
def example_db_path() -> str:
    """
    Fixture que localiza la base de datos de ejemplo.

    Lee la variable de entorno SQL_CONN_EXAMPLE_DB, o usa la ruta por defecto.
    """
    db_path = os.environ.get("SQL_CONN_EXAMPLE_DB", "examples/toys_and_models.sqlite")
    abs_path = os.path.abspath(db_path)
    if not os.path.exists(abs_path):
        pytest.skip(f"No se encontró la base de ejemplo: {abs_path}")
    return abs_path

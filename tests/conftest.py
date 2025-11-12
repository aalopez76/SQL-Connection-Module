# tests/conftest.py
import os
import importlib
import pytest


@pytest.fixture(scope="session")
def example_db_path() -> str:
    """
    Ruta absoluta a la base de ejemplo.
    SQL_CONN_EXAMPLE_DB puede sobreescribir la ruta por defecto.
    """
    db_path = os.environ.get("SQL_CONN_EXAMPLE_DB", "examples/toys_and_models.sqlite")
    abs_path = os.path.abspath(db_path)
    if not os.path.exists(abs_path):
        pytest.skip(f"No se encontró la base de ejemplo: {abs_path}")
    return abs_path


def have_module(modname: str) -> bool:
    try:
        importlib.import_module(modname)
        return True
    except Exception:
        return False


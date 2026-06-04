from importlib.metadata import PackageNotFoundError, version

from .core.base_connector import DatabaseConnector
from .core.factory import get_connector

try:
    __version__ = version("sql-connection-module")
except PackageNotFoundError:  # package not installed (e.g. running from source tree)
    __version__ = "0.0.0+unknown"

__all__ = ["get_connector", "DatabaseConnector", "__version__"]

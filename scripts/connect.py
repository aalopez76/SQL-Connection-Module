#!/usr/bin/env python3
"""
Backwards-compatible wrapper for the SQL-Connection-Module CLI.

The implementation now lives in ``sql_connection.cli`` and is also installed as
the ``sql-connect`` console script. This file is kept so existing invocations
(``python scripts/connect.py ...``) keep working.
"""
from __future__ import annotations

import os
import sys

# Allow running directly from a source checkout without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sql_connection.cli import main  # noqa: E402

if __name__ == "__main__":
    main()

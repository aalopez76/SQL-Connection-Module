# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## What this is

`sql-connection-module` is a **multi-engine SQL connector library** for Python. It exposes a
unified OOP API (abstract `DatabaseConnector` + a `get_connector` factory) over SQLite,
PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, Snowflake and Redshift, plus a small CLI.

It is a **library**, not an ML/analytics project: there is no model, no training data and no
pipeline orchestration (DVC/MLflow are intentionally absent). The example SQLite database is a
committed test fixture.

## Stack & layout

- Python ≥ 3.10, `src/` layout, packaged with **setuptools** (PEP 621 `pyproject.toml`).
- Core has **no hard runtime dependencies**; `pandas` and every DB driver are optional *extras*.
- Tooling: **pytest** (+pytest-cov), **ruff** (lint+format), **mypy**, **pip-tools** (lock), **build**.

```
src/sql_connection/
  __init__.py            # public exports + __version__
  py.typed               # PEP 561 typing marker
  cli.py                 # CLI implementation (entry point: sql-connect)
  core/
    base_connector.py    # DatabaseConnector ABC (lifecycle, read_sql, query, execute,
                         #   ping, connect_with_retries)
    factory.py           # get_connector(engine, **kwargs) + database= alias normalization
    pool.py              # ConnectionPool (thread-safe, engine-agnostic)
    utils.py             # mask_secret()
  engines/               # one connector module per engine
scripts/connect.py       # thin backward-compatible CLI wrapper
tests/                   # pytest suite (driver tests auto-skip when driver absent)
examples/                # demo notebook + toys_and_models.sqlite fixture
docs/                    # AUDIT.md, REFACTOR_PLAN.md
```

## Common commands

Use the venv interpreter on Windows (`make PY=.venv/Scripts/python.exe <target>`), or activate it.

| Action | Make target | Raw command |
|--------|-------------|-------------|
| Install (dev+pandas) | `make install` | `pip install -e ".[dev,pandas]"` |
| Install everything | `make install-all` | `pip install -e ".[dev,all]"` |
| Run tests | `make test` | `pytest` |
| Tests + coverage | `make cov` | `pytest --cov=sql_connection --cov-report=term-missing` |
| Lint | `make lint` | `ruff check .` |
| Format / autofix | `make format` | `ruff check --fix . && ruff format .` |
| Type check | `make typecheck` | `mypy src` |
| Rebuild lock | `make lock` | `pip-compile --extra dev --extra all --output-file requirements.lock pyproject.toml` |
| Build dist | `make build` | `python -m build` |
| Run CLI demo | `make run` | `python scripts/connect.py sqlite --path examples/toys_and_models.sqlite --query "..."` |

Reproducible env: `pip install -r requirements.lock`.

## Conventions

- **Add a new engine**: create `engines/<name>_connector.py` subclassing `DatabaseConnector`
  (implement `connect()` and `dsn_summary()`), import its optional driver defensively
  (`try/except` → `None`, raise a clear `RuntimeError` in `connect()`), then register it in
  `factory.py` (`EngineName` Literal + a branch using `_need(...)`).
- **Secrets**: never put raw passwords in `dsn_summary()` — always `mask_secret(...)`. There is a
  test (`tests/test_masking.py`) that fails if a password leaks.
- **Database kwarg**: prefer the unified `database=` in new code; `db`/`dbname` are deprecated aliases.
- **Logging**: use `logging.getLogger(__name__)`; never log query params (may contain secrets).
  The CLI is the only place that prints data for the user.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`, `build:`).
- **Before pushing**: `ruff check .`, `mypy src`, `pytest` must all pass (mirrors CI).

## Testing notes

Tests that need a DB driver are skipped automatically when the driver is not installed, so the
suite is green on a minimal install. Core behaviour is exercised against in-memory SQLite.

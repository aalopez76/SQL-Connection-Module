# SQL-Connection-Module

### Enterprise-Level Multi-Engine SQL Connector in Python

`SQL-Connection-Module` is a modular, Object-Oriented Python package designed to connect and interact with multiple relational database engines (SQLite, PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, Redshift) through a unified, extensible interface.

It provides a **production-ready foundation** for analytics, data science, and ETL projects requiring portable, secure, and maintainable database access.

> 🔌 **In production:** this connector powers the data engine of the
> [**Executive KPI Dashboard**](https://github.com/aalopez76/Executive_Dashboard)
> ([live demo](https://huggingface.co/spaces/aalpzp/Executive_KPI_Dashboard)).

---

## Overview

Modern data workflows demand flexibility — analysts and data scientists must query heterogeneous systems without rewriting connection logic.  
This module abstracts those differences through a **consistent OOP API**, exposing connection, execution, and reading utilities adaptable to any supported SQL backend.

### **Key Features**
-  Unified connection API across engines (SQLite, PostgreSQL, MySQL, etc.)  
-  Clean OOP architecture with extensible `DatabaseConnector` base class  
-  Safe credential masking and context-managed connections  
-  Optional `pandas` integration (`read_sql`, chunked reads)  
-  Modular engine registration via lightweight factory pattern  
-  Command-line interface (CLI) for quick testing  
-  Tested and structured for enterprise maintainability  

---

## Project Structure

```bash
SQL-Connection-Module/
├─ src/sql_connection/           # Core library (base + engine connectors)
│  ├─ __init__.py                # Public exports + __version__
│  ├─ py.typed                   # PEP 561 typing marker
│  ├─ cli.py                     # CLI implementation (entry point: sql-connect)
│  ├─ core/                      # Abstract interfaces, utilities, factory
│  │  ├─ base_connector.py
│  │  ├─ factory.py
│  │  └─ utils.py
│  └─ engines/                   # Implementations per SQL engine
│     ├─ sqlite_connector.py
│     ├─ postgres_connector.py
│     ├─ mysql_connector.py
│     ├─ sqlserver_connector.py
│     ├─ oracle_connector.py
│     ├─ snowflake_connector.py
│     └─ redshift_connector.py
│
├─ scripts/connect.py            # Backward-compatible CLI wrapper
├─ examples/connect.ipynb        # Jupyter demo – read-only example
├─ tests/                        # pytest suite (smoke, factory, base, masking, cli, errors)
├─ docs/                         # AUDIT.md, REFACTOR_PLAN.md
├─ .github/workflows/ci.yml      # CI: ruff + mypy + pytest (Python 3.10–3.12)
├─ Makefile                      # install / test / lint / format / typecheck / build / ...
├─ requirements.lock             # Pinned dependency set (pip-tools)
├─ .env.example                  # Per-engine credential template
├─ pyproject.toml                # Project metadata, extras, tooling config
├─ CLAUDE.md                     # Repo guide for Claude Code / contributors
├─ LICENSE                       # MIT License
└─ .gitignore
```

## Installation

The core package has **no hard runtime dependencies** — `pandas` and the database
drivers are optional *extras*. Install only what you need.

###  Clone and install in editable mode

```bash
git clone https://github.com/aalopez76/SQL-Connection-Module.git
cd SQL-Connection-Module

# (recommended) create an isolated virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate

pip install -e .
```

###  Verify installation

Run a quick import test to confirm everything is working:
```bash
python -c "from sql_connection import get_connector, __version__; print('Import OK', __version__)"
```

###  Optional dependencies (extras)

Every extra below is declared in `pyproject.toml`, so these commands work as-is:

```bash
pip install -e ".[pandas]"      # DataFrame support (read_sql / read_sql_chunks)
pip install -e ".[postgres]"    # PostgreSQL  (psycopg2-binary)
pip install -e ".[mysql]"       # MySQL / MariaDB  (pymysql)
pip install -e ".[mssql]"       # SQL Server  (pyodbc — requires an ODBC driver)
pip install -e ".[oracle]"      # Oracle  (oracledb)
pip install -e ".[snowflake]"   # Snowflake  (snowflake-connector-python)
pip install -e ".[redshift]"    # Amazon Redshift  (psycopg2-binary)
pip install -e ".[all]"         # All drivers + pandas
pip install -e ".[dev]"         # Dev toolchain (pytest, pytest-cov, ruff, mypy, ...)
```

###  Reproducible environment

A fully pinned dependency set is committed in `requirements.lock` (generated with
`pip-tools`). To recreate the exact development environment:

```bash
pip install -r requirements.lock
```

Regenerate it after changing dependencies:

```bash
pip-compile --extra dev --extra all --output-file requirements.lock pyproject.toml
```



## Usage Examples
a) From Python
```python
from sql_connection import get_connector

conn = get_connector("sqlite", path="examples/toys_and_models.sqlite")

with conn:
    print("Connected:", conn.dsn_summary())
    print("Ping:", conn.ping())
    df = conn.read_sql("SELECT customerName, country FROM customers LIMIT 5;")
    print(df)
```

b) From Command Line (CLI)

After installation the `sql-connect` command is available and is equivalent to
`python scripts/connect.py` (e.g. `sql-connect sqlite --path ... --query "..."`).
Add `--verbose` for debug logging.

SQLite example

-List tables (recommended for smoke test):

```bash
python scripts/connect.py sqlite --path examples/toys_and_models.sqlite \
  --query "SELECT name FROM sqlite_master WHERE type='table';"
```

-Query specific data:

```bash
python scripts/connect.py sqlite --path examples/toys_and_models.sqlite --query "SELECT * FROM customers LIMIT 5"
```

 PostgreSQL example:

```bash
python scripts/connect.py postgres --host localhost --port 5432 \
  --dbname mydb --user myuser --password --query "SELECT COUNT(*) FROM sales"
```


## Example Notebook

Open examples/connect.ipynb
 to explore:

- Connecting to SQLite

- Listing tables

- Querying and filtering data

- Parameterized SQL examples

The notebook demonstrates how this module integrates easily into analytics workflows, allowing data scientists to query, explore, and visualize data programmatically without switching tools.

## Resilience & Pooling

For pipeline/production use, connections can be retried with exponential backoff and
reused through a small, engine-agnostic pool:

```python
from sql_connection import get_connector, ConnectionPool

# Retry transient connection failures
conn = get_connector("postgres", host="db", database="app", user="u", password="p")
conn.connect_with_retries(attempts=5, base_delay=0.5, backoff=2.0)

# Reuse connections via a thread-safe pool
pool = ConnectionPool(
    lambda: get_connector("sqlite", path="app.sqlite"),
    max_size=8,
    pre_ping=True,   # validate idle connections on checkout
)
with pool.connection() as c:
    rows = c.query("SELECT 1")
pool.closeall()
```

## Configuration & Credentials

Never hard-code credentials. Copy `.env.example` to `.env` (git-ignored) and load the
values from the environment in your own code or pass them to `get_connector(...)`:

```bash
cp .env.example .env   # then edit with your real values
```

Passwords are always **masked** in `dsn_summary()` output, so connection summaries are
safe to log.

## Running the Tests

```bash
pip install -e ".[dev,pandas]"   # test deps (add the driver extras you want to exercise)
pytest                            # run the suite
pytest --cov=sql_connection       # with coverage
```

Engine tests for drivers that are not installed are **skipped automatically**, so the
suite is green on a minimal install. The example SQLite database
(`examples/toys_and_models.sqlite`) is committed as a small, self-contained test fixture
(no external data tooling such as DVC is required for this library).

## Design Principles

-OOP architecture: promotes reuse and extension across database types.

-Factory pattern: decouples engine selection from implementation.

-Error safety: controlled connection lifecycle and contextual cleanup.

-Scalability: suitable for production ETL, dashboards, or research analysis.

-Read-only by default: safer for analytics environments.


## Summary

This repository serves as a template and foundation for enterprise-level data projects requiring reliable SQL connectivity.
Its modular design, CLI integration, and OOP architecture enable scalable, maintainable, and portable database access for analytics, pipelines, and research.

> Someparts of this project — the test suite, packaging, CI and several refactors — were developed with AI-assisted development tooling.


# SQL-Connection-Module

### Enterprise-Level Multi-Engine SQL Connector in Python

`SQL-Connection-Module` is a modular, Object-Oriented Python package designed to connect and interact with multiple relational database engines (SQLite, PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, Redshift) through a unified, extensible interface.

It provides a **production-ready foundation** for analytics, data science, and ETL projects requiring portable, secure, and maintainable database access.

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

## 🧱 Project Structure

```bash
SQL-Connection-Module/
├─ src/sql_connection/           # Core library (base + engine connectors)
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
├─ scripts/connect.py            # Multi-engine CLI (connect, query)
├─ examples/connect.ipynb        # Jupyter demo – read-only example
├─ tests/test_smoke.py           # Basic unit and integration tests
├─ pyproject.toml                # Project metadata and dependencies
├─ LICENSE                       # MIT License
└─ .gitignore
``` **<-- CIERRE CORREGIDO**
```

## ⚙️ Installation

### 📦 Clone and install in editable mode

```bash
git clone [https://github.com/aalopez76/SQL-Connection-Module.git](https://github.com/aalopez76/SQL-Connection-Module.git)
cd SQL-Connection-Module
pip install -e
```

### 🔧 Optional dependencies

You can install database drivers or additional tools as extras:

```bash
pip install -e .[pandas]       # For DataFrame support
pip install -e .[postgres]     # For PostgreSQL
pip install -e .[mysql]        # For MySQL / MariaDB
pip install -e .[mssql]        # For SQL Server (requires ODBC driver)
pip install -e .[oracle]       # For Oracle
pip install -e .[snowflake]    # For Snowflake
pip install -e .[dev]          # For development (pytest, linting)
```



## Usage Examples
a) From Python
```bash
from sql_connection import get_connector

conn = get_connector("sqlite", path="examples/toys_and_models.sqlite")

with conn:
    print("Connected:", conn.dsn_summary())
    print("Ping:", conn.ping())
    df = conn.read_sql("SELECT customerName, country FROM customers LIMIT 5;")
    print(df)
```

b) From Command Line (CLI)
SQLite example
```bash
python scripts/connect.py sqlite --path examples/toys_and_models.sqlite --query "SELECT * FROM customers LIMIT 5"
```

```bash
 PostgreSQL example
python scripts/connect.py postgres --host localhost --port 5432 \
  --dbname mydb --user myuser --password --query "SELECT COUNT(*) FROM sales"
```

## Testing

Run tests with pytest:

```bash
pytest -v
```

Sample smoke test includes:
- Package import
- SQLite read-only connection
- Query and ping validation

## Example Notebook

Open examples/connect.ipynb
 to explore:

- Connecting to SQLite

- Listing tables

- Querying and filtering data

- Parameterized SQL examples

The notebook demonstrates how this module integrates easily into analytics workflows, allowing data scientists to query, explore, and visualize data programmatically without switching tools.

## Design Principles

-OOP architecture: promotes reuse and extension across database types.

-Factory pattern: decouples engine selection from implementation.

-Error safety: controlled connection lifecycle and contextual cleanup.

-Scalability: suitable for production ETL, dashboards, or research analysis.

-Read-only by default: safer for analytics environments.

## 🚀 Roadmap

| **Feature** | **Status** |
|--------------|------------|
| SQLite, PostgreSQL connectors | ✅ Stable |
| MySQL, SQL Server, Oracle | ⚙️ In progress |
| Snowflake, Redshift support | 🧩 Planned |
| Connection pooling | 🔜 Planned |
| Async engine support (aioodbc/asyncpg) | 🔜 Future milestone |

##License

This project is licensed under the MIT License — see the LICENSE
 file for details.

## Author

aa lopez
Data Scientist & Engineer
GitHub Profile

## Summary

This repository serves as a template and foundation for enterprise-level data projects requiring reliable SQL connectivity.
Its modular design, CLI integration, and OOP architecture enable scalable, maintainable, and portable database access for analytics, pipelines, and research.


# Plan de refactorización — SQL-Connection-Module

> Derivado de `docs/AUDIT.md`. Tareas ejecutables, ordenadas de mayor a menor impacto y **no
> disruptivas** (se preserva funcionalidad y API públicas). Cada tarea cierra con `pytest -q` en
> verde y un commit Conventional Commits.

**Decisiones acordadas:**
- Lock de dependencias con **pip-tools** (`requirements.lock`); `pyproject` permanece PEP 621.
- Unificación de API con **alias retrocompatibles** (`DeprecationWarning`); **cero breaking changes**.
- Alcance: **🔴 críticos + 🟡 mejorables + arranque de 🟢** (build/versionado para publicación).

---

## Tabla de tareas

| ID | Tarea | Tipo commit | Cierra | Cambio de sistema |
|----|-------|-------------|--------|-------------------|
| T0 | Salvaguarda git (commit/rama backup) | — | salvaguarda | git (confirmar) |
| T1 | Reparar `pyproject.toml` + consolidar config + `py.typed` + `__version__` | `chore(deps)` | C2, C3, M3, M4, M9 | no |
| T2 | Lock reproducible con pip-tools | `build` | C1 | sí (instalar pip-tools) |
| T3 | Alinear README + `.env.example` + política de datos | `docs` | C3, M7, M8 | no |
| T4 | Ampliar tests del núcleo (base, masking, CLI) | `test` | C5 | no |
| T5 | Alias de API retrocompatibles | `feat(api)` | M1 | no |
| T6 | CLI instalable (mover lógica a `cli.py`) | `refactor(cli)` | M5 | mueve archivos (confirmar) |
| T7 | Logging con `logging` | `feat` | M2 | no |
| T8 | Makefile + CI (GitHub Actions) | `ci` | C4, M6 | no |
| T9 | Aplicar `ruff`/`mypy` | `chore` | M3 | no |
| T10 | Documentación final (`CLAUDE.md`, README) | `docs` | requisito flujo | no |
| T11 | Arranque de publicación (`python -m build`) | `build` | 🟢 | no |

---

## Detalle

### T0 — Salvaguarda git
Confirmar estado limpio en git (commit de los 14 archivos modificados) o crear rama
`backup/pre-refactor`. Nunca se borra código sin confirmación explícita.

### T1 — `pyproject.toml` + config
- `[project.optional-dependencies]`: `pandas`, `postgres`, `mysql`, `mssql`, `oracle`, `snowflake`,
  `redshift`, `all`, `dev` (pytest, pytest-cov, ruff, mypy, pip-tools, build).
- Mover `pandas` de core a extra `[pandas]` (ya es opcional en el código), pin `>=1.5`.
- `[project.scripts] sql-connect = "sql_connection.cli:main"` (habilita en T6).
- `__version__` vía `importlib.metadata`; `py.typed` en package-data.
- Migrar `pytest.ini` → `[tool.pytest.ini_options]`; añadir `[tool.ruff]`, `[tool.mypy]`, `[tool.coverage]`.

### T2 — Lock con pip-tools
`pip-compile` desde `pyproject` (extras `dev,all`) → `requirements.lock` con versiones fijadas.

### T3 — README + credenciales
Corregir todos los comandos de instalación; `.env.example` por motor; documentar que
`examples/toys_and_models.sqlite` se mantiene en git como fixture (sin DVC).

### T4 — Tests del núcleo
- `tests/test_base_methods.py`: SQLite `:memory:` → `execute`/`query`/`read_sql`/`read_sql_chunks`,
  `_ensure_connected()` lanza `RuntimeError`.
- `tests/test_masking.py`: `mask_secret` + `dsn_summary()` de cada conector no filtra contraseña.
- `tests/test_cli.py`: `_run("sqlite", ...)` con `--query` y código de retorno.
- Ampliar `tests/test_factory.py` con alias.

### T5 — Alias de API
Canónico `database`; aceptar `db`/`dbname` con `DeprecationWarning` en el factory. Firmas de
conectores intactas.

### T6 — CLI instalable
Mover lógica a `src/sql_connection/cli.py`; `scripts/connect.py` → wrapper delgado. Verificar paridad.

### T7 — Logging
`logging.getLogger(__name__)` en `connect()`/`close()`; CLI con `basicConfig` y `--verbose`.

### T8 — Makefile + CI
Targets: `install`, `lock`, `test`, `lint`, `format`, `typecheck`, `build`, `run`, `clean`.
CI matrix Python 3.10–3.12: `ruff` + `mypy` + `pytest --cov`.

### T9 — ruff/mypy
`ruff --fix` y `mypy src`; corregir sin cambiar comportamiento.

### T10 — Documentación final
`CLAUDE.md` (stack, comandos, convenciones) + README de instalación/pipeline/tests.

### T11 — Publicación
`python -m build` (sdist+wheel) + checklist de release (sin publicar aún).

---

## Verificación end-to-end
1. `pip install -e ".[dev,pandas]"` sin error.
2. `pytest -q` verde + cobertura del núcleo (`pytest --cov`).
3. CLI vía script y vía `sql-connect` con salida idéntica.
4. `ruff check .` y `mypy src` limpios.
5. `python -c "import sql_connection; print(sql_connection.__version__)"`.
6. `python -m build` genera wheel+sdist.
7. CI en verde.

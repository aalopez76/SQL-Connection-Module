# Auditoría técnica — SQL-Connection-Module

> Fecha: 2026-06-03 · Autor: revisión Senior DS · Versión auditada: `0.1.0` (rama `main`)
> Objetivo declarado: **preparar la librería para producción/publicación** (uso como dependencia
> reutilizable, pieza de pipelines ETL/ML y escaparate de buenas prácticas).

---

## 1. Resumen ejecutivo

`SQL-Connection-Module` es una **librería Python de acceso multi-motor a bases SQL** con una
arquitectura OOP sólida: clase base abstracta (`DatabaseConnector`), patrón *factory*
(`get_connector`), siete conectores concretos y una CLI con `argparse`. El diseño conceptual es
**bueno y maduro**; el problema no es el *qué* sino el *cómo se entrega*: el proyecto **no es
reproducible ni publicable hoy**.

Los bloqueantes principales para el objetivo de producción/publicación son:

1. **Entorno no reproducible**: sin lock file y con un desajuste real (`pyproject` exige
   `pandas>=2.0.0`, el entorno corre `pandas 1.5.3`).
2. **`pyproject.toml` incompleto**: no declara los *extras* (`[postgres]`, `[dev]`…) que el README
   promete, ni `py.typed`, ni *entry point* de consola. **Instalar siguiendo el README falla.**
3. **Sin red de seguridad de CI**: no hay GitHub Actions, ni linting/formato/type-check
   automatizados, ni `Makefile`.
4. **Cobertura de tests parcial**: no se prueban los métodos centrales (`read_sql`, `query`,
   `execute`), el enmascarado de secretos ni la CLI; los conectores no-SQLite solo se prueban con
   "conexión rechazada".

El esfuerzo para cerrar los críticos es **bajo-medio** y de **bajo riesgo** (la lógica de negocio
no necesita reescribirse). Es un caso claro de "buen núcleo, empaquetado y tooling pendientes".

**Veredicto:** núcleo recomendable; **no apto para publicar** hasta resolver los 🔴.

---

## 2. Lo que está bien (aspectos rescatables)

- ✅ **Layout `src/`** correcto, con separación `core/` (abstracción) vs `engines/` (implementación).
- ✅ **Abstracción limpia**: `DatabaseConnector` (ABC) define un contrato claro; lifecycle por
  context manager (`__enter__/__exit__`) y `_ensure_connected()` defensivo.
- ✅ **Patrón factory** con `Literal` para los motores y validación de argumentos requeridos
  (`_need`) con mensajes de error útiles.
- ✅ **Drivers opcionales** con import defensivo (`try/except` → `None`) y error explícito en
  `connect()`; permite instalar solo lo necesario.
- ✅ **Enmascarado de secretos** (`mask_secret`) usado en todos los `dsn_summary()`.
- ✅ **CLI cuidada**: subparsers por motor, contraseña por `getpass` (no en argv), códigos de salida
  correctos, fallback de `read_sql`→`query` si no hay pandas.
- ✅ **Tests parametrizados por disponibilidad de driver** (`skipif`) y *fixture* de DB de ejemplo
  con `skip` limpio si falta.
- ✅ **`pytest.ini`** con `pythonpath = src` y `testpaths` correctos. Suite en verde (8 passed, 4 skipped).

---

## 3. Problemas detectados

### 🔴 Críticos (bloquean reproducibilidad / publicación)

| # | Problema | Evidencia | Impacto |
|---|----------|-----------|---------|
| C1 | **Entorno no reproducible.** No hay lock file (poetry.lock / requirements.txt fijado / uv.lock). | Sólo `pyproject.toml` con rangos abiertos. | Builds distintos por máquina; imposible reproducir resultados. |
| C2 | **Desajuste de dependencias real.** `pyproject` pide `pandas>=2.0.0`; el entorno tiene `pandas 1.5.3`. | `python -c "import pandas"` → 1.5.3. | El contrato declarado ya está roto; señal de que nadie valida el entorno. |
| C3 | **`optional-dependencies` ausente.** El README documenta `pip install -e .[postgres]`, `.[dev]`, `.[pandas]`, etc., pero `pyproject` no define `[project.optional-dependencies]`. | `pyproject.toml` vs `README.md` líneas 71-83. | **Las instrucciones de instalación fallan.** Bloquea onboarding y publicación. |
| C4 | **Sin CI.** No existe `.github/workflows/`. | Árbol de archivos. | Nada garantiza que los tests/estilo pasen antes de mergear o publicar. |
| C5 | **Tests sin cobertura del núcleo.** No se prueban `read_sql`, `query`, `execute`, `read_sql_chunks` ni `dsn_summary()`/enmascarado. Sólo SQLite real + "connection refused". | `tests/` (4 archivos). | Un refactor podría romper el comportamiento sin que ningún test lo detecte. |

### 🟡 Mejorables (calidad, mantenibilidad, DX)

| # | Problema | Evidencia | Impacto |
|---|----------|-----------|---------|
| M1 | **API inconsistente entre motores.** El nombre del parámetro de base varía: `db` (MySQL), `dbname` (Postgres/Redshift), `database` (SQL Server), `path` (SQLite). | factory / engines. | Fricción y errores para quien usa varios motores. |
| M2 | **Sin logging.** Se usa `print` (incl. en CLI) en vez del módulo `logging`. | `scripts/connect.py`, conectores. | Sin observabilidad como componente de pipeline; ruido en stdout. |
| M3 | **Sin linting/formato/type-check.** `.gitignore` menciona ruff/mypy pero no hay config ni ejecución. | No hay `[tool.ruff]`/`[tool.mypy]`. | Estilo no garantizado; type hints sin validar pese a usarse en todo el código. |
| M4 | **No empaquetable como librería tipada.** Falta marcador `py.typed` y no se expone `__version__`. | `src/sql_connection/`. | Consumidores no obtienen tipos; sin versión introspectable. |
| M5 | **CLI no instalable como comando.** No hay `[project.scripts]`; se invoca con `python scripts/connect.py`. | `pyproject.toml`. | Inconsistente con una librería "publicable". |
| M6 | **Sin `Makefile` ni tareas estandarizadas.** | Árbol. | Cada quien ejecuta comandos a mano; difícil de automatizar. |
| M7 | **Falta `.env.example` / gestión de credenciales documentada.** | Árbol. | Secretos sin convención; riesgo de fugas. |
| M8 | **DB binaria versionada en git** (`examples/toys_and_models.sqlite`). | `git ls-files`. | Aceptable como *fixture* pequeño, pero conviene decidir política (git, git-lfs o DVC) de cara a producción. |
| M9 | **`pytest.ini` separado** del `pyproject`; config dispersa. | Raíz. | Menor; consolidar mejora mantenibilidad. |
| M10 | **`read_sql`/`read_sql_chunks` con `params or {}`** y pandas+driver DB-API directo. | `base_connector.py`. | Pandas recomienda SQLAlchemy; con `{}` algunos drivers emiten warnings. Funcional pero frágil. |

### 🟢 Recomendaciones a futuro (cuando lo anterior esté cerrado)

- 🟢 **Publicación en PyPI / repo interno** con *build* (`python -m build`) y versionado semántico
  (etiquetas + `release` automatizado).
- 🟢 **`SQLAlchemy` opcional** como backend de `read_sql` para eliminar warnings y ampliar soporte.
- 🟢 **Reintentos/backoff** y *connection pooling* configurable para uso intensivo en pipelines.
- 🟢 **Cobertura ≥ 85%** publicada (badge) y *matrix* de CI por versión de Python (3.10–3.13) y SO.
- 🟢 **Documentación con MkDocs** (`docs/`) y *pre-commit hooks*.
- 🟢 **Allow-list de sentencias** o flag explícito para escritura (hoy `execute` permite DML/DDL pese
  al lema "read-only by default").

---

## 4. Recomendaciones concretas y ordenadas

Ordenadas por impacto/esfuerzo para el objetivo de **producción/publicación**:

1. **Reparar `pyproject.toml`** (C2, C3, M4, M5): añadir `optional-dependencies` (`pandas`, cada
   driver, `dev`), `[project.scripts]`, marcador `py.typed`, y consolidar `pytest`/`ruff`/`mypy`.
2. **Fijar el entorno** (C1): generar lock reproducible (`requirements.lock`/`uv.lock`/`poetry.lock`)
   y documentar el flujo de instalación verificado.
3. **Alinear el README con la realidad** (C3): que cada comando de instalación funcione tal cual.
4. **Ampliar tests del núcleo** (C5): SQLite en memoria para cubrir `read_sql`/`query`/`execute`/
   `chunks`; tests unitarios de `mask_secret` y de cada `dsn_summary()` (verificar que no filtra
   secretos); test de la CLI.
5. **Añadir CI** (C4): workflow de GitHub que instale extras `dev`, ejecute `ruff`, `mypy` y
   `pytest` con cobertura, en *matrix* de Python.
6. **`Makefile`** (M6) con targets homogéneos (`install`, `test`, `lint`, `format`, `typecheck`,
   `build`, `run`).
7. **Logging** (M2): sustituir `print` internos por `logging`; la CLI configura el handler.
8. **`.env.example` + convención de credenciales** (M7).
9. **Decidir política de datos de ejemplo** (M8) y unificar nomenclatura de API si se asume el coste
   (M1, *breaking* — requiere tu visto bueno).
10. **A futuro** (🟢): build/publicación, SQLAlchemy opcional, pooling/retries, docs y cobertura.

---

## 5. Estado de la suite actual (medición)

```
pytest -q  →  8 passed, 4 skipped  (drivers pymysql/pyodbc/oracledb/snowflake no instalados)
Python 3.11.9 · pandas 1.5.3 (¡< 2.0.0 declarado!) · psycopg2 presente
```

> Próximo paso: tras validar prioridades, se redactará `docs/REFACTOR_PLAN.md` con tareas
> ejecutables, ordenadas y **no disruptivas** (se preservará la funcionalidad y la API públicas
> salvo que apruebes explícitamente los cambios *breaking* de M1).

# Release checklist

This library is **build-ready** but not yet published. Follow these steps to cut a release.

## Versioning

Semantic Versioning (`MAJOR.MINOR.PATCH`):

- **PATCH** — bug fixes, no API change.
- **MINOR** — backward-compatible features (e.g. the unified `database=` alias was a minor bump
  candidate; deprecations land here).
- **MAJOR** — breaking changes (e.g. removing the deprecated `db`/`dbname` aliases).

The version lives in `pyproject.toml` (`[project].version`) and is exposed at runtime via
`sql_connection.__version__`.

## Pre-release gate (must be green)

```bash
ruff check .
mypy src
pytest --cov=sql_connection
```

## Build & validate artifacts

```bash
make build                      # or: python -m build
pip install twine               # if not present
twine check dist/*              # validate metadata / README rendering
```

A clean smoke test in a throwaway environment:

```bash
python -m venv /tmp/relcheck && /tmp/relcheck/bin/pip install dist/*.whl
/tmp/relcheck/bin/python -c "import sql_connection; print(sql_connection.__version__)"
/tmp/relcheck/bin/sql-connect --help
```

## Publish

```bash
# Test index first
twine upload --repository testpypi dist/*
# Then production PyPI (or your internal index)
twine upload dist/*
```

## Tag the release

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

> Consider automating build + publish on tag push via a GitHub Actions release workflow
> (trusted publishing / OIDC to PyPI) once the first manual release is validated.

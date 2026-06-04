# Makefile for SQL-Connection-Module
# Override the interpreter with: make PY=.venv/Scripts/python.exe <target>
PY ?= python

.DEFAULT_GOAL := help

.PHONY: help install install-all lock test cov lint format typecheck build run clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Editable install with dev + pandas extras
	$(PY) -m pip install -e ".[dev,pandas]"

install-all:  ## Editable install with every driver + dev
	$(PY) -m pip install -e ".[dev,all]"

lock:  ## Recompile requirements.lock from pyproject
	$(PY) -m piptools compile --extra dev --extra all --output-file requirements.lock pyproject.toml

test:  ## Run the test suite
	$(PY) -m pytest

cov:  ## Run tests with coverage report
	$(PY) -m pytest --cov=sql_connection --cov-report=term-missing

lint:  ## Lint with ruff
	$(PY) -m ruff check .

format:  ## Auto-format / fix with ruff
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

typecheck:  ## Static type check with mypy
	$(PY) -m mypy src

build:  ## Build sdist + wheel
	$(PY) -m build

run:  ## Run the CLI against the example SQLite DB (lists tables)
	$(PY) scripts/connect.py sqlite --path examples/toys_and_models.sqlite \
		--query "SELECT name FROM sqlite_master WHERE type='table'"

clean:  ## Remove build/test artifacts
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov

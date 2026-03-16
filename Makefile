install:
	poetry install

format:
	poetry run ruff format .

lint:
	poetry run ruff check . --fix

type:
	poetry run mypy src

check:
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type

test:
	poetry run pytest

build:
	poetry build

run:
	poetry run girbridge --help

help:
	@echo "Commands:"
	@echo " make install  - install dependencies"
	@echo " make format   - format code"
	@echo " make lint     - run linter"
	@echo " make type     - run mypy"
	@echo " make check    - run all checks (lint, format, type)"
	@echo " make test     - run tests"
	@echo " make build    - build package"
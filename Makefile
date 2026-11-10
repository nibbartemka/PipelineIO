.DEFAULT_GOAL := help
.PHONY: help lint format

help:
	@echo "make lint    - проверить код"
	@echo "make format  - отформатировать код"
	@echo "make check   - проверка без изменений (CI)"
	@echo "make fix     - автофиксы + форматирование"
	@echo "make clean   - удалить кэши и results.log"

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .

fix:
	uv run ruff check --fix .
	uv run ruff format .

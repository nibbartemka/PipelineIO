.DEFAULT_GOAL := help
.PHONY: help install lint format check fix clean

help:
	@echo "make install - установить зависимости проекта через uv"
	@echo "make lint    - проверить код"
	@echo "make format  - отформатировать код"
	@echo "make check   - проверка без изменений (CI)"
	@echo "make fix     - автофиксы + форматирование"
	@echo "make clean   - удалить кэши и results.log"

install:
	uv sync

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

clean:
	rm -rf __pycache__ .ruff_cache results.log

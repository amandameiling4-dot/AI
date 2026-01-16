# Makefile for common developer tasks
.PHONY: setup test run-pipeline format lint

setup:
	python -m pip install --upgrade pip
	@if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
	pip install pytest

test:
	pytest -q

run-pipeline:
	python scripts/data/ingest_sample.py
	python scripts/data/run_pipeline.py

format:
	# Add formatting commands here (black/isort)
	@echo "No formatter configured"

lint:
	@echo "No linter configured"
.PHONY: help install run test clean format lint

help:
	@echo "PointCrypt - Makefile Commands"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  install         Install dependencies (pip install pycryptodome streamlit plotly pytest)"
	@echo "  run             Run Streamlit interactive dashboard"
	@echo "  test            Run all tests (pytest)"
	@echo "  test-verbose    Run tests with detailed output"
	@echo "  test-core       Run core module tests"
	@echo "  test-sender     Run sender module tests"
	@echo "  test-receiver   Run receiver module tests"
	@echo "  clean           Remove __pycache__ and .pytest_cache"
	@echo "  format          Format code (basic Python formatting)"
	@echo "  lint            Check code style (if pylint installed)"
	@echo "  demo            Run quick encryption/decryption demo"
	@echo "  help            Show this help message"
	@echo ""

install:
	pip install pycryptodome streamlit plotly pytest
	@echo "✅ Dependencies installed!"

run:
	streamlit run app/streamlit_app.py

test:
	pytest tests/ -v

test-verbose:
	pytest tests/ -v --tb=short

test-core:
	python -m pytest tests/test_formulas.py tests/test_blocks.py -v

test-sender:
	python -m sender.encryptor

test-receiver:
	python -m receiver.decryptor

test-integration:
	python -m pytest tests/test_integration.py -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"

format:
	@echo "Formatting Python files..."
	autopep8 --in-place --aggressive --aggressive core/*.py 2>/dev/null || echo "autopep8 not installed, skipping"
	autopep8 --in-place --aggressive --aggressive sender/*.py 2>/dev/null || true
	autopep8 --in-place --aggressive --aggressive receiver/*.py 2>/dev/null || true
	autopep8 --in-place --aggressive --aggressive app/*.py 2>/dev/null || true
	@echo "✅ Formatted!"

lint:
	@echo "Linting Python files..."
	pylint core/*.py 2>/dev/null || echo "pylint not installed, skipping"
	@echo "✅ Linting complete!"

demo:
	@echo "Running encryption/decryption demo..."
	python -m receiver.decryptor
	@echo ""
	@echo "All demos completed! 🎉"

.DEFAULT_GOAL := help

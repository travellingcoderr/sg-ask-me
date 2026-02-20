.PHONY: help install dev run check test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies (pip install -e .)"
	@echo "  make dev        - Run development server (uvicorn with reload)"
	@echo "  make run        - Run production server (uvicorn without reload)"
	@echo "  make check      - Check code syntax and imports"
	@echo "  make test       - Run tests (if available)"
	@echo "  make clean      - Clean build artifacts"

# Detect venv location (prefer repo root, fallback to backend)
VENV_PYTHON := $(shell if [ -f "../.venv/bin/python" ]; then echo "../.venv/bin/python"; elif [ -f ".venv/bin/python" ]; then echo ".venv/bin/python"; else echo "python3"; fi)

install:
	@echo "Installing dependencies..."
	$(VENV_PYTHON) -m pip install -e .

dev:
	@echo "Starting development server..."
	$(VENV_PYTHON) -m uvicorn app.main:app --reload --port 8000

run:
	@echo "Starting production server..."
	$(VENV_PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

check:
	@echo "Checking code..."
	$(VENV_PYTHON) check.py

test:
	@echo "Running tests..."
	@echo "No tests configured yet"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

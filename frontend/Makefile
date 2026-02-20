.PHONY: help install dev build start lint clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies (npm install)"
	@echo "  make dev      - Run development server (npm run dev)"
	@echo "  make build    - Build for production (npm run build)"
	@echo "  make start    - Start production server (npm start)"
	@echo "  make lint     - Run linter (npm run lint)"
	@echo "  make clean    - Clean build artifacts and node_modules"

install:
	@echo "Installing dependencies..."
	npm install

dev:
	@echo "Starting development server..."
	npm run dev

build:
	@echo "Building for production..."
	npm run build

start:
	@echo "Starting production server..."
	npm start

lint:
	@echo "Running linter..."
	npm run lint

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .next
	rm -rf out
	rm -rf node_modules
	rm -rf .turbo
	find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true

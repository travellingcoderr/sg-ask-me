#!/bin/bash
# Development server shortcut
# Usage: ./dev.sh

# Detect venv location
if [ -f "../.venv/bin/python" ]; then
    PYTHON="../.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

echo "Starting development server..."
$PYTHON -m uvicorn app.main:app --reload --port 8000

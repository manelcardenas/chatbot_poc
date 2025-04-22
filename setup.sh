#!/bin/bash

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if command -v uv &> /dev/null; then
    uv lock
    uv add -e .
    uv sync
else
    pip install -e .
fi

echo "Setup complete. Activate the virtual environment with 'source .venv/bin/activate'" 
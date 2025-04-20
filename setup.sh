#!/bin/bash

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if command -v uv &> /dev/null; then
    uv pip install -e .
else
    pip install -e ".[dev]"
fi

echo "Setup complete. Activate the virtual environment with 'source .venv/bin/activate'" 
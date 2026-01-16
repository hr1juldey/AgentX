#!/bin/bash
# Run tests

cd "$(dirname "$0")/.."
python -m pytest tests/ -v

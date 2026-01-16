#!/bin/bash
# Run the FastAPI server

cd "$(dirname "$0")/.."
python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload

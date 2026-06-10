#!/bin/sh
set -e

uvicorn fastapi_slap2.main:app --host 0.0.0.0 --port ${PORT:-8000}

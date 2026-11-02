#!/bin/sh
set -e

uvicorn fastapi_slap2.main:app --host "" --port ${PORT:-8000}

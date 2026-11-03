#!/bin/sh
set -e

# --host "" is intentional: it binds all interfaces (IPv4 and IPv6), which Railway (how this project is deployed as a demonstration service) internal networking needs.
# feel free to change it in your own project
exec uvicorn fastapi_slap2.main:app --host "" --port "${PORT:-8000}"

"""Middleware for the SLAP2 API."""

from urllib.parse import urlencode

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp


class UppercaseQueryParamsMiddleware(BaseHTTPMiddleware):
    """Convert all query parameter names to uppercase.

    The DALI spec requires that query parameter names are case-insensitive;
    this middleware normalises them to uppercase for consistent handling.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        original_query = request.query_params.multi_items()
        upper_query = [(key.upper(), value) for key, value in original_query]
        new_query_string = urlencode(upper_query, doseq=True)
        request.scope["query_string"] = new_query_string.encode("utf-8")
        return await call_next(request)

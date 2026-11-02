"""Exception handlers for the SLAP2 API.

Errors are reported as DALI error documents: a VOTable whose results RESOURCE
carries ``<INFO name="QUERY_STATUS" value="ERROR">message</INFO>``.
"""

from xml.sax.saxutils import escape

from fastapi.responses import Response

from fastapi_slap2.responses import XMLResponse

VOTABLE_ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<VOTABLE version="1.4" xmlns="http://www.ivoa.net/xml/VOTable/v1.3">
  <RESOURCE type="results">
    <INFO name="QUERY_STATUS" value="ERROR">{error}</INFO>
  </RESOURCE>
</VOTABLE>
"""


class ParameterError(ValueError):
    """A query parameter is missing, unknown, repeated, or has an invalid value."""


def votable_error_response(message: str, status_code: int) -> Response:
    """Return a VOTable-formatted error response."""
    return XMLResponse(content=VOTABLE_ERROR_XML.format(error=escape(message)), status_code=status_code)


async def parameter_error_handler(request, exc: ParameterError) -> Response:
    return votable_error_response(str(exc), 400)


async def general_exception_handler(request, exc) -> Response:
    return votable_error_response("An unexpected error occurred. Please try again later.", 500)


async def http_exception_handler(request, exc) -> Response:
    error_str = str(exc.detail).replace("\n", " ").strip()
    return votable_error_response(error_str, exc.status_code)


async def validation_exception_handler(request, exc) -> Response:
    errors = exc.errors()
    error_str = "; ".join(f"Invalid value for {e['loc'][-1]}: {e['msg']}" for e in errors)
    return votable_error_response(error_str, 400)

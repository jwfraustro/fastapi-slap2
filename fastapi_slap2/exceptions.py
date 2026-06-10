"""Exception handlers for the SLAP2 API."""

from fastapi.responses import Response

from fastapi_slap2.responses import XMLResponse

VOTABLE_ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<VOTABLE version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.ivoa.net/xml/VOTable/v1.1"
  xsi:schemaLocation="http://www.ivoa.net/xml/VOTable/v1.1 http://www.ivoa.net/xml/VOTable/v1.1">
  <DESCRIPTION>SLAP2</DESCRIPTION>
  <INFO ID="Error" name="Error" value="{error}"/>
</VOTABLE>"""


def votable_error_response(message: str, status_code: int) -> Response:
    """Return a VOTable-formatted error response."""
    return XMLResponse(
        content=VOTABLE_ERROR_XML.format(error=message),
        status_code=status_code,
        media_type="text/xml",
    )


async def general_exception_handler(request, exc) -> XMLResponse:
    error_str = "An unexpected error occurred. Please try again later."
    if hasattr(exc, "exceptions") and exc.exceptions:
        error_str = [str(e) for e in exc.exceptions if str(e)]  # type: ignore
    return votable_error_response(error_str, 500)


async def http_exception_handler(request, exc):
    error_str = exc.detail.replace("\n", " ").strip()
    return votable_error_response(error_str, exc.status_code)


async def validation_exception_handler(request, exc) -> XMLResponse:
    errors = exc.errors()
    error_str = ", ".join([f"Error in {e['loc'][0]} {e['loc'][1]}: {e['msg']}" for e in errors])
    return votable_error_response(error_str, 400)

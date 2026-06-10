"""Response classes for the SLAP2 API."""

from fastapi.responses import Response


class XMLResponse(Response):
    """VOTable XML response."""

    media_type = "application/x-votable+xml"

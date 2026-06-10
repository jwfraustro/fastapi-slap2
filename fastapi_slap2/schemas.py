"""Schemas for the SLAP2 API."""

from enum import StrEnum


class ResponseFormat(StrEnum):
    """Supported response formats."""

    VOTABLE = "votable"

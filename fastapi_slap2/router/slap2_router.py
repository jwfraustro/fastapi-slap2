"""API endpoints for the SLAP2 service."""

from typing import Annotated, Optional

from fastapi import APIRouter, Query
from fastapi_restful.cbv import cbv

from fastapi_slap2 import schemas
from fastapi_slap2.exceptions import votable_error_response
from fastapi_slap2.services import handle_response_format, perform_query

slap2_router = APIRouter()


@cbv(slap2_router)
class SLAP2Router:
    """Router for SLAP2 API endpoints."""

    @slap2_router.get("/query", summary="Perform a SLAP2 query.")
    def query(
        self,
        maxrec: Annotated[
            Optional[int],
            Query(
                description="Maximum number of records to return.",
                example=100,
                ge=0,
                alias="MAXREC",
            ),
        ] = 1000,
        responseformat: Annotated[
            Optional[schemas.ResponseFormat],
            Query(
                description="Format of the response.",
                example="votable",
                alias="RESPONSEFORMAT",
            ),
        ] = "votable",
    ):
        """Perform a SLAP2 query."""
        if maxrec == 0:
            return handle_response_format([], [], responseformat, True)

        return perform_query(maxrec=maxrec, response_format=responseformat)

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

    @slap2_router.get("/lines", summary="Perform a SLAP2 lines query.")
    def lines_query(
        self,
        wavelength: Annotated[
            Optional[list[str]],
            Query(
                description="Wavelength range to query, in meters. Format: 'min max'.",
                example="5.1E-6 5.6E-6",
                alias="WAVELENGTH",
            ),
        ] = None,
        species: Annotated[
            Optional[list[str]],
            Query(
                description="Species to query for, e.g., 'H2O'.",
                example="H2O",
                alias="SPECIES",
            ),
        ] = None,
        species_mass: Annotated[
            Optional[list[str]],
            Query(
                description="Mass range of the species to query for, in atomic mass units (u). Format: 'min max'.",
                example="0 12.011",
                alias="SPECIES_MASS",
            ),
        ] = None,
        inchikey: Annotated[
            Optional[list[str]],
            Query(
                description="InChIKey of the species to query for.",
                example="XLYOFNOQVPJJNP-UHFFFAOYSA-N",
                alias="INCHIKEY",
            ),
        ] = None,
        ion_charge: Annotated[
            Optional[list[str]],
            Query(
                description="Charge state of the ion to query for, e.g., '0' for neutral, '1' for singly ionized.",
                example="1 +Inf",
                alias="ION_CHARGE",
            ),
        ] = None,
        lower_level_energy: Annotated[
            Optional[list[str]],
            Query(
                description="Energy range of the lower level to query for, in Joules. Format: 'min max'.",
                example="3.93E-18 3.94E-18",
                alias="LOWER_LEVEL_ENERGY",
            ),
        ] = None,
        upper_level_energy: Annotated[
            Optional[list[str]],
            Query(
                description="Energy range of the upper level to query for, in Joules. Format: 'min max'.",
                example="3.95E-18 3.96E-18",
                alias="UPPER_LEVEL_ENERGY",
            ),
        ] = None,
        einsteina: Annotated[
            Optional[list[str]],
            Query(
                description="Einstein A coefficient range to query for, in s^-1. Format: 'min max'.",
                example="1E-5 1E-3",
                alias="EINSTEINA",
            ),
        ] = None,
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

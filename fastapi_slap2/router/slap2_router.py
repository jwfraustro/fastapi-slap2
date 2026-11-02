"""API endpoints for the SLAP2 service."""

from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi_restful.cbv import cbv

from fastapi_slap2 import schemas
from fastapi_slap2.config.settings import get_settings
from fastapi_slap2.exceptions import ParameterError
from fastapi_slap2.services import perform_lines_query

slap2_router = APIRouter()


def check_parameter_names(request: Request, allowed: dict[str, bool]) -> None:
    """Reject unknown parameters and repeats of single-valued ones."""
    seen: set[str] = set()
    for name, _ in request.query_params.multi_items():
        if name not in allowed:
            raise ParameterError(f"Parameter {name} is not supported by this service")
        if name in seen and not allowed[name]:
            raise ParameterError(f"Parameter {name} is single-valued and must not be repeated")
        seen.add(name)


def response_media_type(responseformat: schemas.ResponseFormat | None) -> str:
    if responseformat == schemas.ResponseFormat.TEXT_XML:
        return "text/xml"
    return "application/x-votable+xml"


@cbv(slap2_router)
class SLAP2Router:
    """Router for SLAP2 API endpoints."""

    @slap2_router.get(
        "/lines",
        summary="Perform a SLAP2 lines query.",
        responses={200: {"content": {"application/x-votable+xml": {}}}},
    )
    def lines_query(
        self,
        request: Request,
        wavelength: Annotated[
            str | None,
            Query(
                description="Vacuum wavelength interval in metres (mandatory). Format: 'min max' or a single value.",
                example="5.1E-6 5.6E-6",
                alias="WAVELENGTH",
            ),
        ] = None,
        species: Annotated[
            list[str] | None,
            Query(
                description="Species name, exact match against species_name. May be repeated (OR).",
                example="Fe",
                alias="SPECIES",
            ),
        ] = None,
        species_mass: Annotated[
            str | None,
            Query(
                description="Species mass interval in unified atomic mass units (u).",
                example="0 12.011",
                alias="SPECIES_MASS",
            ),
        ] = None,
        inchikey: Annotated[
            list[str] | None,
            Query(
                description="InChIKey of the species, exact match. May be repeated (OR).",
                example="XEEYBQQBJWHFJM-UHFFFAOYSA-N",
                alias="INCHIKEY",
            ),
        ] = None,
        ion_charge: Annotated[
            str | None,
            Query(
                description="Ion charge interval (integers). 0 for neutral species.",
                example="1 +Inf",
                alias="ION_CHARGE",
            ),
        ] = None,
        lower_level_energy: Annotated[
            str | None,
            Query(
                description="Lower level energy interval in Joules.",
                example="3.93E-18 3.94E-18",
                alias="LOWER_LEVEL_ENERGY",
            ),
        ] = None,
        upper_level_energy: Annotated[
            str | None,
            Query(
                description="Upper level energy interval in Joules.",
                example="3.93E-18 3.94E-18",
                alias="UPPER_LEVEL_ENERGY",
            ),
        ] = None,
        einsteina: Annotated[
            str | None,
            Query(
                description="Einstein A coefficient interval in s^-1.",
                example="1.1E-7 1.2E-7",
                alias="EINSTEINA",
            ),
        ] = None,
        maxrec: Annotated[
            int | None,
            Query(
                description="Maximum number of records to return. MAXREC=0 returns metadata only.",
                example=100,
                ge=0,
                alias="MAXREC",
            ),
        ] = None,
        responseformat: Annotated[
            schemas.ResponseFormat | None,
            Query(
                description="Response format. Defaults to application/x-votable+xml.",
                alias="RESPONSEFORMAT",
            ),
        ] = None,
    ):
        """Perform a SLAP2 {lines} query."""
        check_parameter_names(request, schemas.LINES_PARAMETERS)

        if maxrec is None:
            maxrec = get_settings().DEFAULT_MAXREC

        query = schemas.LinesQuery.from_params(
            wavelength=wavelength,
            species=species,
            inchikey=inchikey,
            species_mass=species_mass,
            ion_charge=ion_charge,
            lower_level_energy=lower_level_energy,
            upper_level_energy=upper_level_energy,
            einsteina=einsteina,
        )

        # WAVELENGTH is mandatory, except for a MAXREC=0 metadata request, which
        # validators commonly send without any constraints.
        if query.wavelength is None and maxrec != 0:
            raise ParameterError("Parameter WAVELENGTH is mandatory")

        return perform_lines_query(
            query=query,
            maxrec=maxrec,
            media_type=response_media_type(responseformat),
            request_url=str(request.url),
        )

"""API endpoints for the SLAP2 service."""

from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi_restful.cbv import cbv

from fastapi_slap2 import schemas
from fastapi_slap2.config.settings import get_settings
from fastapi_slap2.exceptions import ParameterError
from fastapi_slap2.services import perform_lines_query, perform_species_query

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

        if wavelength is None:
            raise ParameterError("Parameter WAVELENGTH is required")

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

        return perform_lines_query(
            query=query,
            maxrec=maxrec,
            media_type="text/xml",
            request_url=str(request.url),
        )

    @slap2_router.get(
        "/species",
        summary="Perform a SLAP2 species query.",
        responses={200: {"content": {"application/x-votable+xml": {}}}},
    )
    def species_query(
        self,
        request: Request,
        species_type: Annotated[
            schemas.SpeciesType | None,
            Query(
                description="Type of species to return: 'atom' or 'molecule'. Both are returned if omitted.",
                alias="SPECIES_TYPE",
            ),
        ] = None,
        inchikey: Annotated[
            list[str] | None,
            Query(
                description="InChIKey of the species, exact match. May be repeated (OR).",
                example="UFHFLCQGNIYNRP-UHFFFAOYSA-N",
                alias="INCHIKEY",
            ),
        ] = None,
        inchi: Annotated[
            list[str] | None,
            Query(
                description=(
                    "InChI of the species; supports * and ? wildcards. The 'InChI=' prefix is optional. "
                    "May be repeated (OR)."
                ),
                example="1S/CO/c1-2*",
                alias="INCHI",
            ),
        ] = None,
        species: Annotated[
            list[str] | None,
            Query(
                description="Species name; supports * and ? wildcards. May be repeated (OR).",
                example="CO*",
                alias="SPECIES",
            ),
        ] = None,
        stoichiometric_formula: Annotated[
            list[str] | None,
            Query(
                description="Stoichiometric formula; supports * and ? wildcards. May be repeated (OR).",
                example="CH4O",
                alias="STOICHIOMETRIC_FORMULA",
            ),
        ] = None,
        number_of_atoms: Annotated[
            str | None,
            Query(
                description="Number of atoms in the species (integers). Format: 'min max' or a single value.",
                example="2 5",
                alias="NUMBER_OF_ATOMS",
            ),
        ] = None,
        maxrec: Annotated[
            int | None,
            Query(
                description="Maximum number of records to return. MAXREC=0 returns metadata only.",
                example=10,
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
        """Perform a SLAP2 {species} query."""
        check_parameter_names(request, schemas.SPECIES_PARAMETERS)

        if maxrec is None:
            maxrec = get_settings().DEFAULT_MAXREC

        query = schemas.SpeciesQuery.from_params(
            species_type=species_type,
            inchikey=inchikey,
            inchi=inchi,
            species=species,
            stoichiometric_formula=stoichiometric_formula,
            number_of_atoms=number_of_atoms,
        )

        return perform_species_query(
            query=query,
            maxrec=maxrec,
            media_type="text/xml",
            request_url=str(request.url),
        )

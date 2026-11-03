"""Services for the SLAP2 module.

The demo service is backed by two small CSV tables in ``fastapi_slap2/data``
(see ``scripts/build_demo_data.py``), loaded into memory at first use.
"""

import csv
import io
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from astropy.io.votable import writeto
from astropy.io.votable.tree import Field, Info, Resource, TableElement, VOTableFile

from fastapi_slap2.config.settings import get_settings
from fastapi_slap2.exceptions import ParameterError
from fastapi_slap2.responses import XMLResponse
from fastapi_slap2.schemas import (
    LINES_METADATA,
    LINES_STANDARD_ID,
    SPECIES_METADATA,
    SPECIES_STANDARD_ID,
    LinesQuery,
    SpeciesQuery,
)

DATA_DIR = Path(__file__).resolve().parent / "data"

_CASTS = {"double": float, "float": float, "int": int, "char": str}


@lru_cache
def load_table(filename: str, metadata: tuple[tuple[str, str], ...]) -> list[dict]:
    """Load a CSV table, casting columns by VOTable datatype. Empty cells become None."""
    casts = dict(metadata)
    rows = []
    with open(DATA_DIR / filename, newline="") as f:
        for raw in csv.DictReader(f):
            rows.append({k: (_CASTS[casts.get(k, "char")](v) if v != "" else None) for k, v in raw.items()})
    return rows


def _datatypes(metadata: list[dict]) -> tuple[tuple[str, str], ...]:
    return tuple((m["name"], m["datatype"]) for m in metadata)


def lines_table() -> list[dict]:
    return load_table("lines.csv", _datatypes(LINES_METADATA))


def species_table() -> list[dict]:
    return load_table("species.csv", _datatypes(SPECIES_METADATA))


def build_votable(rows: list[dict], metadata: list[dict], status: str, infos: list[tuple[str, str]]) -> bytes:
    """Serialise rows into a SLAP2 results VOTable."""
    votable = VOTableFile()
    resource = Resource(type="results")
    votable.resources.append(resource)

    resource.infos.append(Info(name="QUERY_STATUS", value=status))
    for name, value in infos:
        resource.infos.append(Info(name=name, value=value))

    table = TableElement(votable)
    resource.tables.append(table)
    for meta in metadata:
        table.fields.append(
            Field(
                votable,
                name=meta["name"],
                datatype=meta["datatype"],
                arraysize=meta.get("arraysize"),
                ucd=meta.get("ucd"),
                unit=meta.get("unit"),
            )
        )

    table.create_arrays(len(rows))
    for i, row in enumerate(rows):
        for meta in metadata:
            value = row.get(meta["name"])
            if value is None:
                table.array.mask[meta["name"]][i] = True
            else:
                table.array[meta["name"]][i] = value

    buffer = io.BytesIO()
    writeto(votable, buffer)
    return buffer.getvalue()


def data_origin_infos(request_url: str, standard_id: str) -> list[tuple[str, str]]:
    """Data origin INFO elements (SLAP2 5.2.1, table "Data provenance INFO elements")."""
    settings = get_settings()
    return [
        ("request_date", datetime.now(UTC).isoformat(timespec="seconds")),
        ("request", request_url),
        ("service_ivoid", settings.SERVICE_IVOID),
        ("service_protocol", standard_id),
        ("publisher", settings.PUBLISHER),
        ("last_update_date", settings.LAST_UPDATE_DATE),
    ]


# Query attribute -> (parameter name, column it constrains).
_LINES_FILTER_COLUMNS = {
    "wavelength": ("WAVELENGTH", "vacuum_wavelength"),
    "species": ("SPECIES", "species_name"),
    "inchikey": ("INCHIKEY", "inchikey"),
    "species_mass": ("SPECIES_MASS", "species_mass"),
    "ion_charge": ("ION_CHARGE", "ion_charge"),
    "lower_level_energy": ("LOWER_LEVEL_ENERGY", "lower_level_energy"),
    "upper_level_energy": ("UPPER_LEVEL_ENERGY", "upper_level_energy"),
    "einsteina": ("EINSTEINA", "einsteina"),
}

_SPECIES_FILTER_COLUMNS = {
    "species_type": ("SPECIES_TYPE", "species_type"),
    "inchikey": ("INCHIKEY", "inchikey"),
    "inchi": ("INCHI", "inchi"),
    "species": ("SPECIES", "species_name"),
    "stoichiometric_formula": ("STOICHIOMETRIC_FORMULA", "stoichiometric_formula"),
    "number_of_atoms": ("NUMBER_OF_ATOMS", "number_of_atoms"),
}


def _matches(constraint, value) -> bool:
    """Test one value against a constraint.

    A list is a repeated parameter (OR across its items); a plain string is an
    exact, case-sensitive match; Interval and Pattern objects match themselves.
    """
    if isinstance(constraint, list):
        return any(_matches(item, value) for item in constraint)
    if isinstance(constraint, str):  # also covers StrEnum values such as SpeciesType
        return value == constraint
    return constraint.matches(value)


def filter_rows(rows: list[dict], query, columns: dict[str, tuple[str, str]]) -> list[dict]:
    """Apply the query constraints: AND between parameters, OR within a repeated parameter."""
    for attr, (param, column) in columns.items():
        constraint = getattr(query, attr)
        if constraint is None:
            continue

        # SLAP2 5.1 / 6.1: a parameter whose column is absent or entirely NULL must raise an error.
        if all(row.get(column) is None for row in rows):
            raise ParameterError(f"Parameter {param} is not supported by this service")

        rows = [row for row in rows if _matches(constraint, row[column])]
    return rows


def perform_query(
    table: list[dict],
    query,
    columns: dict[str, tuple[str, str]],
    metadata: list[dict],
    standard_id: str,
    maxrec: int,
    media_type: str,
    request_url: str,
) -> XMLResponse:
    """Filter a table, apply MAXREC, and return the results VOTable."""
    limit = min(maxrec, get_settings().MAX_RECORDS)

    # Parameters are still validated for MAXREC=0, so an unsupported one errors either way.
    matches = filter_rows(table, query, columns)
    if maxrec == 0:
        results, status = [], "OK"
    else:
        results = matches[:limit]
        status = "OVERFLOW" if len(matches) > limit else "OK"

    content = build_votable(results, metadata, status, data_origin_infos(request_url, standard_id))
    return XMLResponse(content=content, media_type=media_type)


def perform_lines_query(query: LinesQuery, maxrec: int, media_type: str, request_url: str) -> XMLResponse:
    """Run a {lines} query and return the VOTable response."""
    return perform_query(
        lines_table(), query, _LINES_FILTER_COLUMNS, LINES_METADATA, LINES_STANDARD_ID, maxrec, media_type, request_url
    )


def perform_species_query(query: SpeciesQuery, maxrec: int, media_type: str, request_url: str) -> XMLResponse:
    """Run a {species} query and return the VOTable response."""
    return perform_query(
        species_table(),
        query,
        _SPECIES_FILTER_COLUMNS,
        SPECIES_METADATA,
        SPECIES_STANDARD_ID,
        maxrec,
        media_type,
        request_url,
    )

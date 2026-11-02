"""Schemas and protocol metadata for the SLAP2 API."""

import math
from dataclasses import dataclass
from enum import StrEnum

from fastapi_slap2.exceptions import ParameterError

LINES_STANDARD_ID = "ivo://ivoa.net/std/SLAP#lines-2.0"
SPECIES_STANDARD_ID = "ivo://ivoa.net/std/SLAP#species-2.0"


class ResponseFormat(StrEnum):
    """Supported RESPONSEFORMAT values (SLAP2 .1.10)."""

    VOTABLE = "text/xml"


# Column metadata for the {lines} resource (SLAP2 .3).
# Keys: name, datatype, and optionally arraysize, ucd, unit.
LINES_METADATA: list[dict] = [
    {"name": "vacuum_wavelength", "datatype": "double", "unit": "m", "ucd": "em.wl"},
    {"name": "vacuum_wavelength_error", "datatype": "double", "unit": "m", "ucd": "stat.error;em.wl"},
    {"name": "line_title", "datatype": "char", "arraysize": "*", "ucd": "meta.title"},
    {"name": "species_name", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "species_mass", "datatype": "float", "unit": "u", "ucd": "phys.mass"},
    {"name": "inchikey", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "inchi", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "ion_charge", "datatype": "int", "ucd": "phys.atmol.element;phys.atmol.ionization"},
    {"name": "lower_level_description", "datatype": "char", "arraysize": "*", "ucd": "meta.title;phys.atmol.level"},
    {"name": "upper_level_description", "datatype": "char", "arraysize": "*", "ucd": "meta.title;phys.atmol.level"},
    {"name": "einsteina", "datatype": "double", "unit": "s**-1", "ucd": "phys.atmol.transProb"},
    {"name": "lower_level_energy", "datatype": "double", "unit": "J", "ucd": "phys.energy;phys.atmol.level"},
    {"name": "upper_level_energy", "datatype": "double", "unit": "J", "ucd": "phys.energy;phys.atmol.level"},
    {"name": "reference_doi", "datatype": "char", "arraysize": "*", "ucd": "meta.ref.doi"},
    {"name": "reference_uri", "datatype": "char", "arraysize": "*", "ucd": "meta.ref.uri"},
]

# Column metadata for the {species} resource (SLAP2 6.3).
SPECIES_METADATA: list[dict] = [
    {"name": "species_name", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "ion_charge", "datatype": "int", "ucd": "phys.atmol.element;phys.atmol.ionization"},
    {"name": "inchikey", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "inchi", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "stoichiometric_formula", "datatype": "char", "arraysize": "*", "ucd": "phys.atmol.element"},
    {"name": "species_type", "datatype": "char", "arraysize": "*"},
    {"name": "number_of_atoms", "datatype": "int"},
]

# {lines} query parameters -> whether they may be repeated (SLAP2 Appendix, /lines endpoint parameters).
LINES_PARAMETERS: dict[str, bool] = {
    "WAVELENGTH": False,
    "SPECIES": True,
    "INCHIKEY": True,
    "SPECIES_MASS": False,
    "ION_CHARGE": False,
    "LOWER_LEVEL_ENERGY": False,
    "UPPER_LEVEL_ENERGY": False,
    "EINSTEINA": False,
    "MAXREC": False,
    "RESPONSEFORMAT": False,
}

_POS_INF = ("+Inf", "Inf")  # a bare "+" in a URL decodes to a space, so also accept "Inf"
_NEG_INF = ("-Inf",)


@dataclass(frozen=True)
class Interval:
    """A closed numeric interval as defined by DALI (``min max``, or a single value)."""

    lower: float
    upper: float

    def contains(self, value) -> bool:
        return value is not None and self.lower <= value <= self.upper

    @classmethod
    def parse(cls, param: str, raw: str, integer: bool = False) -> "Interval":
        tokens = raw.split()
        if len(tokens) not in (1, 2):
            raise ParameterError(f"{param} must be a single value or a 'min max' interval, got '{raw}'")

        bounds = [cls._parse_bound(param, token, integer) for token in tokens]
        lower, upper = bounds[0], bounds[-1]

        if len(tokens) == 1 and math.isinf(lower):
            raise ParameterError(f"{param} single value must be finite, got '{raw}'")
        if lower > upper:
            raise ParameterError(f"{param} lower bound is greater than upper bound: '{raw}'")
        return cls(lower, upper)

    @staticmethod
    def _parse_bound(param: str, token: str, integer: bool) -> float:
        if token in _POS_INF:
            return math.inf
        if token in _NEG_INF:
            return -math.inf
        try:
            value = int(token) if integer else float(token)
        except ValueError:
            kind = "an integer" if integer else "a number"
            raise ParameterError(f"{param} bound '{token}' is not {kind} or -Inf/+Inf") from None
        if not math.isfinite(value):  # rejects 'nan', 'inf', 'infinity' spellings
            raise ParameterError(f"{param} bound '{token}' is not a number or -Inf/+Inf")
        return value


@dataclass
class LinesQuery:
    """Parsed and validated {lines} query."""

    wavelength: Interval | None = None
    species: list[str] | None = None
    inchikey: list[str] | None = None
    species_mass: Interval | None = None
    ion_charge: Interval | None = None
    lower_level_energy: Interval | None = None
    upper_level_energy: Interval | None = None
    einsteina: Interval | None = None

    @classmethod
    def from_params(
        cls,
        wavelength: str | None,
        species: list[str] | None,
        inchikey: list[str] | None,
        species_mass: str | None,
        ion_charge: str | None,
        lower_level_energy: str | None,
        upper_level_energy: str | None,
        einsteina: str | None,
    ) -> "LinesQuery":
        def interval(param, raw, integer=False):
            return Interval.parse(param, raw, integer) if raw is not None else None

        return cls(
            wavelength=interval("WAVELENGTH", wavelength),
            species=species or None,
            inchikey=inchikey or None,
            species_mass=interval("SPECIES_MASS", species_mass),
            ion_charge=interval("ION_CHARGE", ion_charge, integer=True),
            lower_level_energy=interval("LOWER_LEVEL_ENERGY", lower_level_energy),
            upper_level_energy=interval("UPPER_LEVEL_ENERGY", upper_level_energy),
            einsteina=interval("EINSTEINA", einsteina),
        )

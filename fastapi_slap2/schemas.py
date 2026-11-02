"""Schemas for the SLAP2 API."""

from enum import StrEnum

from enum import StrEnum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

class SIASearchParams(BaseModel):
    """Query parameters for the SIA API."""

class ResponseFormat(StrEnum):
    """Supported response formats."""

    VOTABLE = "votable"

from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

FloatOrInf = Union[float, Literal["Inf", "-Inf"]]
IntOrInf = Union[int, Literal["Inf", "-Inf"]]

class MinMaxFloatRange(BaseModel):
    min: FloatOrInf
    max: FloatOrInf

    @classmethod
    def from_string(cls, s: str):
        tokens = s.strip().split()
        if len(tokens) != 2:
            raise ValueError(f"Expected two values, got: {s}")
        min_val = cls._parse_token(tokens[0])
        max_val = cls._parse_token(tokens[1])
        return cls(min=min_val, max=max_val)

    @staticmethod
    def _parse_token(token: str) -> FloatOrInf:
        if token in ("Inf", "-Inf"):
            return token
        try:
            return float(token)
        except ValueError:
            raise ValueError(f"Invalid float or Inf value: {token}")

class MinMaxIntRange(BaseModel):
    min: IntOrInf
    max: IntOrInf

    @classmethod
    def from_string(cls, s: str):
        tokens = s.strip().split()
        if len(tokens) != 2:
            raise ValueError(f"Expected two values, got: {s}")
        min_val = cls._parse_token(tokens[0])
        max_val = cls._parse_token(tokens[1])
        return cls(min=min_val, max=max_val)

    @staticmethod
    def _parse_token(token: str) -> IntOrInf:
        if token in ("Inf", "-Inf"):
            return token
        try:
            return int(token)
        except ValueError:
            raise ValueError(f"Invalid int or Inf value: {token}")

class LineQueryParams(BaseModel):
    """Query parameters for the Line API endpoint."""

    wavelength: Optional[MinMaxFloatRange] = Field(
        None,
        description="Wavelength range to query, in meters. Format: 'min max'.",
        example="5.1E-6 5.6E-6",
    )
    species: Optional[List[str]] = Field(
        None,
        description="Species to query for, e.g., 'H2O'.",
        example="H2O",
    )
    species_mass: Optional[MinMaxFloatRange] = Field(
        None,
        description="Mass range of the species to query for, in atomic mass units (u). Format: 'min max'.",
        example="0 12.011",
    )
    inchikey: Optional[List[str]] = Field(
        None,
        description="InChIKey of the species to query for.",
        example="XLYOFNOQVPJJNP-UHFFFAOYSA-N",
    )
    ion_charge: Optional[MinMaxIntRange] = Field(
        None,
        description="Charge state of the ion to query for, e.g., '0' for neutral, '1' for singly ionized.",
        example="1 +Inf",
    )
    lower_level_energy: Optional[MinMaxFloatRange] = Field(
        None,
        description="Energy range of the lower level to query for, in Joules. Format: 'min max'.",
        example="3.93E-18 3.94E-18",
    )
    upper_level_energy: Optional[MinMaxFloatRange] = Field(
        None,
        description="Energy range of the upper level to query for, in Joules. Format: 'min max'.",
        example="3.95E-18 3.96E-18",
    )
    einsteina: Optional[MinMaxFloatRange] = Field(
        None,
        description="Einstein A coefficient range to query for, in s^-1. Format: 'min max'.",
        example="1E-5 1E-3",
    )
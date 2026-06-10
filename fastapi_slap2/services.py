"""Services for the SLAP2 module.

Replace this stub with your actual protocol implementation.
"""

import io

from astropy.io.votable import from_table, writeto
from astropy.io.votable.tree import Info, VOTableFile
from astropy.table import Table

from fastapi_slap2.responses import XMLResponse


# Define your VOTable column metadata here.
# Each entry needs at minimum: column_name, datatype.
# Optional keys: utype, ucd, unit, arraysize.
METADATA: list[dict] = [
    # Example:
    # {
    #     "column_name": "t_start",
    #     "utype": "Char.TimeAxis.Coverage.Bounds.Limits.StartTime",
    #     "ucd": "time.start",
    #     "unit": "d",
    #     "datatype": "float",
    # },
]


def handle_response_format(results, metadata, response_format, overflow):
    """Build a response payload in the requested format."""
    if response_format == "votable":
        column_names = (
            [m["column_name"] for m in metadata if m["column_name"] in results[0]]
            if results
            else [m["column_name"] for m in metadata]
        )
        table = Table(rows=results, names=column_names)
        votable: VOTableFile = from_table(table)

        if overflow:
            votable.resources[0].infos.append(Info(name="QUERY_STATUS", value="OVERFLOW"))

        for meta in metadata:
            for field in votable.get_first_table().fields:
                if field.name == meta["column_name"]:
                    field.utype = meta.get("utype")
                    field.ucd = meta.get("ucd")
                    field.unit = meta.get("unit")
                    field.datatype = meta.get("datatype")
                    field.arraysize = meta.get("arraysize")
                    break

        buffer = io.BytesIO()
        writeto(votable, buffer)
        buffer.seek(0)
        return XMLResponse(content=buffer.read())


def perform_query(maxrec: int, response_format: str):
    """Perform the SLAP2 query.

    Replace this with your actual implementation. Populate `results` with
    dicts whose keys match the column_name values in METADATA. Set
    overflow=True when the result set was truncated at maxrec.
    """
    overflow = False
    results: list[dict] = []

    # TODO: implement query logic here

    return handle_response_format(results, METADATA, response_format, overflow)

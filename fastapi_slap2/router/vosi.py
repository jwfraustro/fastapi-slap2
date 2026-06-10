"""VOSI capabilities router for the SLAP2 service."""

from fastapi import APIRouter, Request, Response
from fastapi_restful.cbv import cbv

vosi_router = APIRouter()


@cbv(vosi_router)
class VOSIRouter:
    """Router for the VOSI capabilities endpoint."""

    @vosi_router.get("/capabilities", summary="Get the VOSI capabilities.")
    def capabilities(self, request: Request):
        """Return the VOSI capabilities document."""
        base_url = str(request.url).replace("capabilities", "")

        vosi_response = f"""<vosi:capabilities
        xmlns:vosi="http://www.ivoa.net/xml/VOSICapabilities/v1.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:vs="http://www.ivoa.net/xml/VODataService/v1.1">
        <capability standardID="ivo://ivoa.net/std/VOSI#capabilities">
                <interface xsi:type="vs:ParamHTTP" version="1.0">
                        <accessURL use="full">{base_url}capabilities</accessURL>
                </interface>
        </capability>
        <capability standardID="ivo://ivoa.net/std/SLAP2#query-1">
                <interface xsi:type="vs:ParamHTTP" role="std" version="1.0">
                        <accessURL>{base_url}query</accessURL>
                </interface>
        </capability>
</vosi:capabilities>"""

        return Response(
            content=vosi_response,
            media_type="application/xml",
            headers={"Content-Type": "application/xml"},
        )

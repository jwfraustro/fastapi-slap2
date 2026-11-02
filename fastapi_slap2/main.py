"""Main FastAPI application for SLAP2."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi_slap2.config.settings import get_settings
from fastapi_slap2.exceptions import (
    ParameterError,
    general_exception_handler,
    http_exception_handler,
    parameter_error_handler,
    validation_exception_handler,
)
from fastapi_slap2.router.slap2_router import slap2_router
from fastapi_slap2.router.vosi import vosi_router

app = FastAPI(
    title="SLAP2 API",
    description="FastAPI implementation of the IVOA SLAP2 protocol",
    root_path=get_settings().ROOT_PATH,
)


app.include_router(slap2_router, tags=["SLAP2"])
app.include_router(vosi_router, tags=["VOSI"])

app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ParameterError, parameter_error_handler)

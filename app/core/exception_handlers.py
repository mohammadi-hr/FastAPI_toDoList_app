from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette.responses import JSONResponse


def validation_exception_handler(request:Request, exc: RequestValidationError):
    exc_details = list[dict] = []

    for error in exc.errors():
        exc_details.append({
            "message": error["msg"],
            "type": error["type"],
            "fiels" : ".".join(str(loc) for loc in error["loc"]),
        })

    return JSONResponse(
        status_code=422,
        content={
            "errors": True,
            "error_code": "ValidationError",
            "message": "Request validation failed",
            "details": "Validation failed",
            "url": str(request.url),
        }
    )
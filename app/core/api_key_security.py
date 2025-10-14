from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings


API_KEY_NAME = "X-API-KEY"

"""
Default: auto_error=True
If the header is missing, FastAPI automatically raises a 401 Unauthorized error.
Your dependency function is never called; the request fails immediately.
auto_error=False:
If the header is missing, FastAPI returns None instead of raising an error.
This lets your dependency function handle the error manually.

"""
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

"""
Why Security() is better than Depends()
Integrates with OpenAPI security schemes.
Swagger UI knows this endpoint requires X-API-KEY.
Marks the dependency as security-related, which is useful for docs and compliance.
Allows multiple security dependencies with automatic precedence resolution.

"""


def get_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key

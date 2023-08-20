
from config import API_KEY

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

api_key_header = APIKeyHeader(name="X-API-Key")


async def get_api_key(_api_key_header: str = Security(api_key_header)):
    if _api_key_header == API_KEY:
        return _api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )

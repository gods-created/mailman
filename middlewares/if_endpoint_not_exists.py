from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class IfEndpointNotExists(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if response.status_code == 404:
            return JSONResponse(
                content={
                    'status': False,
                    'err_description': 'Endpoint doesn\'t exist'
                }
            )

        return response
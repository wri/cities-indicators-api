from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class StripApiPrefixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            request.scope["path"] = request.url.path[4:]
        response = await call_next(request)
        return response

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import cities, datasets, indicators, projects

# ----------------------------------------
# Logging Configuration
# ----------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Application Initialization
# ----------------------------------------

app = FastAPI(
    title="WRI Cities Indicators API",
    description="You can use this API to get the value of various indicators for a number of cities at multiple admin levels.",
    summary="An indicators API",
    version="v0",
    terms_of_service="TBD",
    contact={
        "name": "WRI Cities Data Team",
        "url": "https://citiesindicators.wri.org/",
        "email": "citiesdata@wri.org",
    },
    license_info={
        "name": "License TBD",
        "url": "https://opensource.org/licenses/",
    },
)

# ----------------------------------------
# Middleware Configuration
# ----------------------------------------


class StripApiPrefixMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            request.scope["path"] = request.url.path[4:]
        response = await call_next(request)
        return response


CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(StripApiPrefixMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
)

# ----------------------------------------
# Routes
# ----------------------------------------

app.include_router(cities.router, prefix="/cities", tags=["Cities"])
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
app.include_router(indicators.router, prefix="/indicators", tags=["Indicators"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routers import (
    cities_router,
    datasets_router,
    indicators_router,
    projects_router,
)
from app.utils.settings import Settings

# ----------------------------------------
# Load settings
# ----------------------------------------
settings = Settings()


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
    version="v1",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
)

# ----------------------------------------
# Routes
# ----------------------------------------

app.include_router(cities_router.router, prefix="/cities", tags=["Cities"])
app.include_router(datasets_router.router, prefix="/datasets", tags=["Datasets"])
app.include_router(indicators_router.router, prefix="/indicators", tags=["Indicators"])
app.include_router(projects_router.router, prefix="/projects", tags=["Projects"])


@app.get(
    "/health",
    tags=["Default"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
)
def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")

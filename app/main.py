from fastapi import FastAPI

from app.middlewares.strip_api_prefix import StripApiPrefixMiddleware
from app.routers import cities, indicators, projects

DESCRIPTION = """
You can use this API to get the value of various indicators for a number of cities at multiple admin levels.
"""

app = FastAPI(
    title="WRI Cities Indicators API",
    description=DESCRIPTION,
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

# Middlewares
app.add_middleware(StripApiPrefixMiddleware)

# Routers
app.include_router(cities.router, prefix="/cities", tags=["Cities"])
app.include_router(indicators.router, prefix="/indicators", tags=["Indicators"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Health check
@app.get(
    "/health", 
    tags=["Default"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok"
                    }
                }
            }
        }
    }
)
def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return {"status": "ok"}

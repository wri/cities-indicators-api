from fastapi import FastAPI

from app.middlewares.strip_api_prefix import StripApiPrefixMiddleware
from app.routers import cities

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


# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Routers
## Cities
app.include_router(cities.router, prefix="/cities")

# app/main.py
from fastapi import FastAPI
from app.routers import cities

app = FastAPI()

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Cities
app.include_router(cities.router, prefix="/cities")
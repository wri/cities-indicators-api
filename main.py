from fastapi import FastAPI
from pyairtable import Table

import os
airtable_api_key = os.getenv('CITIES_API_AIRTABLE_KEY')


app = FastAPI()


@app.get("/")
def read_root():
    return {"Welcome": "This is the WRI Cities Indicators API"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/cities")
def list_cities():
    table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Cities')
    cities = table.all(view="api")
    return {"cities": cities}

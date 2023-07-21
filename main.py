from fastapi import FastAPI
from fastapi.responses import RedirectResponse


app = FastAPI()

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/cities")
def list_cities():
    table = Table(airtable_api_key, 'appDWCVIQlVnLLaW2', 'Cities')
    cities = table.all(view="api")
    return {"cities": cities}

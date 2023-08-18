# cities-indicators-api
FastAPI connected to Airtable
Docs: https://citiesapi-1-x4387694.deta.app/docs

## Local dev setup
To run this locally 
1. Create an Airtable API token with the `data.records:read` scope and `Cities Indicators Metadata` Access on https://airtable.com/create/tokens/new
2. Store it as a local environment variable called `CITIES_API_AIRTABLE_KEY` in a file called `.env` 
3. Install python packages from requirement.txt
    ```
    pip install -r requirements.txt
    ```

## Run locally
`uvicorn main:app --env-file '/path/to/.env' --reload`

## Deployed
The API is deployed to https://citiesapi-1-x4387694.deta.app/
I followed this tutorial to get this working https://fastapi.tiangolo.com/deployment/deta/

If you want to deploy your own copy follow the instructions starting at https://fastapi.tiangolo.com/deployment/deta/#create-a-free-deta-space-account (You will also have to add the `CITIES_API_AIRTABLE_KEY` to the app > Settings > Configuration)
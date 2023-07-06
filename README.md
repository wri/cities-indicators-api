# cities-indicators-api
FastAPI connected to Airtable
Docs: https://citiesapi-1-x4387694.deta.app/docs

## Local
To run this locally you just need to create an Airtable API token with the `data.records:read` scope and `Cities Indicators Metadata` Access on https://airtable.com/create/tokens/new and store it as a local environment variable called `CITIES_API_AIRTABLE_KEY`.

## Deployed
The API is deployed to https://citiesapi-1-x4387694.deta.app/
I followed this tutorial to get this working https://fastapi.tiangolo.com/deployment/deta/

If you want to deploy your own copy follow the instructions starting at https://fastapi.tiangolo.com/deployment/deta/#create-a-free-deta-space-account (You will also have to add the `CITIES_API_AIRTABLE_KEY` to the app > Settings > Configuration)
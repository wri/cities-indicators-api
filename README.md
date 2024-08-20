# cities-indicators-api
FastAPI connected to Airtable & Carto

Docs: [http://44.201.179.158/docs](http://44.201.179.158/docs)

## Local Development Setup
 
1. Create an Airtable API token with the `data.records:read` scope and `Cities Indicators Metadata` access at [https://airtable.com/create/tokens/new](https://airtable.com/create/tokens/new).
2. Copy `.env.example` file to `.env` and store your Airtable API token in the `CITIES_API_AIRTABLE_KEY` environment variable.
3. Run `docker-compose up` to start the server, or if you prefer running it without Docker, use the following commands in your terminal:
    1. Install `pipenv` (if you haven't already):
        ```sh
        pip install pipenv
        ```
    2. Install the project dependencies:
        ```sh
        pipenv install
        ```
    3. Activate the virtual environment:
        ```sh
        pipenv shell
        ```
    4. Run the server:
        ```sh
        uvicorn app.main:app --reload
        ```
4. If you are on a Debian/Ubuntu system, ensure that you have Python and pip installed. You can install the `python3-pip` package using the following command:
    ```sh
    sudo apt install python3-pip
    ```
5. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to preview the API documentation.

## Deployment
The API is deployed to [https://citiesapi-1-x4387694.deta.app/](https://citiesapi-1-x4387694.deta.app/). We followed this tutorial to get it working: [FastAPI Deta Deployment](https://fastapi.tiangolo.com/deployment/deta/).

If you want to deploy your own copy, follow the instructions starting at [Create a Free Deta Space Account](https://fastapi.tiangolo.com/deployment/deta/#create-a-free-deta-space-account). You will also need to add the `CITIES_API_AIRTABLE_KEY` and `CORS_ORIGINS` environment variables to the app settings under Settings > Configuration.

## Best Practices
Adhere to our [Best Practices](/docs/best-practices.md) to ensure high-quality and consistent development.
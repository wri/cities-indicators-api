# cities-indicators-api
FastAPI connected to Airtable & Carto

Docs: [http://44.201.179.158:8000/docs](http://44.201.179.158:8000/docs)

## Local Development Setup
 
1. Create an Airtable API token with the `data.records:read` scope and `Cities Indicators Metadata` access at [https://airtable.com/create/tokens/new](https://airtable.com/create/tokens/new).
2. Copy `.env.example` file to `.env` and store your Airtable API token in the `CITIES_API_AIRTABLE_KEY` environment variable.
3. Run `docker-compose up` to start the server, or if you prefer running it without Docker, use the following commands in your terminal:
    1. Install the virtual environment:
        ```sh
        python -m venv venv
        ``` 
    2. Activate the virtual environment:
        ```sh
        source venv/bin/activate
        ```
    3. Install the Python packages:
        ```sh
        pip install -r requirements.txt
        ```
    4. Run the server:
        ```sh
        uvicorn main:app --env-file '.env' --reload
        ```
4. If you need to run pylint on your local environment:
    ```sh
    pylint $(git ls-files '*.py')
    ```
5. If you are on a Debian/Ubuntu system, install the `python3-venv` package using the following command:
    ```sh
    sudo apt install python3.10-venv
    ```
6. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to preview the API documentation.

## Deployment
The API is deployed to [https://citiesapi-1-x4387694.deta.app/](https://citiesapi-1-x4387694.deta.app/). We followed this tutorial to get it working: [FastAPI Deta Deployment](https://fastapi.tiangolo.com/deployment/deta/).

If you want to deploy your own copy, follow the instructions starting at [Create a Free Deta Space Account](https://fastapi.tiangolo.com/deployment/deta/#create-a-free-deta-space-account). You will also need to add the `CITIES_API_AIRTABLE_KEY` to the app settings under Settings > Configuration.
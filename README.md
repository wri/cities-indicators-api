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
4. If you are on a Debian/Ubuntu system, install the `python3-venv` package using the following command:
    ```sh
    sudo apt install python3.10-venv
    ```
5. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to preview the API documentation.

## Best Practices

To ensure the maintainability and quality of the codebase, please adhere to the following Python best practices:

1. **Code Formatting**:
   - Use `black` for consistent code formatting. Run `black` using:
     ```sh
     black .
     ```

2. **Linting**:
   - Use `pylint` to check for potential errors and enforce coding standards. Run `pylint` on your Python files with:
     ```sh
     pylint $(git ls-files 'app/*.py')
     ```
   - Configure `.pylintrc` as needed for project-specific settings.

3. **Type Checking**:
   - Use `mypy` for type checking to catch type-related bugs. Run it using:
     ```sh
     mypy .
     ```

4. **Testing**:
   - Write tests for your code using `pytest` to ensure your application behaves as expected. Install `pytest` and run tests with:
     ```sh
     pip install pytest
     pytest
     ```

5. **Documentation**:
   - Update the documentation to reflect changes in the codebase. Ensure that all public functions and methods are properly documented.

6. **Dependency Management**:
   - Use `pip` to manage dependencies and ensure consistency across environments. Generate a `requirements.txt` with:
     ```sh
     pip freeze > requirements.txt
     ```
   - Install dependencies when `requirements.txt` is changed:
     ```sh
    pip install -r requirements.txt
     ```

8. **Code Review**:
   - Participate in code reviews to ensure code quality and share knowledge with team members.

By following these best practices, you will help maintain a high-quality and consistent codebase. Feel free to reach out if you have any questions or need assistance.

## Deployment
The API is deployed to [https://citiesapi-1-x4387694.deta.app/](https://citiesapi-1-x4387694.deta.app/). We followed this tutorial to get it working: [FastAPI Deta Deployment](https://fastapi.tiangolo.com/deployment/deta/).

If you want to deploy your own copy, follow the instructions starting at [Create a Free Deta Space Account](https://fastapi.tiangolo.com/deployment/deta/#create-a-free-deta-space-account). You will also need to add the `CITIES_API_AIRTABLE_KEY`, `CITIES_API_AIRTABLE_BASE_ID`, `CARTO_API_KEY`, `CARTO_USERNAME`, and `CORS_ORIGINS` environment variables to the app settings under Settings > Configuration.

## Best Practices
Adhere to our [API Best Practices](/docs/best-practices.md) to ensure high-quality and consistent development.


# cities-indicators-api

FastAPI connected to Airtable & Carto

Docs: 
- [Production Environment](https://xpakp4mkpz.us-east-1.awsapprunner.com)
- [Development Environment](https://sn3rgxtgsn.us-east-1.awsapprunner.com)


## Local Development Setup

1. Create an Airtable API token with the `data.records:read` scope and `Cities Indicators Metadata` access at [https://airtable.com/create/tokens/new](https://airtable.com/create/tokens/new).
2. Copy `.env.example` file to `.env` and store your Airtable API token in the `CITIES_API_AIRTABLE_KEY` environment variable.
3. Run `docker-compose up` to start the server, or if you prefer running it without Docker, use the following commands in your terminal:
    1. Install `pipenv` (if you haven't already):

        ```sh
        pip install pipenv
        ```

    2. Activate the virtual environment:

        ```sh
        pipenv shell
        ```

    3. Install the project dependencies:

        ```sh
        pipenv install
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

The API is deployed via AWS App Runner.
- Deployments to the development environment happen when any changes to the `develop` branch occur.
- Deployments to the production environment happen when manually forcing a deployment of the `main` branch using the AWS App Runner console.

## Build Docker Image and Push to AWS ECR (ccl-develop branch)

The pipeline `Cities API Image Builder` builds the Docker image that will be used by the AWS APP Runner service `cities-api-app-runner-service-Docker` using the tag `latest`. If you want to build and push a different tag to AWS ECR, follow the steps below:

1. Setup your AWS credentials locally;

2. Login to AWS ECR;

    ```sh
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 540362055257.dkr.ecr.us-east-1.amazonaws.com
    ```
3. Build the image;

    ```sh
    docker build -t cities-indicators-api-img:<TAG>
    ```
4. Tag the image;

    ```sh
    docker tag my-image:latest 540362055257.dkr.ecr.us-east-1.amazonaws.com/cities-indicators-api-img:<TAG>
    ```
5. Push the image to ECR;

    ```sh
    docker push 540362055257.dkr.ecr.us-east-1.amazonaws.com/cities-indicators-api-img:<TAG>
    ```

## Best Practices

Adhere to our [Best Practices](/docs/best-practices.md) to ensure high-quality and consistent development.

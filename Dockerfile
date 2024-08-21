FROM python:3.10

RUN apt-get update && apt-get install -y libgdal-dev

WORKDIR /code

# Copy Pipfile and Pipfile.lock
COPY ./Pipfile ./Pipfile.lock /code/

# Install pipenv and use it to install dependencies globally
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile --system

# Copy the rest of the application code
COPY ./ /code/

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

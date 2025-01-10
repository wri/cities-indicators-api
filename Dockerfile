# Python 3.11 base image
FROM python:3.11

# Set work directory
WORKDIR /app

# Install pipenv
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./ 

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile --system

# Copy source code
COPY ./ /app/

EXPOSE 8000

# Run the application directly without the fetch_secret script
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
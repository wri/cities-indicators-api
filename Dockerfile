# Python 3.11 base image
FROM python:3.11

# Wor directory
WORKDIR /app

# Install pipenv
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile --system

# Install o boto3
RUN pipenv install boto3

# Copy source code
COPY . .

# Copy script to load the AWS secret
COPY fetch_secret.py /app/fetch_secret.py

# Exceute script
CMD ["python3", "/app/fetch_secret.py", "&&", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

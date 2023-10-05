FROM python:3.10

RUN apt-get update
RUN apt-get install -y libgdal-dev

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" "--root-path", "/api/"]

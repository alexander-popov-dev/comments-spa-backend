FROM python:3.13

RUN apt-get update -y

RUN pip install --upgrade pip

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN mkdir /app

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without local --no-interaction

COPY . /app
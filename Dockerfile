FROM python:3.11.8-bookworm

WORKDIR /app

COPY pyproject.toml /app/src/
COPY bodsgleifpipeline /app/src/bodsgleifpipeline/
COPY requirements.txt /app/src/

COPY bin /app/bin/
COPY tests /app/tests/


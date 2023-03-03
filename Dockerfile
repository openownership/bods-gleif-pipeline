FROM python:3.9.16-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bin /app/bin/
COPY tests /app/tests/

CMD ["bin/run]

FROM python:3.9.16-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bin /app/bin/
COPY tests /app/tests/
COPY run_stage.py /app/
COPY setup_indexes.py /app/

CMD ["python", "run_stage.py"]

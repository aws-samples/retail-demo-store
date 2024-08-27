FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /src

RUN apt-get update && apt-get install -y  && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
RUN python -m pip install --upgrade pip && python3 -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./

RUN mkdir data
COPY data/*.json.gz data/



ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "wsgi:app"]
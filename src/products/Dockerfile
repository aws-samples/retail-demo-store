FROM public.ecr.aws/docker/library/python:3.11-slim-bullseye

WORKDIR /src/

RUN apt-get update && apt-get install -y  && rm -rf /var/lib/apt/lists/*

COPY src/products-service/requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt


COPY src/products-service/ .

RUN mkdir dynamo-data
COPY src/products-service/data/*.yaml dynamo-data/

EXPOSE 80

ENV PYTHONUNBUFFERED=0

CMD ["python", "app.py"]

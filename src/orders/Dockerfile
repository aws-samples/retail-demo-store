FROM public.ecr.aws/docker/library/python:3.12-slim-trixie

WORKDIR /src/

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*

COPY src/orders-service/requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY src/orders-service/server.py .
COPY src/orders-service/app.py .
COPY src/orders-service/routes.py .
COPY src/orders-service/services.py .
COPY src/orders-service/handlers.py .
COPY src/orders-service/dynamo_setup.py .

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]

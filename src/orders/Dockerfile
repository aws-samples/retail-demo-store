FROM public.ecr.aws/docker/library/python:3.10-slim-bullseye

WORKDIR /src/

RUN apt-get update && apt-get install -y g++

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
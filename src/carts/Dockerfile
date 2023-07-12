FROM public.ecr.aws/docker/library/python:3.10-slim-bullseye

WORKDIR /src/
RUN apt-get update && apt-get install -y g++
COPY src/carts-service/requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY src/carts-service/server.py .
COPY src/carts-service/app.py .
COPY src/carts-service/routes.py .
COPY src/carts-service/services.py .
COPY src/carts-service/handlers.py .
COPY src/carts-service/dynamo_setup.py .

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
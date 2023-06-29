FROM public.ecr.aws/docker/library/python:3.11-slim-bullseye

WORKDIR /src/

RUN apt-get update && apt-get install -y g++

COPY src/products-service/requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY src/products-service/server.py .
COPY src/products-service/app.py .
COPY src/products-service/routes.py .
COPY src/products-service/services.py .
COPY src/products-service/aws.py .

EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]
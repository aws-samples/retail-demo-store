FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

COPY /src/location-service /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
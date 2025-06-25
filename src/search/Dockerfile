FROM public.ecr.aws/docker/library/python:3.11-slim-bookworm

COPY /src/search-service /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
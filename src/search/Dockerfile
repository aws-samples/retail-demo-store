FROM public.ecr.aws/docker/library/python:3.11-slim-trixie

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY /src/search-service /app

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]